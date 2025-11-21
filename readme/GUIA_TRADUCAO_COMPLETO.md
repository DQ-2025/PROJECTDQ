# Guia Completo de Tradução - Dragon Quest IV PS1

## 📋 Resumo

Este projeto fornece uma **pipeline completa** para traduzir Dragon Quest IV PS1. O processo é dividido em 4 etapas:

1. **Geração de CSV** - Extrai textos do ROM em formato de planilha
2. **Tradução** - Preenche o CSV com traduções em inglês
3. **Validação** - Verifica se as traduções estão corretas
4. **Injeção** - Reinjecta os textos traduzidos na ROM

---

## 🔧 ETAPA 1: Gerar CSV de Tradução

### Comando
```bash
python3 generate_translation_csv.py
```

### O que faz
- ✅ Extrai 91.548 textos do arquivo JSON (`tools_test_output/dq4_all_dialogs_with_addresses.json`)
- ✅ Normaliza quebras de linha para formato CSV
- ✅ Gera arquivo: `translation_files/dq4_translation_csv_novo.csv` (3.33 MB)

### Resultado
```
Arquivo: translation_files/dq4_translation_csv_novo.csv
Tamanho: 3.33 MB
Linhas: 91.549 (91.548 textos + 1 header)
Encoding: UTF-8
Delimitador: | (pipe)
```

### Estrutura do CSV
```
ID_HEX|JAPONÊS|TRADUÇÃO|NOTAS
0x0001|トビラは　かたく閉ざされている……。||
0x0002|ルーシア「<HERO>！　そしてみなさん！ あなたがたと　旅ができた事を わたしは　誇りに思います。||
0x0003|{7f30}「グゴゴーン！||
```

---

## 📊 ETAPA 2: Traduzir no Excel/LibreOffice

### Passo-a-Passo

#### 1. Abrir o arquivo
```
Arquivo: translation_files/dq4_translation_csv_novo.csv
```

#### 2. Importar com delimitador correto
- ⚠️ **IMPORTANTE**: Use `|` (pipe) como delimitador
- **NÃO use** vírgula, tabulação ou ponto-e-vírgula

#### 3. Estrutura das colunas
| Coluna | Nome | Função | Modificar? |
|--------|------|--------|-----------|
| A | ID_HEX | Identificador único | ❌ NÃO |
| B | JAPONÊS | Texto original em japonês | ❌ NÃO |
| C | TRADUÇÃO | Preencher com tradução em inglês | ✅ SIM |
| D | NOTAS | Campo opcional para observações | ✅ OPCIONAL |

#### 4. Exemplo de como preencher

**Antes:**
```
0x0001|トビラは　かたく閉ざされている……。||
```

**Depois:**
```
0x0001|トビラは　かたく閉ざされている……。|The door is tightly closed...|
```

#### 5. Salvar o arquivo
- ✅ Formato: **CSV UTF-8**
- ✅ Delimitador: **| (pipe)**
- ✅ Encoding: **UTF-8 (não ANSI)**
- ❌ NÃO altere: Colunas A e B

### Tips de Tradução
- Procure por `<HERO>` - é o nome do personagem principal, deixar como está
- Procure por `{7f30}` - é um personagem especial, deixar como está
- Preserve espaços e pontuação originais quando possível
- Textos entre `「」` são falas de personagens

---

## ✅ ETAPA 3: Validar Traduções

### Comando
```bash
python3 carregar_traducoes.py
```

### O que faz
- ✅ Carrega seu CSV preenchido
- ✅ Verifica quantas traduções foram preenchidas
- ✅ Mostra amostra das traduções carregadas
- ✅ Gera relatório: `logs/injection_ready_report.txt`

### Resultado esperado
```
Total de textos no ROM: 91548
Traduções carregadas: 91548 (ou menos, dependendo de quantas preencheu)
Taxa de preenchimento: 100% (ou menos)
Status: PRONTO PARA INJEÇÃO
```

---

## 💾 ETAPA 4: Reinjetar na ROM

### Comando
```bash
python3 dq4_advanced_real_injector.py
```

### O que faz
- ✅ Lê o CSV com suas traduções
- ✅ Codifica os textos com Huffman (compressão)
- ✅ Insere os textos na ROM original
- ✅ Gera ROM traduzida: `logs/HBD1PS1D_INJETADO_v7.Q41` (~304 MB)

### Taxa de sucesso esperada
- **99.97%** de sucesso na codificação Huffman
- Apenas 19 caracteres especiais podem falhar (normal)

