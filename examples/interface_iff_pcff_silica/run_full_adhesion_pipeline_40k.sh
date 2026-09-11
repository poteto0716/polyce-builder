#!/bin/bash
# End-to-end, resumable 40k workflow:
# polymer/substrate build -> z surface/minimization -> merge -> interface MD ->
# interaction energy -> upper-quarter SMD/Jarzynski PMF.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../.." && pwd)"
SUBSTRATE_DIR="$HERE/../bulk_first/substrate_slab"
BUILDER=${POLYCE_BUILD:-$ROOT/build/release/apps/polyce-build}
OUT="$HERE/runs/interface_bias_40k"
MAX_ATTEMPTS=3
POLL_SECONDS=60
INTERFACE_SCALE=1
SMD_SCALE=1
REPLICAS=10
ADOPT_INTERFACE_PID=""
ADOPT_SUPERVISOR_PID=""

while [ $# -gt 0 ]; do
    case "$1" in
        --out) OUT=$2; shift 2 ;;
        --max-attempts) MAX_ATTEMPTS=$2; shift 2 ;;
        --poll-seconds) POLL_SECONDS=$2; shift 2 ;;
        --interface-scale) INTERFACE_SCALE=$2; shift 2 ;;
        --smd-scale) SMD_SCALE=$2; shift 2 ;;
        --replicas) REPLICAS=$2; shift 2 ;;
        --adopt-interface-pid) ADOPT_INTERFACE_PID=$2; shift 2 ;;
        --adopt-supervisor-pid) ADOPT_SUPERVISOR_PID=$2; shift 2 ;;
        --smoke) INTERFACE_SCALE=5000; SMD_SCALE=1000; REPLICAS=2; shift ;;
        -h|--help)
            sed -n '2,4p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

[ "$MAX_ATTEMPTS" -ge 1 ] || { echo "--max-attempts must be at least 1" >&2; exit 2; }
[ "$POLL_SECONDS" -ge 1 ] || { echo "--poll-seconds must be at least 1" >&2; exit 2; }
[ "$INTERFACE_SCALE" -ge 1 ] || { echo "--interface-scale must be at least 1" >&2; exit 2; }
[ "$SMD_SCALE" -ge 1 ] || { echo "--smd-scale must be at least 1" >&2; exit 2; }
[ "$REPLICAS" -ge 2 ] || { echo "--replicas must be at least 2" >&2; exit 2; }
[ -x "$BUILDER" ] || { echo "PolyCE builder not executable: $BUILDER" >&2; exit 1; }

mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
PIPELINE_LOG="$OUT/full_pipeline.log"
LOCK_FILE="$OUT/full_pipeline.lock"

# Two master drivers must never write the same stage outputs concurrently.
exec 9>"$LOCK_FILE"
if command -v flock >/dev/null && ! flock -n 9; then
    echo "another full pipeline owns $LOCK_FILE" >&2
    exit 1
fi

note() {
    printf '%s %-18s %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$1" "$2" | tee -a "$PIPELINE_LOG"
}

substrate_complete() {
    [ -s "$SUBSTRATE_DIR/output/substrate.data" ] &&
        [ -s "$SUBSTRATE_DIR/output/substrate.in.styles" ]
}

polymer_complete() {
    [ -s "$HERE/output_40k/polymer.data" ] &&
        [ -s "$HERE/output_40k/polymer.in.styles" ] &&
        [ -s "$HERE/output_40k/polymer.identity" ] &&
        [ -s "$HERE/output_40k/polymer.chains.csv" ]
}

interface_complete() {
    [ -s "$OUT/summary.txt" ] || return 1
    local branch
    for branch in control bias_0p05 bias_0p15; do
        [ -s "$OUT/$branch/09_interface_final.data" ] || return 1
        [ -s "$OUT/$branch/interface_room.dat" ] || return 1
        [ -s "$OUT/$branch/adhesion_summary.txt" ] || return 1
        [ -s "$OUT/$branch/interface_siloxane_profile.txt" ] || return 1
    done
}

