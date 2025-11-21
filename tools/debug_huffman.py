#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: Testa codificação Huffman."""

import sys
sys.path.insert(0, '.')

from libs.huffman import encodeHuffman, makeHuffTree, encodeWithTree

# Teste 1: Texto simples
text1 = "The door is tightly closed..."
print(f"Teste 1: '{text1}'")
print(f"  Comprimento: {len(text1)}")

try:
    encoded = encodeHuffman(text1)
    print(f"  Encoded: {len(encoded)} bytes")
    print(f"  Tipo: {type(encoded)}")
    print(f"  Raw: {encoded[:20]}")
except Exception as e:
    print(f"  ERRO: {e}")

# Teste 2: Com árvore pré-existente
print("\nTeste 2: Extração da ROM para obter árvore")
try:
    with open('input/HBD1PS1D.Q41', 'rb') as f:
        rom = f.read()
        # Procurar árvore em 0x80e
        tree_bytes = rom[0x80e:0x80e+200]
        tree = makeHuffTree(tree_bytes)
        print(f"  Árvore criada: {tree is not None}")
        
        # Tentar codificar com árvore
        text2 = "The door is tightly closed..."
        encoded2 = encodeWithTree(tree, text2)
        print(f"  Encoded com tree: {len(encoded2)} bytes")
except Exception as e:
    print(f"  ERRO: {e}")
    import traceback
    traceback.print_exc()