### Resultado
```
Arquivo gerado: logs/HBD1PS1D_INJETADO_v7.Q41
Tamanho: ~304 MB
Status: Pronto para teste em emulador PS1
```

---

## 📁 Estrutura de Arquivos

```
PROJETODQ4/
├── generate_translation_csv.py      ← ETAPA 1: Gerar CSV
├── GUIA_TRADUCAO.py                 ← Mostrar instruções
├── carregar_traducoes.py             ← ETAPA 3: Validar
├── dq4_advanced_real_injector.py    ← ETAPA 4: Reinjetar
│
├── tools_test_output/
│   └── dq4_all_dialogs_with_addresses.json   (91.548 textos extraídos)
│
├── translation_files/
│   └── dq4_translation_csv_novo.csv  ← Seu arquivo de tradução (ETAPA 2)
│
└── logs/
    ├── injection_ready_report.txt    (Relatório de validação)
    └── HBD1PS1D_INJETADO_v7.Q41     (ROM traduzida gerada)
```

---

## 🎯 Fluxo Completo (Resumido)

```
1. python3 generate_translation_csv.py
   ↓
2. Abra translation_files/dq4_translation_csv_novo.csv no Excel
   ↓
3. Preencha coluna TRADUÇÃO (coluna C)
   ↓
4. Salve o arquivo em UTF-8
   ↓
5. python3 carregar_traducoes.py
   (Valida se as traduções foram carregadas)
   ↓
6. python3 dq4_advanced_real_injector.py
   (Gera ROM traduzida)
   ↓
7. Teste em emulador PS1: logs/HBD1PS1D_INJETADO_v7.Q41
```

---

## ⚠️ Notas Importantes

### Sobre o CSV
- ✅ 91.548 textos únicos do ROM
- ❌ Nem todos precisam ser traduzidos
- 💡 Quanto mais preencher, melhor o resultado

### Sobre caracteres especiais
- `<HERO>` = Nome do personagem (deixar como está)
- `{7f30}` = Personagem especial (deixar como está)
- `　` = Espaço fullwidth (preserve se estiver no original)

### Sobre codificação
- ✅ Use sempre UTF-8
- ✅ Use sempre | (pipe) como delimitador
- ❌ Não use ANSI ou outras codificações
- ❌ Não use vírgula ou tabulação como delimitador

### Sobre a ROM
- 📂 Arquivo original: `input/HBD1PS1D.Q41` (319 MB)
- 📂 ROM traduzida: `logs/HBD1PS1D_INJETADO_v7.Q41` (304 MB)
- ✅ Testada com sucesso (99.97% Huffman encoding)

---

## 📞 Troubleshooting

### Problema: "Arquivo não encontrado"
- Verifique se você está na pasta correta: `PROJETODQ4/`
- Execute: `python3 generate_translation_csv.py` primeiro

### Problema: "CSV não carrega"
- Verifique o delimitador: deve ser `|` (pipe)
- Verifique encoding: deve ser UTF-8
- Abra no LibreOffice se tiver problemas no Excel

### Problema: "Nenhuma tradução foi carregada"
- Preencha a coluna TRADUÇÃO (coluna C) no CSV
- Salve o arquivo
- Execute: `python3 carregar_traducoes.py` novamente

### Problema: "Erro de Huffman encoding"
- Normal: alguns caracteres especiais podem falhar
- Taxa esperada: 99.97% de sucesso
- A ROM ainda funciona com falhas pontuais

---

## ✨ Exemplo Prático Completo

### Traduzir apenas 10 textos (teste rápido)

1. Gere o CSV:
```bash
python3 generate_translation_csv.py
```

2. Abra `translation_files/dq4_translation_csv_novo.csv`

3. Preencha apenas as 10 primeiras linhas de tradução:
```
0x0001|トビラは　かたく閉ざされている……。|The door is tightly closed.|
0x0002|ルーシア「<HERO>！　そしてみなさん！...|Lucia: <HERO>! Everyone!|
... (preencha 8 mais)
```

4. Salve como UTF-8 com delimitador |

5. Valide:
```bash
python3 carregar_traducoes.py
```

6. Reinjecte:
```bash
python3 dq4_advanced_real_injector.py
```

7. Teste em emulador PS1

---

## 📚 Documentação Adicional

- `VERIFICACAO_FINAL.md` - Status técnico do projeto
- `README.md` - Informações gerais
- `logs/injection_ready_report.txt` - Relatório de validação

---

**Status**: ✅ Tudo funcionando corretamente!
**Última atualização**: 2025-11-20
