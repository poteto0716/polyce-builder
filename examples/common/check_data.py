#!/usr/bin/env python3
"""Check LAMMPS full-style data counts, finite numbers, bounds and topology IDs."""
import json
import math
from pathlib import Path
import re
import sys


def check(path):
    text = Path(path).read_text()
    counts, box, sections = {}, {}, {}
    section = None
    for raw in text.splitlines()[1:]:
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        for token in line.split():
            try:
                value = float(token)
            except ValueError:
                continue
            if not math.isfinite(value):
                raise ValueError(f'{path}: non-finite number {token}')
        m = re.fullmatch(r'(\d+) (atoms|bonds|angles|dihedrals|impropers)', line)
        if m:
            counts[m[2]] = int(m[1])
        p = line.split()
        if len(p) == 4 and p[2] in ('xlo', 'ylo', 'zlo'):
            lo, hi = map(float, p[:2])
            if hi <= lo:
                raise ValueError(f'{path}: invalid box {line}')
            box[p[2][0]] = [lo, hi]
        if line[0].isalpha():
            section = line
            sections.setdefault(section, [])
        elif section:
            sections[section].append(p)
    if len(box) != 3 or counts.get('atoms', 0) == 0:
        raise ValueError(f'{path}: missing box/atoms')
    for key in ('atoms', 'bonds', 'angles', 'dihedrals', 'impropers'):
        rows = sections.get(key.capitalize(), [])
        if len(rows) != counts.get(key, 0):
            raise ValueError(f'{path}: {key} header/section mismatch')
        if {int(r[0]) for r in rows} != set(range(1, len(rows) + 1)):
            raise ValueError(f'{path}: invalid {key} IDs')
        if key != 'atoms':
            for row in rows:
                if any(not 1 <= int(a) <= counts['atoms'] for a in row[2:]):
                    raise ValueError(f'{path}: topology references absent atom')
    outside = 0
    for row in sections['Atoms']:
        if len(row) not in (7, 10):
            raise ValueError(f'{path}: expected full atom style')
        for axis, x in zip('xyz', map(float, row[4:7])):
            lo, hi = box[axis]
            if x < lo - 1e-6 or x > hi + 1e-6:
                outside += 1
    return {'file': str(path), 'status': 'PASS', **counts, 'box_A': box,
            'box_lengths_A': {a: hi-lo for a, (lo, hi) in box.items()},
            'finite': True, 'topology_ids_valid': True,
            'coordinate_components_outside_box': outside,
            'bounds_note': 'LAMMPS remaps unwrapped coordinates on periodic axes; check nonperiodic axes separately.'}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Usage: check_data.py DATA [DATA ...]')
    try:
        for arg in sys.argv[1:]:
            print(json.dumps(check(arg), indent=2))
    except (OSError, ValueError, KeyError, IndexError) as exc:
        sys.exit(str(exc))
