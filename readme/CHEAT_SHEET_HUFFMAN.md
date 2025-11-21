# CHEAT SHEET: Huffman Injection PS1 - Referência Visual
## Guia de Bolso para Implementadores

---

## 1. ESTRUTURA TEXTBLOCK (VISUAL)

```
┌─────────────────────────────────────────────────────┐
│              TextBlock Layout                       │
├─────────────────────────────────────────────────────┤
│ [0x00] Header (24B)                                 │
│        ├─ a_off: Fim do bloco (4B)                  │
│        ├─ uuid: ID de diálogo (4B)                  │
│        ├─ huff_c: 0x18 sempre (4B)                  │
│        ├─ huff_d: Início D-section (4B)            │
│        ├─ huff_e: Início árvore (4B)               │
│        └─ zero: 0x00 sempre (4B)                    │
├─────────────────────────────────────────────────────┤
│ [0x18] Huffman Code (variável)                      │
│        (Texto comprimido em Huffman)                │
├─────────────────────────────────────────────────────┤
│ [huff_e] E-Block (10B)                              │
│        ├─ e1: Offset árvore (4B)                    │
│        ├─ e2: Tamanho árvore (4B)                   │
│        └─ e3: Num nós (2B)                          │
├─────────────────────────────────────────────────────┤
│ [huff_e+10] Huffman Tree (variável)                 │
│        (Estrutura da árvore comprimida)             │
├─────────────────────────────────────────────────────┤
│ [huff_d] D-Sections                                 │
│        ├─ D Header (28B): metadados                 │
│        ├─ D1 Block: índices de diálogo              │
│        └─ D2 Block: dados adicionais                │
├─────────────────────────────────────────────────────┤
│ [a_off] Final (8B)                                  │
│        (Sempre presente, propósito desconhecido)    │
└─────────────────────────────────────────────────────┘
```

---

## 2. FLUXO DE INJEÇÃO (QUICK)

```
1. EXTRAIR
   ROM → TextBlock → decodeHuffman → CSV

2. TRADUZIR
   CSV → Preencher colunas em português

3. RECONSTRUIR
   Texto → genFreqTable → createNode → encodeHuffman
                                          ↓
                                    [Code, Tree]

4. VALIDAR TAMANHO
   Size > Available?
   ├─ NÃO → OK (próximo)
   └─ SIM → Fallback Strategy

5. REMAPEAR OFFSETS
   Old Offsets → New Offsets (offset_map)

6. ATUALIZAR SCRIPTS
   ScriptBlock.replaceOffset(old → new)
   ScriptBlock.compress()

7. ESCREVER
   ROM.NEW ← new TextBlock + new ScriptBlock

8. TESTAR
   ROM.NEW em emulador → Validar resultado
```

---

## 3. OFFSET REMAPPING EM AÇÃO

```
Original:
  Code (48B) @ 0x18 → Data @ 0x48
  
Tradução (52B):
  Code (52B) @ 0x18 → Data @ 0x4C  (+4B)
  
Cascata:
  ├─ huff_c: 0x18 (fixo, sem mudança)
  ├─ huff_e: 0x48 → 0x4C (+4B)
  ├─ Tree offset: 0x52 → 0x56 (+4B)
  ├─ huff_d: 0xD0 → 0xD4 (+4B)
  └─ a_off: 0x1C4 → 0x1C8 (+4B)

Fórmula:
  new_offset = old_offset + delta
  delta = (new_code_size - old_code_size)
```

---

## 4. FALLBACK STRATEGY DECISÃO

```
         Try Huffman
              ↓
         [Cabe?]
        /       \
      SIM      NÃO
       ↓         ↓
     ✓OK   Rebuild Tree
             ↓
         [Cabe?]
        /       \
      SIM      NÃO
       ↓         ↓
     ✓OK   Apply LZS
             ↓
         [Cabe?]
        /       \
      SIM      NÃO
       ↓         ↓
     ✓OK   Find Free Space
             ↓
         [Espaço?]
        /       \
      SIM      NÃO
       ↓         ↓
     ✓OK   Abbreviate
             ↓
         [Cabe?]
        /       \
      SIM      NÃO
       ↓         ↓
     ✓OK    ✗FAIL
```

