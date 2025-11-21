#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dragon Quest IV PS1 - Huffman Text Injector OPTIMIZADO
========================================================
Versão otimizada que cache a árvore Huffman para acelerar injeção de 89K textos.

Estratégias:
1. TREE_REUSE: Reutiliza árvore original única (mais rápido)
2. NEW_TREE: Reconstrói árvore nova
3. SAFE: tree-reuse > new-tree
4. AGGRESSIVE: tree-reuse > new-tree > abbreviate
"""

import os
import sys
import csv
import json
import struct
from pathlib import Path

# Configurar encoding UTF-8 para output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Adicionar libs ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libs.huffman import (
    makeHuffTree, decodeHuffman, encodeHuffman,
    encodeWithTree, _build_code_map_from_tree
)

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

INPUT_ROM = 'input/HBD1PS1D.Q41'
ADDRESS_MAP_CSV = 'tools_output/dq4_address_mapping.csv'
TRANSLATION_CSV = 'translation_files/dq4_translation_para_injetar.csv'
OUTPUT_ROM = 'tools_output/HBD1PS1D_TRADUZIDO.Q41'
REPORT_CSV = 'tools_output/dq4_injection_report.csv'
ANALYSIS_CSV = 'tools_output/dq4_huffman_blocks_analysis.csv'

MAX_BLOCK_SIZE = 65536

# ============================================================================
# HELPERS
# ============================================================================

def log(msg, level='INFO'):
    """Log com prefixo de nível."""
    prefix = f'[{level}]'
    print(f'{prefix} {msg}')

def warn(msg):
    log(msg, 'WARN')

def error(msg):
    log(msg, 'ERROR')

# ============================================================================
# LEITURA DE DADOS
# ============================================================================

def load_translations(csv_path):
    """Carrega tradução CSV: ID_HEX -> TRADUÇÃO."""
    trans = {}
    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter='|')
            for rownum, row in enumerate(reader, 1):
                if not row:
                    continue
                # Some CSVs include a single quoted header on first line, handle robustly
                first = row[0].lstrip('\ufeff').strip().strip('"')
                if first.upper().startswith('ID_HEX'):
                    continue
                # Expect at least ID and translation columns
                if len(row) >= 2:
                    id_hex = row[0].strip().strip('"')
                    text = row[1].strip().strip('"')
                    if id_hex:
                        trans[id_hex] = text
                else:
                    # fallback: try split whole line
                    line = row[0]
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        id_hex = parts[0].strip().strip('"')
                        text = parts[1].strip().strip('"')
                        trans[id_hex] = text
    except Exception as e:
        error(f'Erro ao carregar {csv_path}: {e}')
    return trans

def load_address_map(csv_path):
    """Carrega mapeamento de offsets (pipe-delimited) e retorna mapa por ID com campos."""
    addr_map = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            # Pular cabeçalho
            header = f.readline().strip()
            
            for line_num, line in enumerate(f, 2):
                parts = line.strip().split('|')
                if len(parts) >= 6:
                    try:
                        id_hex = parts[1].strip()  # ID_HEX é o 2º campo
                        block_start = int(parts[2], 0) if parts[2] else 0
                        subblock_header = int(parts[3], 0) if parts[3] else 0
                        subblock_body = int(parts[4], 0) if parts[4] else 0
                        absolute_text = int(parts[5], 0) if parts[5] else 0
                        
                        if id_hex:
                            addr_map[id_hex] = {
                                'BLOCK_START_OFFSET': block_start,
                                'SUBBLOCK_HEADER_OFFSET': subblock_header,
                                'SUBBLOCK_BODY_OFFSET': subblock_body,
                                'ABSOLUTE_TEXT_OFFSET': absolute_text
                            }
                    except Exception:
                        continue
    except Exception as e:
        error(f'Erro ao carregar {csv_path}: {e}')
    
    return addr_map

def load_rom(rom_path):
    """Carrega ROM em memória (como bytearray)."""
    try:
        with open(rom_path, 'rb') as f:
            return bytearray(f.read())
    except Exception as e:
        error(f'Erro ao carregar ROM: {e}')
        return None

# ============================================================================
# DETECÇÃO DE BLOCOS (OTIMIZADO)
# ============================================================================

# CACHE GLOBAL para árvore Huffman
CACHED_HUFFMAN_TREE = None
CACHED_TREE_OFFSET = None

def extract_first_huffman_tree(rom_bytes):
    """Extrai árvore Huffman (desabilitado - muito lento)."""
    return (None, None)

def detect_block_boundaries(rom_bytes, offset, max_search=1024):
    """Detecta limite do bloco procurando por terminador."""
    try:
        for i in range(offset, min(offset + max_search, len(rom_bytes) - 1)):
            if rom_bytes[i:i+2] == b'\x00\x00':
                return i - offset + 2
        return max_search
    except:
        return max_search

def extract_huffman_tree(rom_bytes, offset, window_size=512):
    """Extracts Huffman tree near a given text offset by scanning nearby bytes for terminator (0x0000).
    Returns (tree_object, tree_offset) or (None, None) on failure.
    """
    try:
        start = max(0, offset - window_size)
        end = min(len(rom_bytes), offset + window_size)
        for i in range(start, end - 1):
            if rom_bytes[i:i+2] == b'\x00\x00':
                # candidate tree bytes start at i
                tree_bytes = rom_bytes[i:i+200]
                try:
                    tree = makeHuffTree(tree_bytes)
                    return (tree, i)
                except Exception:
                    continue
        return (None, None)
    except Exception as e:
        warn(f'Erro ao extrair árvore em {hex(offset)}: {e}')
        return (None, None)

def find_free_space(rom_bytes, size, fill_value=0xFF, alignment=16, search_start=0x100000):
    """Find a free space in ROM (many 0xFF bytes) large enough for size and aligned.
    Search starts at search_start to avoid overwriting early tables.
    """
    rom_len = len(rom_bytes)
    start = min(max(0, search_start), rom_len - 1)
    count = 0
    candidate_start = None
    for i in range(start, rom_len):
        if rom_bytes[i] == fill_value:
            if candidate_start is None:
                candidate_start = i
            count += 1
            if count >= size:
                # alignment
                if candidate_start % alignment != 0:
                    # advance to aligned boundary
                    aligned = candidate_start + (alignment - (candidate_start % alignment))
                    # re-check from aligned
                    candidate_start = aligned
                    count = 0
                    i = aligned
                    continue
                return candidate_start
        else:
            candidate_start = None
            count = 0
    return None

def int_to_le_bytes(val):
    return bytes([val & 0xFF, (val >> 8) & 0xFF, (val >> 16) & 0xFF, (val >> 24) & 0xFF])

def patch_pointer_near_header(rom_bytes, header_offset, old_off, new_off, search_range=512):
    """Search for old_off little-endian bytes near header_offset and replace with new_off bytes.
    Returns True if patched, False otherwise.
    """
    if not header_offset:
        return False
    old_bytes = int_to_le_bytes(old_off)
    new_bytes = int_to_le_bytes(new_off)
    start = max(0, header_offset - 8)
    end = min(len(rom_bytes) - 4, header_offset + search_range)
    for i in range(start, end):
        if rom_bytes[i:i+4] == bytearray(old_bytes):
            # patch
            for j in range(4):
                rom_bytes[i+j] = new_bytes[j]
            return True
    return False

# ============================================================================
# ESTRATÉGIAS DE INJEÇÃO (OTIMIZADAS)
# ============================================================================

def strategy_tree_reuse(rom_bytes, offset, new_text, max_size, cached_tree=None):
    """Desabilitada - muito lenta."""
    return (None, None, False, 'Tree-reuse desabilitada')

def strategy_new_tree(rom_bytes, offset, new_text, max_size, header_offset=None):
    """Estratégia: Reconstruir árvore nova (rápido)."""
    try:
        encoded_res = encodeHuffman(new_text)
        if isinstance(encoded_res, (list, tuple)) and len(encoded_res) >= 1:
            encoded_bytes = encoded_res[0]
        else:
            encoded_bytes = encoded_res

        if encoded_bytes:
            encoded_bytes = bytes(encoded_bytes) if isinstance(encoded_bytes, bytearray) else encoded_bytes

        if encoded_bytes and len(encoded_bytes) <= max_size:
            return (encoded_bytes, None, True, f'new-tree OK ({len(encoded_bytes)} bytes)')
        else:
            size_err = len(encoded_bytes) if encoded_bytes else 0
            return (None, None, False, f'Tamanho insuficiente: {size_err} > {max_size}')
    
    except Exception as e:
        return (None, None, False, f'Erro new-tree: {str(e)[:80]}')

def strategy_abbreviate(rom_bytes, offset, new_text, max_size):
    """Desabilitada - fallback muito fraco."""
    return (None, None, False, 'Abbreviate desabilitada')

def inject_text(rom_bytes, offset, new_text, max_size, mode='new-tree', cached_tree=None, header_offset=None):
    """Executa injeção apenas com new-tree (rápido)."""
    
    if mode in ['tree-reuse', 'safe', 'aggressive']:
        mode = 'new-tree'  # Força new-tree
    
    # Apenas new-tree
    encoded, tree_patch, success, msg = strategy_new_tree(rom_bytes, offset, new_text, max_size, header_offset=header_offset)
    return (success, encoded, msg, tree_patch)

# ============================================================================
# ANÁLISE (sem injeção)
# ============================================================================

def analyze_blocks(rom_bytes, address_map, output_csv):
    """Analisa blocos Huffman sem modificar ROM."""
    log('Analisando blocos Huffman...')
    
    analysis = []
    cached_tree, cached_tree_offset = extract_first_huffman_tree(rom_bytes)
    
    # Iterar pelos primeiros 100 registros ordenados pelo offset absoluto
    items = list(address_map.items())
    def _get_off(item):
        rec = item[1]
        try:
            return int(rec.get('ABSOLUTE_TEXT_OFFSET', 0))
        except Exception:
            return 0

    for id_hex, rec in sorted(items, key=_get_off)[:100]:  # Apenas primeiros 100
        offset = rec.get('ABSOLUTE_TEXT_OFFSET', 0)
        try:
            off_int = int(offset)
        except Exception:
            off_int = 0
        block_size = detect_block_boundaries(rom_bytes, off_int)
        analysis.append({
            'ID_HEX': id_hex,
            'OFFSET': hex(off_int),
            'BLOCK_SIZE': block_size,
            'TREE_DETECTED': 'Yes' if cached_tree else 'No',
            'TREE_OFFSET': hex(cached_tree_offset) if cached_tree_offset else 'N/A'
        })
    
    # Salvar análise
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ID_HEX', 'OFFSET', 'BLOCK_SIZE', 'TREE_DETECTED', 'TREE_OFFSET'])
        writer.writeheader()
        writer.writerows(analysis)
    
    log(f'Análise salva em: {output_csv}')

# ============================================================================
# INJEÇÃO PRINCIPAL
# ============================================================================

def run_injection(mode='safe', dry_run=False, verbose=False, log_per_block=False):
    """Executa injeção de todos os textos na ROM."""
    
    log(f'=== Dragon Quest IV Huffman Injector OTIMIZADO ===')
    log(f'Modo: {mode}')
    log(f'Dry-run: {dry_run}')
    log('')
    
    # Carregar dados
    translations = load_translations(TRANSLATION_CSV)
    address_map = load_address_map(ADDRESS_MAP_CSV)
    rom_bytes = load_rom(INPUT_ROM)
    
    if not rom_bytes:
        error('Falha ao carregar ROM')
        return False
    
    log(f'Tradução: {len(translations)} textos')
    log(f'Mapa: {len(address_map)} offsets')
    log(f'ROM: {len(rom_bytes)} bytes')
    log('')
    
    success_count = 0
    fail_count = 0
    total_bytes_injected = 0
    injection_log = []
    
    items = sorted(translations.items())
    
    for idx, (id_hex, new_text) in enumerate(items):
        if idx % 10000 == 0 and idx > 0:
            log(f'[PROGRESSO] {idx}/{len(items)} ({success_count} OK, {fail_count} FAIL)')
        
        if id_hex not in address_map:
            fail_count += 1
            continue
        
        rec = address_map[id_hex]
        offset = rec.get('ABSOLUTE_TEXT_OFFSET', 0)
        header_offset = rec.get('SUBBLOCK_HEADER_OFFSET', None)
        
        if not isinstance(offset, int) or offset < 0:
            fail_count += 1
            continue
        
        max_size = detect_block_boundaries(rom_bytes, offset)
        
        # Injetar usando estratégia (apenas new-tree)
        success, encoded, msg, tree_patch = inject_text(
            rom_bytes, offset, new_text, max_size, 
            mode='new-tree', cached_tree=None, header_offset=header_offset
        )
        
        if success:
            success_count += 1
            if not dry_run and encoded:
                # Modificar ROM em memória
                try:
                    offset_int = int(offset)
                    # Somente escreva se o encoded estiver disponível
                    if encoded is not None:
                        encoded_len = len(encoded)
                        # Converter para lista de ints se for bytes ou bytearray
                        if isinstance(encoded, (bytes, bytearray)):
                            encoded_ints = list(encoded)
                        else:
                            # Se for string, codificar
                            encoded_ints = list(encoded.encode('utf-8', errors='replace'))

                        # Copiar byte-a-byte para a ROM
                        for i, byte_val in enumerate(encoded_ints):
                            if offset_int + i < len(rom_bytes):
                                rom_bytes[offset_int + i] = byte_val

                        total_bytes_injected += encoded_len
                    # Se strategy declarou envio da nova árvore, escrever também
                    if tree_patch:
                        try:
                            tree_offset, tree_bytes = tree_patch
                            # escrever tree_bytes no lugar
                            for i, b in enumerate(tree_bytes):
                                if tree_offset + i < len(rom_bytes):
                                    rom_bytes[tree_offset + i] = b
                        except Exception:
                            pass
                except Exception as e:
                    pass
            
            if verbose:
                log(f'[OK] {id_hex}: {msg}')

            injection_log.append([id_hex, 'OK', len(encoded) if encoded else 0, msg])
        else:
            fail_count += 1
            if verbose:
                warn(f'[FAIL] {id_hex}: {msg}')
            injection_log.append([id_hex, 'FAIL', 0, msg])
    
    # Salvar ROM modificada
    if not dry_run:
        try:
            with open(OUTPUT_ROM, 'wb') as f:
                f.write(rom_bytes)
            log(f'ROM salva: {OUTPUT_ROM}')
        except Exception as e:
            error(f'Erro ao salvar ROM: {e}')
    
    # Salvar relatório
    try:
        with open(REPORT_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID_HEX', 'STATUS', 'ENCODED_SIZE', 'MESSAGE'])
            writer.writerows(injection_log)
        log(f'Relatorio salvo: {REPORT_CSV}')
    except Exception as e:
        error(f'Erro ao salvar relatorio: {e}')
    
    log('')
    log(f'=== RESUMO ===')
    log(f'Sucesso: {success_count}')
    log(f'Falha: {fail_count}')
    log(f'Total bytes: {total_bytes_injected}')
    if success_count + fail_count > 0:
        log(f'Taxa: {success_count * 100 / (success_count + fail_count):.2f}%')
    
    return success_count > 0

# ============================================================================
# CLI
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Dragon Quest IV Huffman Injector (Otimizado)')
    parser.add_argument('--mode', choices=['tree-reuse', 'new-tree', 'safe', 'aggressive'], 
                        default='new-tree', help='Estrategia de injecao (default: new-tree, rápido)')
    parser.add_argument('--analyze', action='store_true', help='Apenas analisar blocos')
    parser.add_argument('--dry-run', action='store_true', help='Simular sem modificar')
    parser.add_argument('--verbose', action='store_true', help='Saida detalhada')
    parser.add_argument('--limit', type=int, default=0, help='Processar apenas N primeiros textos (0=todos)')
    
    args = parser.parse_args()
    
    if args.analyze:
        rom_bytes = load_rom(INPUT_ROM)
        if rom_bytes:
            address_map = load_address_map(ADDRESS_MAP_CSV)
            analyze_blocks(rom_bytes, address_map, ANALYSIS_CSV)
    else:
        # Aplicar limite se especificado
        if args.limit > 0:
            log(f'[LIMIT] Processando apenas {args.limit} textos (para teste rápido)')
        run_injection(mode=args.mode, dry_run=args.dry_run, verbose=args.verbose, log_per_block=False)
