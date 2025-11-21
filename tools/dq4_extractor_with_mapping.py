#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dragon Quest IV PSX - Text Extractor with Address Mapping v5.0
Extração de textos com mapeamento completo de endereços de origem

Baseado em dq4_extractor.py
Author: DQ4 Professional Translation Team
Version: 5.0 - Complete Huffman Integration with Address Mapping
"""

import struct
import os
import sys
import json
import csv
from collections import OrderedDict
from typing import List, Tuple, Dict, Optional

# Magic header que precede cada bloco
MAGIC_HEADER = b'\x00\x00\x08\x00\x00\x00\x08\x00'

class HuffmanDecoder:
    """Decodificador Huffman completo para DQ4"""
    
    @staticmethod
    def decode_shift_jis(sjis_code: int) -> str:
        """Decodifica código Shift-JIS para caractere"""
        try:
            return sjis_code.to_bytes(2, byteorder='big', signed=False).decode('cp932')
        except:
            return ''
    
    @staticmethod
    def parse_tree(switch: int, offset: int, cur_node: int, tree_bytes: bytes) -> any:
        """
        Parseia árvore Huffman recursivamente.
        
        Args:
            switch: 0 para esquerda, 1 para direita
            offset: Offset base para navegação
            cur_node: Nó atual
            tree_bytes: Bytes da árvore Huffman
        """
        index = cur_node * 2 + (offset if switch else 0)
        
        if index + 1 >= len(tree_bytes):
            return None
        
        h_byte = tree_bytes[index + 1]
        l_byte = tree_bytes[index]
        
        # Se é um nó interno (0x80XX)
        if (h_byte & 0xF0) == 0x80:
            node = (h_byte << 8) + l_byte - 0x8000
            # Cria novo nó com filhos
            temp = [None, None]
            temp[0] = HuffmanDecoder.parse_tree(0, offset, node, tree_bytes)
            temp[1] = HuffmanDecoder.parse_tree(1, offset, node, tree_bytes)
            return temp
        
        # Códigos de controle
        elif h_byte == 0x7F or h_byte == 0x7E:
            return "{%02x%02x}" % (h_byte, l_byte)
        
        # Fim de texto
        elif h_byte == 0 and l_byte == 0:
            return "{0000}"
        
        # Caractere Shift-JIS
        else:
            h_byte += 0x80
            enc_letter = (h_byte << 8) + l_byte
            return HuffmanDecoder.decode_shift_jis(enc_letter)
    
    @staticmethod
    def make_huff_tree(raw_huff: bytes) -> list:
        """Constrói árvore Huffman a partir dos bytes"""
        root = [None, None]
        
        # Remove últimos 2 bytes (zeros)
        raw_huff = list(raw_huff)[:-2]
        raw_length = len(raw_huff)
        
        if raw_length < 2:
            return root
        
        half = int(raw_length / 2)
        
        # Calcula nó raiz
        l_byte = raw_huff[raw_length - 2] + (raw_huff[raw_length - 1] << 8)
        root_node = 1 + l_byte - 0x8000
        
        root[0] = HuffmanDecoder.parse_tree(0, half, root_node, raw_huff)
        root[1] = HuffmanDecoder.parse_tree(1, half, root_node, raw_huff)
        
        return root
    
    @staticmethod
    def decode_huffman(offset: int, code: bytes, huff_tree: list) -> list:
        """
        Decodifica dados comprimidos usando árvore Huffman.
        
        Returns:
            Lista de dicionários com 'text' e 'offset'
        """
        d_text = ""
        dialog = []
        temp_tree = huff_tree
        byte_idx = 0
        start = offset
        start_bit = 0
        
        for byte in code:
            # Processa cada bit do byte
            for i in range(8):
                # Verifica se bit é 1 ou 0
                bit_code = 1 if (byte & (1 << i) > 0) else 0
                
                # Se é lista, continua navegando
                if isinstance(temp_tree[bit_code], list):
                    temp_tree = temp_tree[bit_code]
                else:
                    # Encontrou folha
                    d_text = ''.join([d_text, temp_tree[bit_code]])
                    
                    # Se encontrou fim de texto
                    if temp_tree[bit_code] == '{0000}':
                        bit_offset = start * 8 + start_bit
                        dialog.append({
                            'text': d_text,
                            'offset': '0x%04X' % bit_offset
                        })
                        d_text = ""
                        start = byte_idx + offset
                        start_bit = i + 1
                    
                    temp_tree = huff_tree
            
            byte_idx += 1
        
        return dialog

class DQ4ExtractorWithMapping:
    """Extrator com mapeamento completo de endereços"""
    
    # Mapa de códigos de controle para texto legível
    CONTROL_CODE_MAP = {
        '{0000}': '',  # Fim (removido)
        '{7f02}': '\n',
        '{7f04}': '',  # Itálico (ignorado)
        '{7f0a}': '',
        '{7f0b}': '',
        '{7f0c}': '',
        '{7f15}': '<GOLD>',
        '{7f1a}': 'ルーシア',
        '{7f1f}': '<HERO>',
        '{7f20}': 'ライアン',
        '{7f21}': 'アリーナ',
        '{7f22}': 'クリフト',
        '{7f23}': 'ブライ',
        '{7f24}': 'トルネコ',
        '{7f25}': 'ミネア',
        '{7f26}': 'マーニャ',
        '{7f28}': 'スコット',
        '{7f29}': 'アレクス',
        '{7f2a}': 'フレア',
        '{7f2b}': 'ホイミン',
        '{7f2c}': 'オーリン',
        '{7f2d}': 'ホフマン',
        '{7f2e}': 'パノン',
        '{7f2f}': 'ルーシア',
        '{7f31}': 'ピサロ',
        '{7f32}': 'ロザリー',
        '{7f34}': '<NAME>',
        '{7f42}': '<TOWN>'
    }
    
    def __init__(self, q41_path: str):
        self.q41_path = q41_path
        self.dialogs = OrderedDict()
        self.text_blocks_processed = 0
        self.valid_dialogs = 0
        self.decoder = HuffmanDecoder()
        self.address_map = []  # Lista para rastrear endereços
    
    def human_readable_text(self, text: str) -> str:
        """Converte códigos de controle para texto legível"""
        for code, replacement in self.CONTROL_CODE_MAP.items():
            text = text.replace(code, replacement)
        return text.strip()
    
    def parse_text_block(self, data: bytes, block_offset: int = 0, subblock_idx: int = 0) -> Optional[Dict]:
        """
        Parseia um sub-bloco de texto e extrai diálogos com endereços.
        
        Estrutura do TextBlock:
        - Header (24 bytes)
        - Huffman Code (variável)
        - E Section (10 bytes)
        - Huffman Tree (variável)
        """
        try:
            if len(data) < 24:
                return None
            
            # Lê header do TextBlock (24 bytes)
            header = struct.unpack('<IIIIII', data[:24])
            a_off = header[0]
            uuid = header[1]
            huff_c = header[2]
            huff_d = header[3]
            huff_e = header[4]
            zero = header[5]
            
            # Valida header
            if huff_c != 0x18:  # huff_c sempre é 0x18
                return None
            
            if huff_e >= len(data) or a_off >= len(data):
                return None
            
            # Extrai dados comprimidos (entre huff_c e huff_e)
            enc_data = data[huff_c:huff_e]
            
            # Lê E section (10 bytes após huff_e)
            if huff_e + 10 > len(data):
                return None
            
            e1 = struct.unpack('<I', data[huff_e:huff_e+4])[0]  # Offset da árvore
            e2 = struct.unpack('<I', data[huff_e+4:huff_e+8])[0]  # Tamanho da árvore
            e3 = struct.unpack('<H', data[huff_e+8:huff_e+10])[0]  # Número de nós
            
            # Calcula offset da árvore
            tree_start = huff_e + 10
            
            # Se huff_d é 0, usa a_off
            if huff_d == 0:
                tree_end = a_off
            else:
                tree_end = huff_d
            
            # Extrai árvore Huffman
            if tree_start >= len(data) or tree_end > len(data) or tree_start >= tree_end:
                return None
            
            enc_huff_tree = data[tree_start:tree_end]
            
            if len(enc_huff_tree) < 4:
                return None
            
            # Constrói árvore Huffman
            huff_tree = self.decoder.make_huff_tree(enc_huff_tree)
            
            if not huff_tree or (not huff_tree[0] and not huff_tree[1]):
                return None
            
            # Decodifica textos
            dec_text = self.decoder.decode_huffman(huff_c, enc_data, huff_tree)
            
            if not dec_text:
                return None
            
            # Extrai textos válidos com endereços
            texts = []
            for line in dec_text:
                text = line['text']

                # Ignora diálogos dummy ou vazios
                if "ダミー{7f0b}{0000}" in text or text == "{0000}":
                    continue

                # Converte códigos de controle
                readable_text = self.human_readable_text(text)

                if len(readable_text) > 0:
                    # Calcula endereço absoluto no arquivo
                    relative_offset = int(line.get('offset', '0x0000'), 16)
                    absolute_offset = block_offset + relative_offset
                    
                    texts.append({
                        'text': readable_text,
                        'raw_offset': line.get('offset'),
                        'relative_offset': relative_offset,
                        'absolute_offset': absolute_offset,
                    })

            if not texts:
                return None

            # Retorna dicionário com uuid e textos
            return {
                'uuid': uuid,
                'a_off': a_off,
                'huff_c': huff_c,
                'huff_d': huff_d,
                'huff_e': huff_e,
                'huff_tree_start': tree_start,
                'huff_tree_end': tree_end,
                'texts': texts,
                'block_offset': block_offset,
                'subblock_idx': subblock_idx
            }
        
        except Exception as e:
            return None
    
    def extract_all_texts(self):
        """Extrai todos os textos do arquivo com mapeamento de endereços"""
        print(f"\n[FASE 1] Parseando arquivo HBD1PS1D...")
        print(f"[*] Arquivo: {self.q41_path}")
        
        if not os.path.exists(self.q41_path):
            print(f"[!] Arquivo não encontrado!")
            return False
        
        file_size = os.path.getsize(self.q41_path)
        print(f"[*] Tamanho: {file_size:,} bytes")
        
        print(f"\n[FASE 2] Extraindo textos com decodificação Huffman completa...")
        
        with open(self.q41_path, 'rb') as f:
            blocks_found = 0
            text_blocks_found = 0
            dialog_id = 0
            
            offset = 0
            while offset < file_size:
                f.seek(offset)
                magic = f.read(8)
                
                if magic == MAGIC_HEADER:
                    block_start_offset = offset
                    # Lê header do bloco
                    header = f.read(16)
                    if len(header) < 16:
                        break
                    
                    num_sub, num_sect, total_len, zero = struct.unpack('<IIII', header)
                    
                    # Valida
                    if 1 <= num_sub <= 20 and 1 <= num_sect <= 200 and total_len > 0:
                        blocks_found += 1
                        
                        # Lê headers dos sub-blocos
                        subblock_headers = []
                        for i in range(num_sub):
                            sb_header = f.read(16)
                            if len(sb_header) < 16:
                                break
                            
                            data_len, uncomp_len, unk, comp_flag, block_type = struct.unpack('<IIIHH', sb_header)
                            subblock_headers.append((data_len, uncomp_len, unk, comp_flag, block_type))
                        
                        # Lê dados dos sub-blocos
                        subblock_idx = 0
                        for data_len, uncomp_len, unk, comp_flag, block_type in subblock_headers:
                            if data_len > 0 and data_len < 10 * 1024 * 1024:
                                # guarda offsets antes de ler os dados
                                subblock_body_offset = f.tell()
                                subblock_header_offset = subblock_body_offset - 16
                                raw_data = f.read(data_len)

                                # Processa sub-blocos de texto (tipo 40 ou 42)
                                if block_type == 40 or block_type == 42:
                                    text_blocks_found += 1

                                    parsed = self.parse_text_block(raw_data, subblock_body_offset, subblock_idx)

                                    if parsed:
                                        uuid = parsed.get('uuid')
                                        for entry in parsed.get('texts', []):
                                            dialog_id += 1
                                            dialog_id_hex = f"{dialog_id:04X}"
                                            
                                            # Armazena metadados completos para reinserção
                                            self.dialogs[dialog_id_hex] = {
                                                'text': entry.get('text'),
                                                'uuid': uuid,
                                                'block_start_offset': block_start_offset,
                                                'subblock_body_offset': subblock_body_offset,
                                                'subblock_header_offset': subblock_header_offset,
                                                'block_type': block_type,
                                                'absolute_offset': entry.get('absolute_offset'),
                                                'relative_offset': entry.get('relative_offset'),
                                                'raw_offset': entry.get('raw_offset'),
                                                'huff_tree_start': parsed.get('huff_tree_start'),
                                                'huff_tree_end': parsed.get('huff_tree_end'),
                                                'huff_c': parsed.get('huff_c'),
                                                'huff_e': parsed.get('huff_e'),
                                                'subblock_idx': subblock_idx
                                            }
                                            
                                            # Adiciona ao mapa de enderecos
                                            self.address_map.append({
                                                'dialog_id': dialog_id,
                                                'dialog_id_hex': f'0x{dialog_id_hex}',
                                                'block_start': hex(block_start_offset),
                                                'subblock_header': hex(subblock_header_offset),
                                                'subblock_body': hex(subblock_body_offset),
                                                'absolute_text_offset': hex(entry.get('absolute_offset')),
                                                'uuid': uuid,
                                                'text_preview': entry.get('text')[:100]
                                            })
                            
                            subblock_idx += 1
                        
                        # Progress
                        if blocks_found % 500 == 0:
                            progress = (offset / file_size) * 100
                            print(f"  [{blocks_found:4d} blocos] {progress:.1f}% - {len(self.dialogs)} diálogos extraídos")
                        
                        # Pula para próximo bloco
                        offset += num_sect * 2048
                    else:
                        offset += 2048
                else:
                    offset += 2048
        
        print(f"[✓] {blocks_found:,} blocos processados")
        print(f"[✓] {text_blocks_found:,} text blocks encontrados")
        print(f"[✓] {len(self.dialogs):,} diálogos únicos extraídos!")
        
        return True
    
    def export_address_mapping(self, output_dir='tools_output'):
        """Exporta CSV com mapeamento completo de endereços"""
        os.makedirs(output_dir, exist_ok=True)
        
        map_file = os.path.join(output_dir, 'dq4_address_mapping.csv')
        
        with open(map_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([
                'DIALOG_ID',
                'ID_HEX',
                'BLOCK_START_OFFSET',
                'SUBBLOCK_HEADER_OFFSET',
                'SUBBLOCK_BODY_OFFSET',
                'ABSOLUTE_TEXT_OFFSET',
                'UUID',
                'TEXT_PREVIEW'
            ])
            
            for entry in self.address_map:
                writer.writerow([
                    entry['dialog_id'],
                    entry['dialog_id_hex'],
                    entry['block_start'],
                    entry['subblock_header'],
                    entry['subblock_body'],
                    entry['absolute_text_offset'],
                    entry['uuid'],
                    entry['text_preview']
                ])
        
        print(f"[✓] Address Mapping CSV: {map_file}")
        return map_file
    
    def export_json(self, output_dir='tools_output'):
        """Exporta em JSON com endereços"""
        os.makedirs(output_dir, exist_ok=True)
        
        json_data = {
            'metadata': {
                'version': '5.0',
                'method': 'Complete Huffman Decoding with Address Mapping',
                'total_dialogs': len(self.dialogs),
                'source_file': os.path.basename(self.q41_path)
            },
            'dialogs': []
        }
        
        for text_id_hex, info in self.dialogs.items():
            json_data['dialogs'].append({
                'id': int(text_id_hex, 16),
                'id_hex': f'0x{text_id_hex}',
                'japanese_text': info.get('text'),
                'uuid': info.get('uuid'),
                'addresses': {
                    'block_start': info.get('block_start_offset'),
                    'subblock_header': info.get('subblock_header_offset'),
                    'subblock_body': info.get('subblock_body_offset'),
                    'absolute_text': info.get('absolute_offset'),
                    'huffman_tree_start': info.get('huff_tree_start'),
                    'huffman_tree_end': info.get('huff_tree_end'),
                    'huffman_code_start': info.get('huff_c'),
                    'huffman_code_end': info.get('huff_e')
                },
                'english_text': '',
                'notes': ''
            })
        
        json_file = os.path.join(output_dir, 'dq4_all_dialogs_with_addresses.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"[✓] JSON with Addresses: {json_file}")
        return json_file
    
    def export_txt(self, output_dir='logs'):
        """Exporta em TXT com endereços"""
        os.makedirs(output_dir, exist_ok=True)
        
        txt_file = os.path.join(output_dir, 'dq4_all_dialogs_with_addresses.txt')
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write('='*120 + '\n')
            f.write('DRAGON QUEST IV PSX - TODOS OS DIÁLOGOS COM ENDEREÇOS (HUFFMAN COMPLETO)\n')
            f.write('='*120 + '\n\n')
            f.write(f'Total: {len(self.dialogs)} diálogos\n')
            f.write(f'Método: Complete Huffman Decoding with Address Mapping\n')
            f.write(f'Versão: 5.0\n\n')
            f.write('='*120 + '\n\n')
            
            for text_id_hex, info in self.dialogs.items():
                text_id = int(text_id_hex, 16)
                f.write(f'[{text_id:04d}] 0x{text_id_hex}\n')
                f.write(f'UUID: {info.get("uuid")}\n')
                f.write(f'Block Start:           0x{info.get("block_start_offset"):08X}\n')
                f.write(f'Subblock Header:       0x{info.get("subblock_header_offset"):08X}\n')
                f.write(f'Subblock Body:         0x{info.get("subblock_body_offset"):08X}\n')
                f.write(f'Absolute Text Offset:  0x{info.get("absolute_offset"):08X}\n')
                f.write(f'Huffman Tree Range:    0x{info.get("huff_tree_start"):08X} - 0x{info.get("huff_tree_end"):08X}\n')
                f.write(f'Huffman Code Range:    0x{info.get("huff_c"):08X} - 0x{info.get("huff_e"):08X}\n')
                f.write('-'*120 + '\n')
                f.write(f'{info.get("text")}\n')
                f.write('\n')
        
        print(f"[✓] TXT with Addresses: {txt_file}")
        return txt_file
    
    def run(self):
        """Executa pipeline completo"""
        print('='*80)
        print('DRAGON QUEST IV PSX - TEXT EXTRACTOR WITH ADDRESS MAPPING v5.0')
        print('='*80)
        print()
        
        # Extrai textos
        if not self.extract_all_texts():
            print("[!] Falha na extracao!")
            return False
        
        if len(self.dialogs) == 0:
            print("[!] Nenhum dialogo extraido!")
            return False
        
        # Fase 3: Exportar
        print(f"\n[FASE 3] Exportando resultados com mapeamento de enderecos...")
        
        json_file = self.export_json()
        txt_file = self.export_txt()
        map_file = self.export_address_mapping()
        
        # Resumo
        print(f"\n[RESUMO FINAL]")
        print(f"  Dialogos extraidos: {len(self.dialogs)}")
        
        # Exemplos com endereços
        if self.dialogs:
            print(f"\n[PRIMEIROS 10 DIALOGOS COM ENDERECOS]")
            for idx, (text_id_hex, info) in enumerate(list(self.dialogs.items())[:10], 1):
                text = info.get('text') or ''
                preview = text[:50].replace('\n', ' ')
                if len(text) > 50:
                    preview += '...'
                abs_offset = info.get('absolute_offset')
                print(f"  {idx:2d}. [0x{text_id_hex}] @ 0x{abs_offset:08X} - {preview}")
        
        print(f"\n[OK] EXTRACAO COM MAPEAMENTO CONCLUIDA COM SUCESSO!")
        print(f"\nArquivos gerados:")
        print(f"  - {json_file}")
        print(f"  - {txt_file}")
        print(f"  - {map_file}")
        
        return True

def main():
    """Função principal"""
    # Prefer input/HBD1PS1D.Q41 in the workspace
    base_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(base_dir)
    default_q41 = os.path.join(project_root, 'input', 'HBD1PS1D.Q41')
    q41_path = default_q41

    if not os.path.exists(q41_path):
        print(f"[!] Arquivo Q41 não encontrado em '{q41_path}'")
        sys.exit(1)

    print(f"[✓] Q41: {os.path.getsize(q41_path):,} bytes")
    print()

    extractor = DQ4ExtractorWithMapping(q41_path)
    
    # Executa extração completa
    success = extractor.run()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