---

## 5. CONTROLE CODES (PRESERVAR SEMPRE)

```
FUNDAMENTAL:
  {0000}  = FIM DE DIÁLOGO (OBRIGATÓRIO)
  {7f02}  = QUEBRA DE LINHA

PERSONAGENS:
  {7f1f}  = {HERO}
  {7f20}  = ライアン
  {7f21}  = アリーナ
  {7f23}  = ブライ

OUTROS:
  {7f04}  = ITÁLICO
  {7f0a}  = ?
  {7f0b}  = ?
  {7f15}  = {GOLD}

REGRA: Sempre manter {0000} ao final!
```

---

## 6. VALIDAÇÃO CHECKLIST

```
PRÉ-INJEÇÃO:
  ☐ ROM original backed up
  ☐ Texto extraído corretamente
  ☐ CSV traduzido + validado
  ☐ Controle codes preservados
  ☐ Tamanho estimado OK

DURANTE:
  ☐ Huffman comprime corretamente
  ☐ Offsets recalculados
  ☐ Scripts atualizados
  ☐ Estrutura válida

PÓS:
  ☐ Decodifica sem erro
  ☐ Número de diálogos igual
  ☐ Offsets em ordem decrescente (D1)
  ☐ Emulador rodou sem crash
  ☐ Diálogos visíveis e corretos
```

---

## 7. CÓDIGO ESSENCIAL (COPY-PASTE)

### Extrair
```python
from libs.blockDefs import TextBlock
from libs.parsing import parseHBD1, parseBlock

for b in parseHBD1('HBD1PS1D.Q41'):
    for sb in parseBlock(b):
        if sb.type in [40, 42]:
            tb = TextBlock(sb)
            tb.parse()
            for d in tb.decText:
                print(f"{d['text']}\t{d['offset']}")
```

### Codificar
```python
from libs.huffman import encodeHuffman

text = "Sua tradução aqui{7f02}Próxima linha{0000}"
[code, tree] = encodeHuffman(text)
print(f"Tamanho: {len(code)} bytes")
```

### Atualizar Script
```python
from libs.blockDefs import ScriptBlock

script.replaceOffset(
    dialog_id=0x0F,
    oldOff=0x24,
    newOff=0x28
)
```

### Validar
```python
def validate(tb):
    assert tb.huff_c == 0x18
    assert tb.huff_c < tb.huff_e < tb.huff_d < tb.a_off
    assert tb.a_off <= 2048
    print("✓ OK")
```

---

## 8. TABELA: TAMANHO TÍPICO

```
┌──────────────┬──────────┬──────────────┐
│ Componente   │ Original │ Variação     │
├──────────────┼──────────┼──────────────┤
│ Header       │ 24 B     │ Fixo         │
│ Code         │ 40-100 B │ Variável     │
│ E-Block      │ 10 B     │ Fixo         │
│ Tree         │ 200-500B │ +50% rebuild │
│ D-Section    │ 200-400B │ Fixo (tipo)  │
│ Final        │ 8 B      │ Fixo         │
├──────────────┼──────────┼──────────────┤
│ TOTAL        │ 500-1000B│ Até 2048 B   │
└──────────────┴──────────┴──────────────┘
```

---

## 9. DEBUGGING RÁPIDO

### Se Huffman não descomprime
```
1. Verificar formato da árvore:
   ├─ hByte & 0x80 == 0x80 → node
   ├─ hByte == 0x7F → control
   └─ else → character

2. Verificar parseTree recursão

3. Verificar ordem (switch 0/1)
```

### Se offsets errados
```
1. Calcular delta:
   delta = new_size - old_size

2. Todos offsets após Code sofrem +delta

3. Validar ordem: huff_c < huff_e < huff_d < a_off
```

### Se ROM crasha
```
1. Validar D1 offsets decrescentes
2. Validar offsets dentro de limites
3. Testar cada diálogo individualmente
4. Usar No$psx para debug memória
```

---

## 10. COMANDOS PYTHON ÚTEIS

