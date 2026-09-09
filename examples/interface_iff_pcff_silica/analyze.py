#!/usr/bin/env python3
"""Summarize sampled surface/interface interaction energy, not a free energy."""
import json
import math
import statistics
import sys

if len(sys.argv) != 3:
    sys.exit('Usage: analyze.py interface_room.dat interface.data')
rows = [list(map(float, l.split())) for l in open(sys.argv[1])
        if l.strip() and not l.lstrip().startswith('#')]
if not rows or any(len(r) != 3 or not all(map(math.isfinite, r)) for r in rows):
    sys.exit('Missing or invalid interface energy samples')
edges = {}
for line in open(sys.argv[2]):
    p = line.split()
    if len(p) == 4 and p[2] in ('xlo', 'ylo'):
        edges[p[2]] = float(p[1]) - float(p[0])
area = edges['xlo'] * edges['ylo']
if not math.isfinite(area) or area <= 0:
    sys.exit('Invalid interface area')
tail = rows[len(rows)//2:]
energies = [r[1] for r in tail]
mean = statistics.mean(energies)
print(json.dumps({'status': 'PASS', 'samples_total': len(rows), 'samples_used': len(tail),
                  'area_A2': area, 'mean_E_interface_kcal_mol': mean,
                  'sample_stddev_kcal_mol': statistics.stdev(energies) if len(energies)>1 else 0,
                  'mean_gap_A': statistics.mean(r[2] for r in tail),
                  'negative_E_per_area_J_m2': -mean*4184/(6.02214076e23*area*1e-20),
                  'interpretation': 'Pair plus kspace group/group energy; not a PMF or adhesion free energy.'}, indent=2))
