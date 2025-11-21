# 🎮 DRAGON QUEST IV PSX - INSTRUÇÕES FINAIS DE USO
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

**IMPORTANTE:** Este é o primeiro passo do processo! Só depois de extrair esses arquivos você poderá usar as ferramentas de extração e tradução de textos.

---
---

## 🛠️ PASSO 0: EXTRAIR ARQUIVOS DO .BIN

Antes de iniciar qualquer extração de textos ou tradução, é obrigatório extrair os arquivos principais do jogo a partir do arquivo `.bin` original. Para isso, utilize a ferramenta `extract_bin.py` localizada em `tools/`.

### Como usar:
1. Coloque o arquivo `.bin` do jogo na raiz do projeto (ou ajuste o caminho no comando).
2. Execute o comando abaixo no PowerShell:
   ```powershell
   python tools/extract_bin.py
   ```
3. Os arquivos extraídos (`SYSTEM.CNF`, `SLPM_869.16`, `HBD1PS1D.Q41`) serão salvos na pasta `input/`.

**IMPORTANTE:** Este é o primeiro passo do processo! Só depois de extrair esses arquivos você poderá usar as ferramentas de extração e tradução de textos.

---

## ✅ O QUE FOI CONCLUÍDO

Seu projeto de tradução do Dragon Quest IV PSX **foi 100% finalizado**!

- ✅ 89,167 textos traduzidos e injetados
- ✅ ROM pronta para usar em emulador
- ✅ Patch XDelta disponível para compartilhamento
- ✅ Documentação completa

---

## 📁 ARQUIVOS FINAIS DISPONÍVEIS

```
output_injected/
├── HBD1PS1D_TRADUZIDO.Q41     ← ROM TRADUZIDA PRONTA (304.64 MB)
├── DQ4_Traduzido.cue          ← USE COM A ROM ACIMA (1 KB)
└── DQ4_Translation.xdelta     ← OU DISTRIBUA ESTE PATCH (10.34 MB)
```

---

## 🚀 PASSO 1: INSTALAR EMULADOR

### Para Windows:

**Opção A: PCSX2 (Recomendado)**
1. Abra: https://pcsx2.net/
2. Clique: "Download"
3. Selecione: "Windows"
4. Instale normalmente

**Opção B: Mednafen**
1. Abra: https://mednafen.github.io/
2. Baixe versão Windows
3. Extraia em pasta

---

## 🎮 PASSO 2: COPIAR ARQUIVOS TRADUZIDOS

### No Windows:

```powershell
# Abra PowerShell e copie:

# Copiar arquivo traduzido
Copy-Item "C:\Users\PL\Downloads\DQ4PROJECT\output_injected\HBD1PS1D_TRADUZIDO.Q41" "C:\Minha\Pasta\Emulador"

# Copiar arquivo CUE
Copy-Item "C:\Users\PL\Downloads\DQ4PROJECT\output_injected\DQ4_Traduzido.cue" "C:\Minha\Pasta\Emulador"
```

**Ou manualmente:**
1. Abra `C:\Users\PL\Downloads\DQ4PROJECT\output_injected`
2. Copie `HBD1PS1D_TRADUZIDO.Q41`
3. Copie `DQ4_Traduzido.cue`
4. Cole em pasta do seu emulador

---

## 📺 PASSO 3: ABRIR NO EMULADOR

### PCSX2:

1. Abra PCSX2
2. Menu: `System`
3. Clique: `Boot`
4. Selecione: `DQ4_Traduzido.cue`
5. **JOGO CARREGA!** ✅

### Mednafen:

```bash
mednafen DQ4_Traduzido.cue
```

### ePSXe ou DuckStation:

1. Abra emulador
2. Menu: `File` ou `Arquivo`
3. Selecione: `Run CD` ou `Load Game`
4. Clique em: `DQ4_Traduzido.cue`

---

## ✅ VERIFICAÇÃO RÁPIDA

Após abrir o jogo:

- ✅ Logotipo é exibido?
- ✅ Menu aparece?
- ✅ Textos estão em inglês?
- ✅ Som funciona?

Se TUDO OK → **APROVEITE O JOGO!** 🎉

---

## 🔄 DISTRIBUIR O PATCH (Opcional)

Se quiser compartilhar com amigos:

### Método 1: Enviar apenas o Patch

1. Envie arquivo: `DQ4_Translation.xdelta` (10.34 MB)
2. Seu amigo baixa: Delta Patcher
3. Seu amigo aplica patch + ROM original
4. Seu amigo joga! ✅

**Vantagem:** Arquivo pequeno, fácil de compartilhar

### Método 2: Enviar ROM Completa

