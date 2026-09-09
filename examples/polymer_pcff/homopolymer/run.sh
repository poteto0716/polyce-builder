#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
../../common/check_external.sh pcff
mkdir -p output
../../../bin/polyce-build build.polyce > output/report.json
python3 ../../common/check_data.py output/pmma10.data
printf 'PASS: output/pmma10.data (LAMMPS data)\n'
