#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
LMP=${LMP:-lmp}
mode=${1:-smoke}
stage=${2:-all}
case "$mode" in smoke|full) ;; *) echo 'Usage: run_lammps.sh [smoke|full] [all|1|2|3|4|5]' >&2; exit 2;; esac
case "$stage" in all|1|2|3|4|5) ;; *) echo 'Invalid stage' >&2; exit 2;; esac
command -v "$LMP" >/dev/null || { echo 'Install LAMMPS with CLASS2, KSPACE, MOLECULE and EXTRA-FIX; see README.md.' >&2; exit 2; }
[[ -s polymer_bulk/output/polymer.data && -s substrate_slab/output/substrate.data ]] || {
  echo 'Run ./run.sh first.' >&2; exit 2;
}
mkdir -p "output/$mode"
cd "output/$mode"
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
# Print every actual LAMMPS command so each stage can be reproduced individually.
run() {
  local tag=$1; shift
  printf 'Command:'; printf ' %q' "$LMP" "$@"; printf '\n'
  "$LMP" "$@" -log "$tag.log" > "$tag.stdout" 2>&1 || {
    tail -25 "$tag.stdout" >&2; exit 1;
  }
}
selected() { [[ "$stage" == all || "$stage" == "$1" ]]; }
short_min=(); phase1=(); phase2=(); phase4=(); phase5=()
if [[ "$mode" == smoke ]]; then
  short_min=(-var MIN_ITER 100 -var MIN_EVAL 1000)
  phase1=(-var N_WARM 100 -var N_HOT 100 -var N_COOL 100 -var N_ROOM 100)
  phase2=(-var N_SETTLE 100 -var N_ANNEAL 100 -var PROFILE_EVERY 10 -var PROFILE_REPEAT 10 -var PROFILE_STEPS 100)
  phase4=(-var N_WARM 100 -var N_HOT 100 -var N_COOL 100 -var N_FREE 100)
  phase5=(-var N_ROOM 100 -var SAMPLE_EVERY 10 -var PROFILE_REPEAT 10 -var PROFILE_STEPS 100)
fi
if selected 1; then
  cp ../../polymer_bulk/output/polymer.data 01_polymer_bulk.data
  sed 's|^read_data .*|read_data 01_polymer_bulk.data|' ../../polymer_bulk/output/polymer.in.styles > polymer.in.styles
  run 01 -in ../../lammps/in.01_polymer_relax.lmp -var poly polymer "${short_min[@]}" "${phase1[@]}"
fi
if selected 2; then
  run 02 -in ../../lammps/in.02_polymer_slab.lmp "${short_min[@]}" "${phase2[@]}"
fi
if selected 3; then
  cp ../../substrate_slab/output/substrate.data substrate.data
  python3 ../../merge_parameters.py substrate.data 04_polymer_slab.data > merge_variables.txt
  merge=()
  while read -r flag key value; do
    [[ "$key" == n_sub ]] || merge+=("$flag" "$key" "$value")
  done < merge_variables.txt
  run 03 -in ../../lammps/in.03_merge.lmp -var sub substrate.data -var gap 3.0 -var vac 60.0 "${merge[@]}"
fi
nsub=$(awk '$2=="atoms" {print $1; exit}' ../../substrate_slab/output/substrate.data)
if selected 4; then
  run 04a -in ../../lammps/in.04a_interface_md.lmp -var n_sub "$nsub" "${short_min[@]}" "${phase4[@]}"
fi
if selected 5; then
  run 04b -in ../../lammps/in.04b_interface_measure.lmp -var n_sub "$nsub" "${phase5[@]}"
  python3 ../../analyze.py interface_room.dat 09_interface_final.data > interaction_summary.json
  cat interaction_summary.json
fi
python3 ../../../common/check_data.py ./*.data
echo "PASS: LAMMPS $mode stage $stage. Smoke mode validates execution, not equilibration or adhesion free energy."