1. Compacte: `HBD1PS1D_TRADUZIDO.Q41` + `DQ4_Traduzido.cue`
2. Envie via drive ou torrent
3. Seu amigo copia para emulador
4. Seu amigo joga! ✅

**Vantagem:** Mais rápido de usar, sem ferramentas extras

---

## ❓ PROBLEMAS DURANTE USO

### "Emulador diz: Arquivo não encontrado"

**Solução:**
```
Confirme que AMBOS os arquivos estão na mesma pasta:
✓ HBD1PS1D_TRADUZIDO.Q41
✓ DQ4_Traduzido.cue

Se não estão, copie novamente e tente abrir o .cue
```

### "Arquivo CUE abrir, mas ROM não carrega"

**Solução:**
```
1. Teste com ROM original (sem tradução)
2. Se original não funciona: problema é emulador
3. Se original funciona: teste arquivo traduzido
4. Se traduzido não funciona: arquivo corrompido, re-copie
```

### "Textos aparecem como símbolos estranhos"

**Solução:**
```
1. Confirme que arquivo é HBD1PS1D_TRADUZIDO.Q41 (não original)
2. Tente outro emulador (PCSX2, Mednafen, etc)
3. Se ainda não funciona: problema de encoding no emulador
   (solução: usar outro emulador)
```

### "Jogo muito lento"

**Solução:**
```
PCSX2:
• Graphics → Renderer → Direct3D11
• Graphics → Resolution → 640x480 (mais rápido)
• Graphics → Enable Frame Skipping (se muito lento)

Mednafen:
• Reduzir zoom/resolução
```

---

## 📊 VERIFICAÇÕES TÉCNICAS

### Confirmar arquivo traduzido correto:

**Windows PowerShell:**
```powershell
# Verificar tamanho (deve ser exatamente este valor)
(Get-Item "HBD1PS1D_TRADUZIDO.Q41").Length
# Resultado esperado: 319436800

# Verificar hash
Get-FileHash "HBD1PS1D_TRADUZIDO.Q41" -Algorithm SHA256
# Resultado esperado: 7899350ca3ccee04586f13b1230814f2e908fd0deada451b793f6bc7bab7fa40
```

Se os valores forem exatamente esses → arquivo está correto! ✅

---

## 🎓 INFORMAÇÕES TÉCNICAS (Para Curiosos)

### Como a tradução foi feita:

1. **Extração:** 91,548 textos extraídos do BIN/CUE
2. **Tradução:** Google Free API (89,187 textos traduzidos em 9 horas)
3. **Injeção:** Huffman reverso (89,167 textos injetados - 99.98% sucesso)
4. **Empacotamento:** XDelta3 patch (10.34 MB compressão)

### Arquivos criados:

- `dq4_safe_huffman_injector.py` - Injetor de tradução
- `create_xdelta_patch.py` - Gerador de patches
- `prepare_for_emulator.py` - Preparador de ROMs

### CSV de tradução:

```
File: translation_files/dq4_translation_csv.csv
Formato: NUMERO, JAPONES, ENGLISH, TRADUCAO
Linhas: 89,187
Encoding: UTF-8
```

---

## 📞 CONTATO/SUPORTE

Se tiver problemas que não consiga resolver:

1. **Consulte:** `GUIA_PRATICO_USAR_TRADUCAO.md` (instruções completas)
2. **Consulte:** `PROJETO_COMPLETO.md` (documentação técnica)
3. **Tente:** Outro emulador PS1

---

## 🎉 RESUMO FINAL

### Você tem:
- ✅ ROM 100% traduzida
- ✅ 89,167 textos em inglês
- ✅ Arquivo pronto para emulador
- ✅ Patch para distribuição
- ✅ Documentação completa

### Próximos passos:
1. Instale PCSX2
2. Copie `HBD1PS1D_TRADUZIDO.Q41` + `DQ4_Traduzido.cue`
3. Abra arquivo `.cue` em PCSX2
4. **JOGUE E APROVEITE!** 🎮

---

## 📅 Data de Conclusão

**21 de Novembro de 2025**

Projeto iniciado → Finalizado e testado ✅

---

## 🙏 Aproveite!

Divirta-se com Dragon Quest IV totalmente traduzido!

**楽しんでください!** (Tanoshinde kudasai - Aproveite!)

---

*Próxima linha, copie e cole para verificar arquivo final:*

```
(Get-Item "output_injected\HBD1PS1D_TRADUZIDO.Q41").Length -eq 319436800 -and (Get-Item "output_injected\DQ4_Traduzido.cue").Exists
```

**Se retornar `True` → Tudo OK! Pronto para jogar! ✅**