smd_complete() {
    [ -s "$OUT/summary_smd_pmf.txt" ] || return 1
    local branch replica
    for branch in control bias_0p05 bias_0p15; do
        [ -s "$OUT/$branch/smd_25pct/pmf_summary.txt" ] || return 1
        [ -s "$OUT/$branch/smd_25pct/pmf_jarzynski.csv" ] || return 1
        for replica in $(seq 1 "$REPLICAS"); do
            [ -f "$OUT/$branch/smd_25pct/pull_${replica}.done" ] || return 1
        done
    done
}

build_substrate() {
    (cd "$SUBSTRATE_DIR" && "$BUILDER" build.polyce)
}

build_polymer() {
    (cd "$HERE" && ./build_40k.sh)
}

run_interface() {
    (cd "$HERE" && ./run_interface_bias_40k.sh --out "$OUT" --scale "$INTERFACE_SCALE")
}

run_smd() {
    (cd "$HERE" && ./run_smd_pmf_40k.sh --out "$OUT" --replicas "$REPLICAS" --scale "$SMD_SCALE")
}

# Run one coarse stage. The child drivers have finer-grained output gates, so
# another attempt resumes the incomplete substage rather than starting over.
run_stage() {
    local name=$1 check_function=$2 run_function=$3
    local stage_log="$OUT/stage_${name}.log"
    if "$check_function"; then
        note "$name" "complete output exists; skipped"
        return 0
    fi

    local attempt=1 rc=0
    while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
        note "$name" "attempt $attempt/$MAX_ATTEMPTS started"
        if "$run_function" >> "$stage_log" 2>&1; then
            rc=0
        else
            rc=$?
        fi
        if "$check_function"; then
            note "$name" "completed"
            return 0
        fi
        note "$name" "attempt $attempt ended status=$rc without completion output"
        attempt=$((attempt + 1))
        [ "$attempt" -le "$MAX_ATTEMPTS" ] && sleep "$POLL_SECONDS"
    done
    note "$name" "automatic attempt limit reached"
    return 1
}

pid_alive() {
    [ -n "$1" ] && kill -0 "$1" 2>/dev/null
}

wait_for_adopted_interface() {
    if interface_complete; then
        return 0
    fi
    if ! pid_alive "$ADOPT_INTERFACE_PID" && ! pid_alive "$ADOPT_SUPERVISOR_PID"; then
        return 1
    fi

    note interface "adopting active PID=$ADOPT_INTERFACE_PID supervisor=$ADOPT_SUPERVISOR_PID"
    while ! interface_complete; do
        if ! pid_alive "$ADOPT_INTERFACE_PID" && ! pid_alive "$ADOPT_SUPERVISOR_PID"; then
            note interface "adopted processes exited before completion; switching to local resume"
            return 1
        fi
        sleep "$POLL_SECONDS"
    done
    note interface "adopted calculation completed"
    return 0
}

note pipeline "started out=$OUT"
run_stage substrate substrate_complete build_substrate || exit 1
run_stage polymer polymer_complete build_polymer || exit 1

if interface_complete; then
    note interface "complete outputs exist; skipped"
elif ! wait_for_adopted_interface; then
    run_stage interface interface_complete run_interface || exit 1
fi

run_stage smd smd_complete run_smd || exit 1

{
    echo "40k end-to-end adhesion pipeline complete"
    echo "polymer_data $HERE/output_40k/polymer.data"
    echo "substrate_data $SUBSTRATE_DIR/output/substrate.data"
    echo "interface_summary $OUT/summary.txt"
    echo "smd_summary $OUT/summary_smd_pmf.txt"
    echo "completed_at $(date '+%Y-%m-%d %H:%M:%S %Z')"
} > "$OUT/full_pipeline_summary.txt"

note pipeline "completed"
