import csv
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from libs import huffman

Q41_PATH = os.path.join('input', 'HBD1PS1D.Q41')
ADDRESS_MAP_PATH = os.path.join('tools_output', 'dq4_address_mapping.csv')
TRANSLATION_CSV_PATH = os.path.join('translation_files', 'dq4_translation_para_injetar.csv')
REPORT_PATH = os.path.join('tools_output', 'reinsert_english_report.csv')

# Helper to read translation CSV (ID_HEX -> ENGLISH)
def load_translations(csv_path):
    translations = {}
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        for i, row in enumerate(reader):
            if i == 0:  # Skip header
                continue
            if len(row) < 2:
                continue
            id_hex = row[0].strip().replace('"','')
            eng = row[1].strip().replace('"','')
            if id_hex and id_hex != 'ID_HEX':
                translations[id_hex] = eng
    return translations

# Helper to read address mapping (ID_HEX -> offset)
def load_address_map(csv_path):
    mapping = {}
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        for i, row in enumerate(reader):
            if i == 0:  # Skip header
                continue
            if len(row) < 6:
                continue
            try:
                id_hex = row[1].strip()
                offset = int(row[5], 16) if row[5].startswith('0x') else int(row[5])
                if id_hex:
                    mapping[id_hex] = offset
            except Exception:
                continue
    return mapping

# Extract Huffman tree from Q41 at offset (reuse code from libs/huffman.py)
def extract_huffman_tree(q41_bytes, offset):
    # Heuristic: scan backwards for tree terminator (\x00\x00), then parse
    window = q41_bytes[max(0, offset-256):offset+256]
    for i in range(len(window)):
        if window[i:i+2] == b'\x00\x00':
            try:
                tree = huffman.makeHuffTree(window[i:])
                return tree
            except Exception:
                continue
    return None

# Main reinsertion routine
def reinsert_english():
    translations = load_translations(TRANSLATION_CSV_PATH)
    address_map = load_address_map(ADDRESS_MAP_PATH)
    with open(Q41_PATH, 'rb') as f:
        q41_bytes = bytearray(f.read())
    report = []
    for id_hex, eng_text in translations.items():
        if not eng_text:
            continue  # skip untranslated
        offset = address_map.get(id_hex)
        if offset is None:
            continue
        # Try to extract Huffman tree
        tree = extract_huffman_tree(q41_bytes, offset)
        if tree:
            try:
                encoded = huffman.encodeWithTree(tree, eng_text)
                # Check if fits (conservative: do not overwrite beyond original block)
                orig_len = 256  # TODO: get real block size if available
                if len(encoded) <= orig_len:
                    q41_bytes[offset:offset+len(encoded)] = encoded
                    report.append([id_hex, 'OK', len(encoded), 'tree_reuse'])
                else:
                    report.append([id_hex, 'FAIL_SIZE', len(encoded), 'tree_reuse'])
            except Exception as e:
                report.append([id_hex, 'FAIL_ENCODE', 0, 'tree_reuse'])
        else:
            # Fallback: build new tree
            try:
                encoded, tree_bytes = huffman.encodeHuffman(eng_text)
                orig_len = 256  # TODO: get real block size if available
                if len(encoded) + len(tree_bytes) <= orig_len:
                    q41_bytes[offset:offset+len(encoded)] = encoded
                    report.append([id_hex, 'OK', len(encoded), 'new_tree'])
                else:
                    report.append([id_hex, 'FAIL_SIZE', len(encoded), 'new_tree'])
            except Exception as e:
                report.append([id_hex, 'FAIL_ENCODE', 0, 'new_tree'])
    # Write modified Q41
    with open(Q41_PATH.replace('.Q41', '_ENGLISH.Q41'), 'wb') as f:
        f.write(q41_bytes)
    # Write report
    with open(REPORT_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID_HEX', 'STATUS', 'ENCODED_LEN', 'METHOD'])
        writer.writerows(report)
    print(f'Reinsertion complete. Output: {Q41_PATH.replace(".Q41", "_ENGLISH.Q41")}, Report: {REPORT_PATH}')

if __name__ == '__main__':
    reinsert_english()