```python
# Converter hex para int
offset = int('0x24', 16)  # = 36

# Converter int para hex
print(hex(36))  # = 0x24

# Bytes to int (little-endian)
val = int.from_bytes(b'\x24\x00', 'little')

# Int to bytes (little-endian)
b = (36).to_bytes(4, 'little')

# XOR (útil para validação)
checksum = 0
for byte in data:
    checksum ^= byte

# Comparar blocos
if old_data[0:24] != new_data[0:24]:
    print("Header mudou!")
```

---

## 11. FREQUÊNCIA EM JAPONÊS

```
Caracteres mais comuns em DQ4:
  な, た, に, い, を, は, れ, ろ, て
  る, と, し, き, け, だ, 人, の, 大

Códigos mais comuns:
  {0000} = FIM (extremamente comum)
  {7f02} = QUEBRA (muito comum)
  {7fXX} = CONTROLE

Dica: Texto com muitos {0000} comprime bem!
```

---

## 12. ARQUIVO ESPERADO: CSV

```
Formato:
  [número] | [original] | [tradução]

Exemplo:
  1 | {7f20}ライアン{0000} | {7f20}Rayan{0000}
  2 | アリーナは戦士です{0000} | Alena é guerreira{0000}
  3 | シンシア{7f21}は... | Synthesia{7f21} é...

IMPORTANTE:
  • Preservar {codes}
  • Sempre terminar com {0000}
  • Uma linha por diálogo
  • UTF-8 encoding
```

---

## 13. ESTRUTURA D-BLOCK (Simplificado)

```
D Header (28B):
  [0] = 0x01 (sempre)
  [4] = d1_off
  [8] = d2_off
  [12] = d_entries (count)
  [14-23] = vars[0-4]

D1 Block (por entrada):
  [0:4] = offset    (4B) ← EM ORDEM DECRESCENTE!
  [4:6] = value     (2B) ← Shift-JIS char
  [6:7] = flag1     (1B) ← ?
  [7:8] = flag2     (1B) ← ?

Validação CRÍTICA:
  offsets[i-1] > offsets[i]  (DEVE!)
```

---

## 14. ERROS COMUNS E SOLUÇÕES

```
┌──────────────────┬──────────────────────────────┐
│ Erro             │ Solução                      │
├──────────────────┼──────────────────────────────┤
│ Offset mismatch  │ Recalcular delta e aplicar   │
│ Crashed  emulador│ Validar D1 order             │
│ Texto truncado   │ {0000} missing ao final?     │
│ Tree não parse   │ Verificar hByte flags        │
│ Tamanho grande   │ Usar abbreviate()            │
│ Script não acha  │ replaceOffset() falhou?      │
│ Hieróglifos      │ Shift-JIS encoding errado    │
└──────────────────┴──────────────────────────────┘
```

---

## 15. RESUMO DE FÓRMULAS

```
Code Size = huff_e - huff_c (sempre em múltiplo de 4)
Tree Size = huff_d - huff_e - 10
D Size    = a_off - huff_d
Total     = 24 + code_size + 10 + tree_size + d_size

Block Size DEVE ser ≤ 2048 bytes!

Compression Ratio = 100 - (compressed_size / original_size * 100)
Typical = 40-60% compression
```

---

## 16. REFERÊNCIA RÁPIDA ESTRUTURA

```
TEXTBLOCK SIZE CALCULATION:
┌──────────────────────────────────┐
│ header(24)                       │ Fixed
│ + code(var)                      │ Variável!
│ + eblock(10)                     │ Fixed
│ + tree(var)                      │ Recalc
│ + dheader(28)                    │ Fixed
│ + d1(var) + d2(var)              │ Preservado
│ + final(8)                       │ Fixed
└──────────────────────────────────┘
         ↓
   Total ≤ 2048 B
```

---

## 🎯 TL;DR (2 minutos)

1. **Extrair:** Use dq4psxtrans `extractText.py`
2. **Traduzir:** Preencha CSV mantendo {codes}
3. **Comprimir:** `encodeHuffman()` cria code + tree
4. **Validar:** Tamanho <= espaço? Senão fallback
5. **Remapear:** Offsets antigos → novos
6. **Scripts:** Atualizar com novos offsets
7. **Escrever:** Nova ROM com blocos modificados
8. **Testar:** Em emulador para validar

---

**Cheat Sheet Completo - Salve para referência rápida!**

Última atualização: Novembro 21, 2025
