#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
case "${1:-}" in
  pcff) files=(pcff/pcff.frc pcff/pcff_templates.dat) ;;
  iff) files=(iff/pcff_interface_v1_5.frc iff/pcff_interface_v1_5_templates.dat iff/silica.car iff/silica.mdf) ;;
  *) echo 'Usage: check_external.sh pcff|iff' >&2; exit 2 ;;
esac
for f in "${files[@]}"; do
  if [[ ! -s "$root/external/$f" ]]; then
    echo "Missing external/$f. Follow docs/external_data.md, then rerun this example." >&2
    exit 2
  fi
done
(cd "$root" && python3 scripts/external_data.py verify "$1")
