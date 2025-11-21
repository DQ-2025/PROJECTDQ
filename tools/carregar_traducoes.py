#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reinjetor de Tradução - Dragon Quest IV PS1
Carrega traduções do CSV preenchido e reinjecta na ROM
Versão simplificada para demonstração
"""

import os
import sys
import json
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_translations_from_csv(csv_file):
    """Carrega apenas as traduções preenchidas do CSV"""
    translations = {}
    total = 0
    preenchidas = 0
    
    if not os.path.exists(csv_file):
        print(f"[!] Arquivo não encontrado: {csv_file}")
        return translations, 0, 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='|')
            for row in reader:
                total += 1
                id_hex = row.get('ID_HEX', '').strip()
                traducao = row.get('TRADUÇÃO', '').strip()
                
                if id_hex and traducao:  # Apenas se tiver tradução preenchida
                    translations[id_hex] = traducao
                    preenchidas += 1
        
        return translations, total, preenchidas
    
    except Exception as e:
        print(f'[!] Erro ao ler CSV: {e}')
        import traceback
        traceback.print_exc()
        return {}, 0, 0

def main():
    print('='*100)
    print('REINJETOR DE TRADUÇÃO - DRAGON QUEST IV PS1')
    print('='*100)
    print()
    
    # CSV de tradução
    csv_file = 'translation_files/dq4_translation_csv_novo.csv'
    
    # Carrega traduções
    print(f'[*] Carregando traduções de: {csv_file}')
    translations, total, preenchidas = load_translations_from_csv(csv_file)
    
    if total == 0:
        print('[!] Erro ao carregar CSV')
        sys.exit(1)
    
    print(f'    ✓ Total de linhas: {total}')
    print(f'    ✓ Traduções preenchidas: {preenchidas}')
    print(f'    ✓ Taxa de preenchimento: {100*preenchidas/total:.1f}%')
    print()
    
    if preenchidas == 0:
        print('[!] AVISO: Nenhuma tradução foi preenchida no CSV!')
        print('[!] Preencha a coluna TRADUÇÃO (coluna C) antes de reinjetar.')
        print()
        print('Passos:')
        print('  1. Abra: translation_files/dq4_translation_csv_novo.csv')
        print('  2. Use delimitador: | (pipe)')
        print('  3. Preencha coluna TRADUÇÃO (coluna C)')
        print('  4. Salve em UTF-8')
        print('  5. Execute este script novamente')
        print()
        sys.exit(1)
    
    # Carrega dados extraídos
    print('[*] Carregando dados extraídos...')
    json_file = 'tools_output/dq4_all_dialogs_with_addresses.json'
    
    if not os.path.exists(json_file):
        print(f'[!] Arquivo não encontrado: {json_file}')
        sys.exit(1)
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        dialogs = data.get('dialogs', [])
        print(f'    ✓ {len(dialogs)} textos carregados')
    except Exception as e:
        print(f'[!] Erro ao ler JSON: {e}')
        sys.exit(1)
    
    print()
    
    # Processa
    print('[*] Analisando traduções...')
    
    traduzidos = 0
    nao_traduzidos = 0
    sample_traduzidos = []
    
    for dialog in dialogs:
        id_hex = dialog.get('id_hex', '')
        
        if id_hex in translations:
            traduzidos += 1
            if len(sample_traduzidos) < 5:
                sample_traduzidos.append({
                    'id': id_hex,
                    'ja': dialog['japanese_text'][:50],
                    'en': translations[id_hex][:50]
                })
        else:
            nao_traduzidos += 1
    
    print(f'    ✓ Textos com tradução: {traduzidos}')
    print(f'    ✓ Textos sem tradução: {nao_traduzidos}')
    print(f'    ✓ Taxa de cobertura: {100*traduzidos/(traduzidos+nao_traduzidos):.1f}%')
    print()
    
    print('[*] Amostra de traduções carregadas:')
    print('-'*100)
    for sample in sample_traduzidos:
        print(f"\n[{sample['id']}]")
        print(f"  JA: {sample['ja']}")
        print(f"  EN: {sample['en']}")
    
    print()
    print()
    
    # Gera relatório
    print('[*] Gerando relatório...')
    os.makedirs('logs', exist_ok=True)
    
    report_file = 'logs/injection_ready_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('='*100 + '\n')
        f.write('RELATÓRIO DE PREPARAÇÃO PARA INJEÇÃO\n')
        f.write('='*100 + '\n\n')
        f.write(f'Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        
        f.write('RESUMO\n')
        f.write('-'*100 + '\n')
        f.write(f'Total de textos no ROM: {len(dialogs)}\n')
        f.write(f'Traduções carregadas: {preenchidas}\n')
        f.write(f'Textos com tradução: {traduzidos}\n')
        f.write(f'Textos sem tradução: {nao_traduzidos}\n')
        f.write(f'Taxa de cobertura: {100*traduzidos/(traduzidos+nao_traduzidos):.1f}%\n\n')
        
        f.write('STATUS\n')
        f.write('-'*100 + '\n')
        if traduzidos > 0:
            f.write(f'✓ Pronto para injeção\n')
            f.write(f'✓ {traduzidos} textos serão traduzidos\n')
            f.write(f'✓ {nao_traduzidos} textos mantêm original (japonês)\n')
        else:
            f.write(f'✗ Nenhuma tradução carregada\n')
    
    print(f'    ✓ Relatório salvo: {report_file}')
    print()
    
    print('='*100)
    print('✓ RESULTADO FINAL')
    print('='*100)
    print(f'Status: PRONTO PARA INJEÇÃO')
    print(f'Traduções: {traduzidos} textos')
    print(f'Cobertura: {100*traduzidos/(traduzidos+nao_traduzidos):.1f}%')
    print()
    
    if traduzidos > 0:
        print('PRÓXIMO PASSO:')
        print('  Execute: python3 dq4_advanced_real_injector.py')
        print('  Isso gerará a ROM traduzida')
        print()
    else:
        print('⚠️  AVISO: Preencha as traduções no CSV antes de continuar')
        print()

if __name__ == '__main__':
    main()
