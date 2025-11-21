#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de CSV de Tradução - Dragon Quest IV PS1
Extrai textos japoneses do JSON extraído e gera CSV para tradução
"""

import os
import sys
import json
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_extracted_texts():
    """Carrega textos extraídos do JSON"""
    json_file = 'tools_output/dq4_all_dialogs_with_addresses.json'
    
    if not os.path.exists(json_file):
        print(f"[!] Erro: Arquivo não encontrado: {json_file}")
        return []
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'dialogs' in data:
            return data['dialogs']
        else:
            print(f"[!] Erro: Chave 'dialogs' não encontrada no JSON")
            return []
    
    except Exception as e:
        print(f"[!] Erro ao ler JSON: {e}")
        import traceback
        traceback.print_exc()
        return []

def normalize_text_for_csv(text):
    """Normaliza texto para CSV:
    - Substitui quebras de linha por espaço único
    - Preserva espaços especiais (fullwidth space)
    """
    # Remove quebras de linha
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Remove espaços múltiplos (mas preserva fullwidth space \u3000)
    import re
    text = re.sub(r'  +', ' ', text)  # Remove espaços ASCII múltiplos
    return text.strip()

def generate_csv(output_file='translation_files/dq4_translation_template.csv'):
    """Gera CSV de tradução a partir dos textos extraídos"""
    
    print('='*100)
    print('GERADOR DE CSV DE TRADUÇÃO - Dragon Quest IV PS1')
    print('='*100)
    print()
    
    # Carrega textos
    print('[*] Carregando textos extraídos...')
    dialogs = load_extracted_texts()
    
    if not dialogs:
        print('[!] Nenhum texto foi carregado!')
        return False
    
    print(f'    ✓ {len(dialogs)} textos carregados')
    print()
    
    # Cria diretório se não existir
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f'[+] Diretório criado: {output_dir}')
    
    # Gera CSV
    print('[*] Gerando CSV de tradução...')
    
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            # Header
            f.write('ID_HEX|JAPONÊS|TRADUÇÃO|NOTAS\n')
            
            # Dados
            for i, dialog in enumerate(dialogs, 1):
                id_hex = dialog.get('id_hex', f'0x{i:04X}')
                japanese_text = dialog.get('japanese_text', '')
                
                # Normaliza para CSV
                japanese_normalized = normalize_text_for_csv(japanese_text)
                
                # Escapar pipes dentro do texto (substituir por espaço ou remover)
                japanese_normalized = japanese_normalized.replace('|', ' ')
                
                # Linha CSV: ID|TEXTO_JA|TRADUÇÃO_VAZIA|NOTAS_VAZIAS
                line = f'{id_hex}|{japanese_normalized}||\n'
                f.write(line)
                
                # Progress
                if i % 10000 == 0:
                    print(f'    Processados: {i}/{len(dialogs)} textos...')
        
        print(f'    ✓ CSV gerado com sucesso')
        print()
        
        # Estatísticas
        print('='*100)
        print('ESTATÍSTICAS')
        print('='*100)
        print(f'Arquivo: {output_file}')
        print(f'Total de linhas: {len(dialogs)} + 1 (header)')
        print(f'Tamanho: {os.path.getsize(output_file) / (1024*1024):.2f} MB')
        print(f'Encoding: UTF-8')
        print(f'Delimiter: | (pipe)')
        print()
        print('[✓] CSV pronto para tradução!')
        print()
        print('INSTRUÇÕES DE USO:')
        print('  1. Abra o arquivo no Excel/LibreOffice com delimiter: | (pipe)')
        print('  2. Coluna A: ID_HEX (não modificar)')
        print('  3. Coluna B: JAPONÊS (não modificar)')
        print('  4. Coluna C: TRADUÇÃO (preencher com tradução em inglês)')
        print('  5. Coluna D: NOTAS (opcional)')
        print('  6. Salve como CSV UTF-8 com delimiter: | (pipe)')
        print()
        
        return True
    
    except Exception as e:
        print(f'[!] Erro ao gerar CSV: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    output_file = 'translation_files/dq4_translation_csv.csv'
    
    success = generate_csv(output_file)
    
    if success:
        print(f'[OK] Arquivo salvo: {output_file}')
    else:
        print('[ERRO] Falha ao gerar CSV')
        sys.exit(1)

if __name__ == '__main__':
    main()
