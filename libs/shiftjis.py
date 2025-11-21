import codecs

ShiftJISLookup = {}

asciiMap = {
  ' ':0x8140,
  '{':0x816f,
  '}':0x8170,
  '.':0x8142,
  ',':0x8141,
  '\'':0x8166,
  '?':0x8148,
  '!':0x8149
}

def mapASCII( char ):
  # Uppercase Letters
  if( ord(char) >= 0x41 and ord(char) <= 0x5A ):
    char = ord(char) + 0x60 - 0x41 + 0x8200
    return char
  # Lowercase Letters
  elif( ord(char) >= 0x61 and ord(char) <= 0x7A ):
    char = ord(char) + 0x81 - 0x61 + 0x8200
    return char
  # Decimals
  elif( ord(char) >= 0x30 and ord(char) <= 0x39 ):
    char = ord(char) + 0x4f - 0x30 + 0x8200
    return char
  # Map
  elif char in asciiMap:
    return asciiMap[char]


def decodeShiftJIS( sjis ):
  try:
    return sjis.to_bytes(2,byteorder='big',signed=False).decode('cp932')
  except:
    # print( "BAD SHIFTJIS: 0x%02X" % sjis )
    return ''

def encodeShiftJIS( ascii ):
  # Se for um caractere japonês (Shift-JIS de 2 bytes)
  if ord(ascii) > 255:
    # O mwilkens usa 'cp932' para mapear caracteres japoneses
    ch = int.from_bytes(bytearray(ascii,'cp932'),byteorder='big') - 0x8000
    return ch.to_bytes(2,byteorder='little',signed=False)
  
  # Se for um caractere ASCII, mapear para Shift-JIS de largura dupla (Zenkaku)
  # O mwilkens' mapASCII já faz isso, mas precisamos garantir que ele lide com
  # caracteres que não estão no mapa (como 'T', 'h', 'e', etc.)
  
  # O erro anterior era porque o mapASCII não mapeava todos os caracteres ASCII.
  # Vamos usar a lógica do mwilkens para mapear letras e números.
  
  # Mapeamento de letras maiúsculas (A-Z)
  if( ord(ascii) >= 0x41 and ord(ascii) <= 0x5A ):
    # 0x41 ('A') -> 0x8260 ('Ａ')
    c = ord(ascii) + 0x8260 - 0x41
    return (c - 0x8000).to_bytes(2,byteorder='little',signed=False)
  
  # Mapeamento de letras minúsculas (a-z)
  elif( ord(ascii) >= 0x61 and ord(ascii) <= 0x7A ):
    # 0x61 ('a') -> 0x8281 ('ａ')
    c = ord(ascii) + 0x8281 - 0x61
    return (c - 0x8000).to_bytes(2,byteorder='little',signed=False)
  
  # Mapeamento de números (0-9)
  elif( ord(ascii) >= 0x30 and ord(ascii) <= 0x39 ):
    # 0x30 ('0') -> 0x824F ('０')
    c = ord(ascii) + 0x824F - 0x30
    return (c - 0x8000).to_bytes(2,byteorder='little',signed=False)
  
  # Mapeamento de pontuação (usando mapASCII para o resto)
  elif ascii in asciiMap:
    c = asciiMap[ascii]
    return (c - 0x8000).to_bytes(2,byteorder='little',signed=False)
  
  # Se não for mapeado, retorna um caractere de espaço (ou erro)
  # Para evitar o erro, vamos retornar o código do espaço (0x8140)
  print(f"AVISO: Caractere ASCII '{ascii}' não mapeado. Usando espaço.")
  c = 0x8140
  return (c - 0x8000).to_bytes(2,byteorder='little',signed=False)