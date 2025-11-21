#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '.')
from tools.dq4_huffman_injector_optimized import load_translations, load_address_map, load_rom, extract_first_huffman_tree, strategy_new_tree

translations = load_translations('translation_files/dq4_translation_para_injetar.csv')
addr_map = load_address_map('tools_output/dq4_address_mapping.csv')
rom = load_rom('input/HBD1PS1D.Q41')

# Pick first ID
print('First translation keys (sample):', list(translations.keys())[:5])
first_id = next(k for k in translations.keys() if 'ID_HEX' not in k.upper())
text = translations[first_id]
rec = addr_map[first_id]
off = rec['ABSOLUTE_TEXT_OFFSET']
header = rec['SUBBLOCK_HEADER_OFFSET']

print(f"Testing strategy_new_tree for {first_id}, off={hex(off)}, header={hex(header)}")

enc, tree_patch, success, msg = strategy_new_tree(rom, off, text, 1024, header_offset=header)
print('=> success', success, 'msg', msg)
if tree_patch:
    print('tree_patch', tree_patch)
else:
    print('no tree_patch')

# If we wrote something, show a small dump at offset
if success and enc:
    print('encoded len', len(enc))
    print('encoded head', enc[:16])
    print('dump bytes at new offset (if any):', rom[off:off+32])
