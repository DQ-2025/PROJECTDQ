#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepara o CSV limpo para injeção, extraindo apenas ID_HEX e TRADUCAO.
"""

import csv

input_csv = 'translation_files/dq4_translation_csv_limpo.csv'
output_csv = 'translation_files/dq4_translation_para_injetar.csv'

print('[INFO] Preparando tradução para injeção...')

try:
    with open(input_csv, 'r', encoding='utf-8') as f_in:
        with open(output_csv, 'w', encoding='utf-8', newline='') as f_out:
            
            # Ler com aspas como delimitador
            reader = csv.reader(f_in, delimiter='|', quotechar='"')
            
            processed = 0
            for row in reader:
                if len(row) >= 3:
                    id_hex = row[0].strip('"').strip()
                    traducao = row[2].strip('"').strip()
                    
                    # Pular cabeçalho
                    if id_hex == 'ID_HEX':
                        continue
                    
                    # Escrever em formato simples pipe-delimited
                    f_out.write(f'{id_hex}|{traducao}\n')
                    processed += 1
            
            print(f'[INFO] {processed} linhas processadas')
            print(f'[INFO] Tradução salva em: {output_csv}')

except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()
