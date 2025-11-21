#!/usr/bin/env python3
"""
Convert a PlayStation .bin image to a plain .iso (2048-byte sectors) and extract
specified files from the ISO.

Behavior:
- Detects if .bin contains 2048-byte or 2352-byte sectors by checking for the
  Primary Volume Descriptor signature 'CD001' in sector 16.
- If 2352-byte sectors are used, extracts 2048 bytes from each sector (offset 16).
- Writes out <basename>.iso and then extracts the three files if present:
  SYSTEM.CNF, SLPM_869.16, HBD1PS1D.Q41

Usage: python tools/bin_to_iso_and_extract.py [path/to/game.bin]

"""
import sys
from pathlib import Path
import struct

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# files to extract
TARGET_FILES = ["SYSTEM.CNF", "SLPM_869.16", "HBD1PS1D.Q41"]


def detect_sector_size(data: bytes) -> int:
    """Try to detect sector size by checking for 'CD001' at sector 16."""
    for sector in (2048, 2352, 2336):
        off = sector * 16
        if off + 6 <= len(data):
            # The PVD signature is at offset +1..+5 normally, but searching for b'CD001' inside
            # the region is robust.
            block = data[off: off + 64]
            if b'CD001' in block:
                return sector
    # fallback heuristics
    if len(data) % 2352 == 0:
        return 2352
    if len(data) % 2048 == 0:
        return 2048
    return 2048


def bin_to_iso(bin_path: Path, iso_path: Path, sector_size: int) -> None:
    """Convert bin to iso by extracting 2048-byte data sectors."""
    print(f"Converting {bin_path.name} -> {iso_path.name} (sector_size={sector_size})")
    with bin_path.open('rb') as f_in, iso_path.open('wb') as f_out:
        if sector_size == 2048:
            # direct copy
            # copy in chunks
            chunk = 1024 * 1024
            total = 0
            while True:
                data = f_in.read(chunk)
                if not data:
                    break
                f_out.write(data)
                total += len(data)
            print(f"Wrote {total} bytes to {iso_path}")
            return

        # for 2352 or others: read sector-by-sector
        sector = sector_size
        idx = 0
        while True:
            buf = f_in.read(sector)
            if not buf:
                break
            if len(buf) != sector:
                # ignore truncated tail
                break
            # mode1 data starts at offset 16 and is 2048 bytes long
            if len(buf) >= 16 + 2048:
                data = buf[16:16+2048]
            else:
                # unexpected, fallback to zeros
                data = b'\x00' * 2048
            f_out.write(data)
            idx += 1
            if idx % 100000 == 0:
                print(f"  processed {idx} sectors...")
        print(f"Processed {idx} sectors, wrote iso {iso_path}")


# ISO9660 helpers

def le32(b: bytes) -> int:
    return struct.unpack_from('<I', b)[0]


def parse_pvd(iso_bytes: bytes, sector_size: int):
    pvd_off = sector_size * 16
    if pvd_off + 2048 > len(iso_bytes):
        raise ValueError('ISO too small to contain PVD')
    pvd = iso_bytes[pvd_off:pvd_off+2048]
    if b'CD001' not in pvd:
        raise ValueError('PVD signature CD001 not found')
    # Root directory record at offset 156
    # root directory record begins at offset 156 inside the PVD
    root_dr = pvd[156:156+34]
    dr_len = root_dr[0]
    extent_lba = le32(root_dr[2:6])
    extent_size = le32(root_dr[10:14])
    return extent_lba, extent_size


