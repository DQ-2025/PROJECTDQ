#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: Verifica o conteúdo do CSV de tradução carregado."""

import os

csv_path = 'translation_files/dq4_translation_para_injetar.csv'

trans = {}
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line_num <= 10:  # Primeiras 10 linhas
                parts = line.strip().split('|', 1)
                print(f"Linha {line_num}: {len(parts)} partes")
                if len(parts) == 2:
                    id_hex, text = parts
                    print(f"  ID: '{id_hex}' -> Texto: '{text[:60]}...' (len={len(text)})")
                else:
                    print(f"  Raw: {parts}")
except Exception as e:
    print(f'Erro: {e}')
