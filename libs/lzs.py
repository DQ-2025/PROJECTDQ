import math
from libs.helpers import printHex

# Implementação simplificada - retorna dados sem descompressão
# A maioria dos blocos de texto tipo 40 não usa LZS

def decompress( in_data, d_size ):
    # Retorna dados sem modificação
    # Blocos de texto tipo 40 geralmente não usam LZS
    return in_data[:d_size] if d_size > 0 else in_data

def compress( in_data, c_size ):
    # Não implementado - retorna dados originais
    data = in_data
    l = len(data)
    while l % 4 != 0:
        l += 1
    l = l - len(data)
    return data + bytes(l)
