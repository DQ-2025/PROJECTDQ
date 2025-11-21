with open('input/HBD1PS1D.Q41', 'rb') as f:
    rom = f.read()
header = 0x0E3E1C
body = 0x0E3E2C
text = 0x0E3EEC
pat_text = text.to_bytes(4, 'little')
pat_body = body.to_bytes(4, 'little')
print('Search header bytes for text pat', pat_text.hex())
for i in range(header, header + 64):
    if rom[i:i+4] == pat_text:
        print('Found text ptr at', hex(i))
for i in range(header, header + 64):
    if rom[i:i+4] == pat_body:
        print('Found body ptr at', hex(i))
print('Header dump:')
print(' '.join(['%02x' % b for b in rom[header:header+80]]))
