#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisa blocos Huffman no Q41 usando o mapeamento existente
Gera um CSV (`tools_output/dq4_huffman_blocks.csv`) com colunas:
ID_HEX|ABSOLUTE_TEXT_OFFSET|DATA_LEN|TREE_LEN|BLOCK_LEN|SAMPLE_TEXT

Estratégia heurística:
- Para cada offset listado em `tools_output/dq4_address_mapping.csv`, lê uma janela
  a partir do offset (por exemplo 16KB)
- Procura por possíveis finais de árvore (b'\x00\x00') dentro da janela e tenta
  interpretar os bytes seguintes/anteriores como árvore via `makeHuffTree`
- Usa `decodeHuffman` para validar se o bloco decodifica e contém o terminador `{0000}`
"""

import os
import csv
import sys
from typing import Optional

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from libs.huffman import makeHuffTree, decodeHuffman


MAPPING = os.path.join('tools_output', 'dq4_address_mapping.csv')
OUT_CSV = os.path.join('tools_output', 'dq4_huffman_blocks.csv')
Q41_PATH = os.path.join('input', 'HBD1PS1D.Q41')


def try_detect_block(qdata: bytes, offset: int, window: int = 0x4000) -> Optional[dict]:
    """Tenta detectar estrutura: [encoded_data][huffman_tree]\x00\x00
    Retorna dicionário com tamanhos e sample de texto se encontrado, caso contrário None."""

    end = min(offset + window, len(qdata))
    buf = qdata[offset:end]

    # procurar possíveis terminações de árvore (b'\x00\x00')
    candidates = [i for i in range(0, len(buf)-1) if buf[i:i+2] == b'\x00\x00']

    for c in candidates:
        tree_start = None
        # assumimos árvore ocupa bytes antes do marcador; vamos escolher um split entre
        # data and tree: tree is buf[data_len: c+2]
        tree_bytes = buf[:c+2]
        # tentaremos várias posições de início de árvore (pragmaticamente testar)
        # aqui tratamos tree_bytes como possível rawHuff
        try:
            huff = makeHuffTree(tree_bytes)
        except Exception:
            # não é uma árvore válida
            continue

        # se makeHuffTree não levantou, agora tentamos decodificar - porém decodeHuffman
        # espera (offset_bits, code_bytes, huff). No caso, o código está após a árvore,
        # mas nossa heurística original armazena dados primeiro e árvore depois. Tentar
        # ambas ordens: data+tree (conhecido no repo: encoded_data + tree)

        # Tentativa 1: data before tree (normal no injector)
        # separar: data = buf[len(tree_bytes):c+2] -> vazio aqui, então precisamos ler maiores janelas
        # Em vez disso, vamos tentar reconstruir usando aproximação: procurar por terminador {0000}
        # Testar decodificação assumindo tree_bytes é a árvore e o código está antes.
        # Assim, código = buf[:c_pos] where c_pos varies.

        # vamos testar alguns splits razoáveis: data_len from 1 to min(4096, len(buf)-len(tree_bytes))
        max_data_len = min(4096, len(buf) - (c+2))
        # também testar código longo antes da árvore: split point from 1..(c-2)
        for data_len in range(1, min(8192, c)):
            code_bytes = buf[c - data_len:c]
            try:
                dialogs = decodeHuffman(0, code_bytes, huff)
                # decodeHuffman returns list of dialogs if terminator found
                if isinstance(dialogs, list) and any('0000' in d.get('text','') or '{0000}' in d.get('text','') for d in dialogs):
                    sample = dialogs[0]['text'] if dialogs else ''
                    return {
                        'data_len': data_len,
                        'tree_len': len(tree_bytes),
                        'block_len': data_len + len(tree_bytes),
                        'sample_text': sample.replace('\n',' ').replace('\r',' ')
                    }
            except Exception:
                continue

    return None


def main():
    if not os.path.exists(MAPPING):
        print(f"[!] Mapeamento '{MAPPING}' não encontrado. Gere `tools_output/dq4_address_mapping.csv` primeiro.")
        return 1

    if not os.path.exists(Q41_PATH):
        print(f"[!] Arquivo Q41 '{Q41_PATH}' não encontrado em input/.")
        return 1

    with open(Q41_PATH, 'rb') as f:
        qdata = f.read()

    results = []

    with open(MAPPING, 'r', encoding='utf-8') as f:
        # detectar delimitador
        first = f.readline()
        delimiter = '|' if '|' in first else ','
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            dialog_id = row.get('ID_HEX') or row.get('id_hex') or row.get('DIALOG_ID') or row.get('dialog_id')
            offset_str = row.get('ABSOLUTE_TEXT_OFFSET') or row.get('absolute_text_offset') or row.get('offset')
            if not dialog_id or not offset_str:
                continue
            try:
                if isinstance(offset_str, str) and offset_str.startswith('0x'):
                    offset = int(offset_str, 16)
                else:
                    offset = int(offset_str)
            except Exception:
                continue

            info = try_detect_block(qdata, offset)
            if info:
                results.append({
                    'ID_HEX': dialog_id,
                    'ABSOLUTE_TEXT_OFFSET': hex(offset),
                    'DATA_LEN': info['data_len'],
                    'TREE_LEN': info['tree_len'],
                    'BLOCK_LEN': info['block_len'],
                    'SAMPLE_TEXT': info['sample_text']
                })
                print(f"[OK] {dialog_id} @ 0x{offset:08X} -> block {info['block_len']} bytes")
            else:
                print(f"[SKIP] {dialog_id} @ 0x{offset:08X} -> não detectado (aumente janela/heurística)")

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['ID_HEX','ABSOLUTE_TEXT_OFFSET','DATA_LEN','TREE_LEN','BLOCK_LEN','SAMPLE_TEXT'], delimiter='|')
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"[DONE] Resultado salvo em: {OUT_CSV}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
