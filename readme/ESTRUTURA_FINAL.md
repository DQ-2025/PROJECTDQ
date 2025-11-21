# ESTRUTURA FINAL - FERRAMENTAS DE TRADUÇÃO
---

## 🛠️ PASSO 0: Preparação dos Arquivos

Antes de iniciar qualquer extração ou tradução, siga estes passos:

1. **Coloque o arquivo do jogo:**
   - Copie o arquivo `.bin` e o arquivo `.cue` do jogo para a pasta `input/` do projeto.
   - Exemplo:
     - `input/game.bin`
     - `input/game.cue`

2. **Extraia os arquivos principais:**
   - Execute a ferramenta `extract_bin.py` para extrair os arquivos necessários do `.bin`.
   - Comando no PowerShell:
     ```powershell
     python tools/extract_bin.py
     ```
   - Os arquivos extraídos (`SYSTEM.CNF`, `SLPM_869.16`, `HBD1PS1D.Q41`) serão salvos na pasta `input/`.

**IMPORTANTE:** Só depois de extrair esses arquivos você poderá usar as ferramentas de extração e tradução de textos.

---

## 📁 SCRIPTS PRINCIPAIS

### 1. **generate_translation_csv.py** ✅
Gera o CSV de tradução a partir dos textos extraídos
```bash
python3 generate_translation_csv.py
```
**Saída**: `translation_files/dq4_translation_csv_novo.csv` (3.33 MB, 91.548 textos)

### 2. **carregar_traducoes.py** ✅
Valida as traduções preenchidas no CSV
```bash
python3 carregar_traducoes.py
```
**Função**: Verifica quantas traduções foram preenchidas e gera relatório

### 3. **dq4_advanced_real_injector.py** ✅
Reinjecta as traduções na ROM com Huffman encoding
```bash
python3 dq4_advanced_real_injector.py
```
**Saída**: `logs/HBD1PS1D_INJETADO_v7.Q41` (ROM traduzida)

### 4. **GUIA_TRADUCAO.py** ✅
Mostra guia passo-a-passo de como usar
```bash
python3 GUIA_TRADUCAO.py
```

---

## 📚 DOCUMENTAÇÃO

- **GUIA_TRADUCAO_COMPLETO.md** - Guia passo-a-passo completo
- **CSV_TRADUCAO_README.md** - Instruções de uso do CSV
- **README.md** - Informações gerais do projeto

---

## 📂 ARQUIVOS DE DADOS

```
input/                    → Arquivo ROM original
  └── HBD1PS1D.Q41

tools_test_output/        → Textos extraídos
  └── dq4_all_dialogs_with_addresses.json (91.548 textos)

translation_files/        → Seu arquivo de tradução
  └── dq4_translation_csv_novo.csv

logs/                      → Saídas finais
  └── HBD1PS1D_INJETADO_v7.Q41 (ROM traduzida)
```

---

## 🎯 FLUXO DE TRADUÇÃO

```
1. python3 generate_translation_csv.py
   ↓ Gera: translation_files/dq4_translation_csv_novo.csv

2. Abra CSV → Preencha coluna TRADUÇÃO → Salve em UTF-8
   ↓

3. python3 carregar_traducoes.py
   ↓ Valida traduções

4. python3 dq4_advanced_real_injector.py
   ↓ Gera: logs/HBD1PS1D_INJETADO_v7.Q41

5. Teste em emulador PS1
```

---

## ✅ STATUS

- ✅ Ferramentas de verificação removidas
- ✅ Apenas scripts essenciais mantidos
- ✅ Documentação essencial mantida
- ✅ Pronto para usar

---

**Data**: 2025-11-20
**Status**: Estrutura limpa e otimizada
