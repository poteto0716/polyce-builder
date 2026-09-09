#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
../common/check_external.sh iff
mkdir -p structure substrate_slab/output polymer_bulk/output
python3 prepare_silica.py ../../external/iff/silica.car ../../external/iff/silica.mdf \
  structure/silica.mol2 --name silica --wrap xy --z-shift 2.0 \
  --json structure/conversion.json > structure/conversion.stdout.json
../../bin/polyce-build substrate_slab/build.polyce > substrate_slab/output/report.json
../../bin/polyce-build polymer_bulk/build.polyce > polymer_bulk/output/report.json
python3 ../common/check_data.py substrate_slab/output/substrate.data polymer_bulk/output/polymer.data
echo 'PASS: both components built. Merge, relaxation and analysis require ./run_lammps.sh.'