def read_directory(iso_bytes: bytes, sector_size: int, lba: int, size: int):
    # recursive-aware directory reader: returns list of entries (files and dirs)
    base = lba * sector_size
    data = iso_bytes[base: base + size]
    entries = []
    i = 0
    while i < len(data):
        length = data[i]
        if length == 0:
            # move to next sector boundary
            i = ((i // sector_size) + 1) * sector_size
            continue
        rec = data[i:i+length]
        if len(rec) < 34:
            i += length
            continue
        extent = le32(rec[2:6])
        rec_size = le32(rec[10:14])
        # file flags at offset 25
        file_flags = rec[25]
        fi_len = rec[32]
        fi = rec[33:33+fi_len]
        # name decoding
        try:
            name = fi.decode('ascii', errors='ignore')
        except Exception:
            name = str(fi)
        # remove version suffix ;1
        if name.endswith(';1'):
            name = name[:-2]
        # skip current/parent
        if name in ['\x00', '\x01', '\x00\x00']:
            i += length
            continue
        entries.append({'name': name, 'extent': extent, 'size': rec_size, 'is_dir': bool(file_flags & 0x02)})
        i += length
    return entries


def read_directory_recursive(iso_bytes: bytes, sector_size: int, lba: int, size: int, path_prefix=""):
    """Recursively read directory records and return full file listing.
    Returns list of dicts: {'path':..., 'name':..., 'extent':..., 'size':..., 'is_dir':...}
    """
    results = []
    entries = read_directory(iso_bytes, sector_size, lba, size)
    for e in entries:
        full_path = (path_prefix + '/' + e['name']).lstrip('/')
        results.append({'path': full_path, 'name': e['name'], 'extent': e['extent'], 'size': e['size'], 'is_dir': e.get('is_dir', False)})
        if e.get('is_dir'):
            # recursive
            try:
                sub = read_directory_recursive(iso_bytes, sector_size, e['extent'], e['size'], full_path)
                results.extend(sub)
            except Exception:
                # ignore recursion errors
                pass
    return results


def extract_from_iso(iso_path: Path, out_dir: Path, sector_size: int):
    iso_bytes = iso_path.read_bytes()
    lba, size = parse_pvd(iso_bytes, sector_size)
    print(f"Root directory LBA={lba}, size={size}")
    # read recursively all files
    all_entries = read_directory_recursive(iso_bytes, sector_size, lba, size, path_prefix='')
    print(f"Total entries found in ISO: {len(all_entries)}")
    found = {}
    for e in all_entries:
        name_up = e['name'].upper()
        # compare target base names
        if name_up in TARGET_FILES:
            print(f"Found {name_up} at extent {e['extent']} size {e['size']} path {e['path']}")
            start = e['extent'] * sector_size
            data = iso_bytes[start:start+e['size']]
            out_path = out_dir / name_up
            out_path.write_bytes(data)
            found[name_up] = out_path
    # If recursive read didn't yield entries, try a raw-bytes search for filenames as fallback
    if not found:
        print('No entries from directory recursion; trying raw byte search for target filenames...')
        for target in TARGET_FILES:
            # search for both with and without version suffix
            candidates = [target.encode('ascii'), (target + ';1').encode('ascii')]
            for cand in candidates:
                pos = iso_bytes.find(cand)
                if pos != -1:
                    # candidate file id likely at pos; directory record starts ~33 bytes before
                    rec_start = pos - 33
                    if rec_start < 0:
                        continue
                    rec_len = iso_bytes[rec_start]
                    if rec_len == 0 or rec_start + rec_len > len(iso_bytes):
                        continue
                    rec = iso_bytes[rec_start:rec_start+rec_len]
                    try:
                        extent = le32(rec[2:6])
                        fsize = le32(rec[10:14])
                    except Exception:
                        continue
                    print(f"Heuristic found {target} at pos {pos}, extent={extent}, size={fsize}")
                    start = extent * sector_size
                    data = iso_bytes[start:start+fsize]
                    out_path = out_dir / target
                    out_path.write_bytes(data)
                    found[target] = out_path
                    break
            if target in found:
                continue
    return found


def main(argv):
    if len(argv) > 1:
        bin_path = Path(argv[1])
    else:
        bin_path = PROJECT_ROOT / 'game.bin'
    if not bin_path.exists():
        print('game.bin not found at', bin_path)
        return
    iso_path = bin_path.with_suffix('.iso')

    data = bin_path.read_bytes()
    sector = detect_sector_size(data)
    print('Detected sector size:', sector)
    # create iso
    bin_to_iso(bin_path, iso_path, sector)
    # attempt extraction - salvar na pasta /input (ajustado para o workspace)
    out_dir = PROJECT_ROOT / 'input'
    out_dir.mkdir(exist_ok=True)
    try:
        found = extract_from_iso(iso_path, out_dir, 2048)
    except Exception as e:
        print('Failed to parse ISO using sector_size=2048, trying detected sector size...')
        try:
            found = extract_from_iso(iso_path, out_dir, sector)
        except Exception as e2:
            print('Extraction failed:', e2)
            return
    print('Extraction result:')
    for tf in TARGET_FILES:
        print(' -', tf, '->', 'FOUND' if tf in found else 'MISSING')


if __name__ == '__main__':
    main(sys.argv)
