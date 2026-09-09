#!/usr/bin/env python3
# Runtime helper for this example; conversion/offset logic preserved.
import argparse
import json
import re
import sys
from collections import Counter

def read_car(path):
    atoms = []
    cell = None
    with open(path) as fh:
        for line in fh:
            if line.startswith('PBC '):
                f = line.split()
                cell = [float(f[1]), float(f[2]), float(f[3]), float(f[4]), float(f[5]), float(f[6])]
                continue
            if line.startswith('!') or line.startswith('PBC=') or line.startswith('end'):
                continue
            f = line.split()
            if len(f) < 9:
                continue
            atoms.append({'name': f[0], 'position': (float(f[1]), float(f[2]), float(f[3])), 'residue': int(f[5]), 'type': f[6], 'element': f[7], 'charge': float(f[8])})
    if cell is None:
        raise SystemExit(f'{path}: no PBC record; the model states no cell')
    return (cell, atoms)
_PARTNER = re.compile('^(?:XXXX_(\\d+):)?([A-Za-z]+\\d+)(?:%[-0-9]+)?(?:#\\S+)?$')

def read_mdf_bonds(path, index):
    bonds = set()
    unresolved = []
    in_topology = False
    with open(path) as fh:
        for raw in fh:
            line = raw.rstrip('\n')
            if line.startswith('#topology'):
                in_topology = True
                continue
            if line.startswith('#') and (not line.startswith('#topology')):
                in_topology = False
                continue
            if not in_topology or not line.startswith('XXXX_'):
                continue
            f = line.split()
            head = f[0]
            residue, name = head[len('XXXX_'):].split(':')
            here = index.get((int(residue), name))
            if here is None:
                unresolved.append(head)
                continue
            for token in f[12:]:
                m = _PARTNER.match(token)
                if not m:
                    unresolved.append(token)
                    continue
                other_residue = int(m.group(1)) if m.group(1) else int(residue)
                there = index.get((other_residue, m.group(2)))
                if there is None:
                    unresolved.append(token)
                    continue
                if there == here:
                    raise SystemExit(f'{path}: atom {head} is bonded to itself')
                bonds.add((min(here, there), max(here, there)))
    if unresolved:
        raise SystemExit(f"{path}: {len(unresolved)} connection(s) name no atom, first is '{unresolved[0]}'")
    return sorted(bonds)

def write_mol2(path, name, cell, atoms, bonds):
    with open(path, 'w') as fh:
        fh.write('# Converted from an INTERFACE force field surface model by\n')
        fh.write('# prepare_silica.py. Types and charges are the\n')
        fh.write('# published ones; see SOURCES.md for the model and its citation.\n')
        fh.write('@<TRIPOS>MOLECULE\n')
        fh.write(f'{name}\n')
        fh.write(f' {len(atoms)} {len(bonds)} 1 0 0\n')
        fh.write('SURFACE\n')
        fh.write('USER_CHARGES\n\n')
        fh.write('@<TRIPOS>ATOM\n')
        for i, a in enumerate(atoms, start=1):
            x, y, z = a['position']
            fh.write(f"{i:7d} {a['name']:<8s} {x:12.6f} {y:12.6f} {z:12.6f} {a['type']:<6s} 1 {name:<12s} {a['charge']:9.4f}\n")
        fh.write('\n@<TRIPOS>BOND\n')
        for b, (i, j) in enumerate(bonds, start=1):
            fh.write(f'{b:7d} {i + 1:7d} {j + 1:7d} 1\n')
        fh.write('\n@<TRIPOS>CRYSIN\n')
        fh.write(' {:.4f} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f} 1 1\n'.format(*cell))

def bond_lengths(atoms, bonds, cell, periodic):
    out = []
    for i, j in bonds:
        d = []
        for axis in range(3):
            v = atoms[j]['position'][axis] - atoms[i]['position'][axis]
            if periodic[axis]:
                L = cell[axis]
                v -= L * round(v / L)
            d.append(v)
        out.append((d[0] * d[0] + d[1] * d[1] + d[2] * d[2]) ** 0.5)
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('car')
    ap.add_argument('mdf')
    ap.add_argument('out')
    ap.add_argument('--name', default='silica')
    ap.add_argument('--json', dest='report')
    ap.add_argument('--wrap', default='', help="axes to fold into [0, L), e.g. 'xy'")
    ap.add_argument('--z-shift', dest='z_shift', type=float, default=0.0)
    args = ap.parse_args()
    cell, atoms = read_car(args.car)
    index = {}
    for i, a in enumerate(atoms):
        key = (a['residue'], a['name'])
        if key in index:
            raise SystemExit(f"{args.car}: residue {key[0]} names '{key[1]}' twice")
        index[key] = i
    bonds = read_mdf_bonds(args.mdf, index)
    periodic = [ax in args.wrap for ax in 'xyz']
    before = bond_lengths(atoms, bonds, cell, [True, True, True])
    for a in atoms:
        x, y, z = a['position']
        for axis, value in enumerate((x, y, z)):
            if periodic[axis]:
                value -= cell[axis] * (value // cell[axis])
            if axis == 2:
                value += args.z_shift
            a['position'] = a['position'][:axis] + (value,) + a['position'][axis + 1:]
    after = bond_lengths(atoms, bonds, cell, [True, True, True])
    bond_drift = max((abs(b - a) for b, a in zip(before, after))) if bonds else 0.0
    if bond_drift > 1e-09:
        raise SystemExit(f'a rigid operation changed a bond by {bond_drift:.3e} A; that is not a rigid operation')
    write_mol2(args.out, args.name, cell, atoms, bonds)
    types = Counter((a['type'] for a in atoms))
    charge_of = {}
    for a in atoms:
        charge_of.setdefault(a['type'], set()).add(round(a['charge'], 6))
    for t, qs in charge_of.items():
        if len(qs) > 1:
            raise SystemExit(f"type '{t}' carries {len(qs)} different charges: {sorted(qs)}")
    degree = Counter()
    for i, j in bonds:
        degree[i] += 1
        degree[j] += 1
    by_type_degree = {}
    for i, a in enumerate(atoms):
        by_type_degree.setdefault(a['type'], Counter())[degree.get(i, 0)] += 1
    extent = {}
    for axis, k in enumerate('xyz'):
        vs = [a['position'][axis] for a in atoms]
        extent[k] = [min(vs), max(vs)]
    report = {'source_car': args.car, 'source_mdf': args.mdf, 'atoms': len(atoms), 'bonds': len(bonds), 'cell': cell, 'wrapped_axes': args.wrap, 'z_shift': args.z_shift, 'largest_bond_length_change': bond_drift, 'bonds_crossing_a_boundary': sum((1 for raw, imaged in zip(bond_lengths(atoms, bonds, cell, [False, False, False]), after) if raw - imaged > 1e-06)), 'longest_bond': max(after) if bonds else 0.0, 'extent': extent, 'types': dict(sorted(types.items())), 'charge_per_type': {t: sorted(q)[0] for t, q in sorted(charge_of.items())}, 'net_charge': round(sum((a['charge'] for a in atoms)), 9), 'coordination': {t: dict(sorted(c.items())) for t, c in sorted(by_type_degree.items())}}
    text = json.dumps(report, indent=2)
    if args.report:
        with open(args.report, 'w') as fh:
            fh.write(text + '\n')
    print(text)
    return 0
if __name__ == '__main__':
    sys.exit(main())
