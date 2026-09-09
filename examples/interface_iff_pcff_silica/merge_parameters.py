#!/usr/bin/env python3
# Runtime helper for this example; conversion/offset logic preserved.
import sys
SECTIONS = ('Masses', 'Atoms', 'Velocities', 'Bonds', 'Angles', 'Dihedrals', 'Impropers')

def read(path):
    counts, types, members = ({}, {}, {})
    section, bonds = (None, {})
    for raw in open(path):
        line = raw.split('#')[0].strip()
        if not line:
            continue
        head = line.split()[0]
        if head in SECTIONS or 'Coeffs' in line:
            section = head if head in SECTIONS else None
            continue
        p = line.split()
        if len(p) >= 2 and (not p[-1].replace('.', '').replace('-', '').isdigit()):
            if len(p) == 2 and p[1] in ('atoms', 'bonds', 'angles', 'dihedrals', 'impropers'):
                counts[p[1]] = int(p[0])
            elif len(p) == 3 and p[2] == 'types':
                types[p[1]] = int(p[0])
            continue
        if section == 'Bonds' and len(p) >= 4:
            a, b = (int(p[2]), int(p[3]))
            bonds.setdefault(a, set()).add(b)
            bonds.setdefault(b, set()).add(a)
            members.setdefault('bond', {})
            for x in (a, b):
                members['bond'][x] = members['bond'].get(x, 0) + 1
        elif section in ('Angles', 'Dihedrals', 'Impropers') and len(p) >= 5:
            key = section.lower()[:-1]
            members.setdefault(key, {})
            for tok in p[2:]:
                x = int(tok)
                members[key][x] = members[key].get(x, 0) + 1
    return (counts, types, members, bonds)

def per_atom_max(members, key):
    d = members.get(key, {})
    return max(d.values()) if d else 0

def special_max(bonds):
    best = 0
    for a, first in bonds.items():
        seen = set(first)
        for b in first:
            seen |= bonds.get(b, set())
        for b in list(seen):
            seen |= bonds.get(b, set())
        seen.discard(a)
        best = max(best, len(seen))
    return best

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sub_c, sub_t, sub_m, sub_b = read(sys.argv[1])
    pol_c, pol_t, pol_m, pol_b = read(sys.argv[2])
    out = {'off_a': sub_t.get('atom', 0), 'off_b': sub_t.get('bond', 0), 'off_ang': sub_t.get('angle', 0), 'off_d': sub_t.get('dihedral', 0), 'off_i': sub_t.get('improper', 0), 'add_a': pol_t.get('atom', 0), 'add_b': pol_t.get('bond', 0), 'add_ang': pol_t.get('angle', 0), 'add_d': pol_t.get('dihedral', 0), 'add_i': pol_t.get('improper', 0), 'n_sub': sub_c.get('atoms', 0)}
    for key, var in (('bond', 'xb'), ('angle', 'xang'), ('dihedral', 'xd'), ('improper', 'xi')):
        out[var] = max(per_atom_max(sub_m, key), per_atom_max(pol_m, key))
    out['xs'] = max(special_max(sub_b), special_max(pol_b))
    for k, v in out.items():
        print(f'-var {k} {v}')
if __name__ == '__main__':
    main()
