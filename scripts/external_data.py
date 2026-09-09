#!/usr/bin/env python3
"""Install user-obtained data; this script does not download or grant rights."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PINS = json.loads((ROOT / 'scripts/external_checksums.json').read_text())


def checked(name, data):
    if hashlib.sha256(data).hexdigest() != PINS[name]:
        raise ValueError(f'{name}: checksum differs from the validated dataset')
    return data


def main():
    args = sys.argv[1:]
    if len(args) != 2 or args[0] not in ('pcff', 'iff', 'verify'):
        sys.exit('Usage: external_data.py pcff FIELD_DIRECTORY | iff ARCHIVE.zip | verify pcff|iff')
    mode, location = args
    if mode == 'verify':
        if location not in ('pcff', 'iff'):
            raise ValueError('verify requires pcff or iff')
        for name in PINS:
            if name.startswith(location + '/'):
                checked(name, (ROOT / 'external' / name).read_bytes())
        print(f'External {location}: checksums PASS')
        return
    pending = {}
    if mode == 'pcff':
        for name in PINS:
            if name.startswith('pcff/'):
                pending[name] = checked(name, (Path(location) / Path(name).name).read_bytes())
    else:
        archive = Path(location).read_bytes()
        if hashlib.sha256(archive).hexdigest() != '42b26c36ee91254eb83b2e87f8ac4dd8258dd59b4d7aa966c5fd8123410a2086':
            raise ValueError('IFF archive checksum mismatch; see docs/external_data.md')
        with zipfile.ZipFile(location) as z:
            for name in PINS:
                if not name.startswith('iff/'):
                    continue
                leaf = Path(name).name
                member = ('FORCE_FIELDS/' + leaf if leaf.startswith('pcff_') else
                          'MODEL_DATABASE/SILICA/silica_Q3_amorph_4_7OH_0pct_ion.' + leaf.split('.')[-1])
                pending[name] = checked(name, z.read('INTERFACE_FF_1_5/' + member))
    for name, data in pending.items():
        path = ROOT / 'external' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    print(f'Installed {mode} for local use only. Do not include external data in a release.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        sys.exit(str(exc))
