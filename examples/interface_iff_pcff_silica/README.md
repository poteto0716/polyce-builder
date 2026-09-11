# iFF-PCFF silica / PMMA interface

This example uses the existing bulk-first workflow: build a silica slab and a
periodic polymer melt independently, relax and unwrap the polymer with LAMMPS,
merge the two systems, relax the interface, then measure their interaction.

```text
IFF CAR + MDF → silica slab ───────────────────────────┐
                                                     ↓
PMMA monomer → chains → packed periodic melt → slab → merge
                                                     ↓
                                               relaxation
                                                     ↓
                                       surface/interface interaction
```

## Requirements

- Ubuntu 24.04 x86_64, PolyCE, Bash and Python 3 (standard library only).
- The bundled IFF 1.5 parameter database, typing templates and Q3 amorphous
  silica model. Their provenance and pinned checksums are documented in
  [external data](../../docs/external_data.md).
- **LAMMPS is required for merge, relaxation and interaction analysis.** Install
  CLASS2, KSPACE, MOLECULE and EXTRA-FIX functionality, including
  `lj/class2/coul/long`, bonded class2 styles, `pppm`, `wall/reflect`,
  `compute group/group`, `chunk/atom`, `ave/chunk`, `nvt`, and `property/atom`.
  Check available styles with `lmp -h`. A suitable Ubuntu package can be installed
  with `sudo apt-get install lammps`; verify that it contains these features.
- No GPU is required. Use CPU PPPM for the interaction measurement because
  `compute group/group ... kspace yes` is not supported by `pppm/kk`.

## Model and parameter assignment

Silica: a 2×2 in-plane replication of the IFF
`silica_Q3_amorph_4_7OH_0pct_ion` surface, 11712 atoms and 14944 bonds, already
silanol-terminated. `prepare_silica.py` converts the supplied
CAR/MDF coordinates/connectivity to MOL2, wraps x/y and shifts z by +2 Å. It
retains the original `sc4`, `oc23`, `oc24`, `hoy` types and charges, verifies that
bond lengths survive conversion and writes `structure/conversion.json`.
This imports an existing surface; PolyCE does not synthesize amorphous silica or
invent termination chemistry. The builder performs the replication through
`replicate 2 2 1`; the resulting x/y cell is 80.6296 × 82.8640 Å.

Polymer: 80 PMMA chains of DP20, `*CC(C)(C(=O)OC)*`, capped by `*C` at both ends.
The periodic cell is 80.6296 × 82.8640 × 34.245854 Å, with `image_flags yes` so
LAMMPS can unwrap chains before removing z periodicity. The polymer explicitly
uses `build_nonbond_mode physical_corrected`, matching the existing bulk-first
workflow driver rather than relying on the general CLI default. Scaling the chain
count by four preserves the original polymer density when the surface area is
scaled from 1×1 to 2×2.

Both components use the same PCFF-INTERFACE 1.5 class-II parameter database.
Organic types and charges come from its templates and bond increments; silica
retains its supplied types/charges. Parameter assignment happens **before merge**
inside the two PolyCE builds. Each writes its own LAMMPS coefficients. LAMMPS
merges with dynamically computed type offsets and storage reservations and
forms cross interactions by the existing sixth-power rule. Electrostatics use
12 Å real-space cutoffs and PPPM accuracy 1e-5; free-z stages use slab 3.0.
No later ad hoc assignment or new cross-interface force field is introduced.

## Run

```bash
cd examples/interface_iff_pcff_silica
./run.sh
./run_lammps.sh
```

The first script performs all PolyCE-side construction. The second runs the short
**smoke** workflow on CPU. If LAMMPS is named differently:

```bash
LMP=lmp_mpi ./run_lammps.sh
```

The script accepts a single executable name/path in `LMP`, not shell flags.
Set `OMP_NUM_THREADS` if desired; default is 1. Outputs are overwritten on rerun.

Smoke mode uses 100-step stages and minimization limits of 100 iterations/1000
force evaluations, plus 10-step sampling. These are intentionally short execution
checks. They do **not** establish equilibration, an experimentally valid interface,
a converged density profile or an adhesion free energy.

`./run_lammps.sh full` uses the existing inputs' full defaults (up to hundreds of
thousands of steps per stage and 10000/100000 minimization budgets). This can take
substantial time and was not completed in the binary validation. Scientific use
requires inspection of convergence, density profiles, temperature and uncertainties.

## Individual construction commands

From this example directory, these are the exact operations used by `run.sh`:

```bash
../common/check_external.sh iff
mkdir -p structure substrate_slab/output polymer_bulk/output
python3 prepare_silica.py ../../external/iff/silica.car ../../external/iff/silica.mdf \
  structure/silica.mol2 --name silica --wrap xy --z-shift 2.0 \
  --json structure/conversion.json > structure/conversion.stdout.json
../../bin/polyce-build substrate_slab/build.polyce > substrate_slab/output/report.json
../../bin/polyce-build polymer_bulk/build.polyce > polymer_bulk/output/report.json
python3 ../common/check_data.py substrate_slab/output/substrate.data polymer_bulk/output/polymer.data
```

These include silica import/parameterization, polymer chain compilation, packing,
organic parameter assignment and both LAMMPS data exports.

## Individual LAMMPS stages

Run these in order from this example directory. Each prints its actual LAMMPS
command with all expanded variables, writes a stage log and checks resulting data.
Use the same mode throughout; stages consume the preceding stage's files.

```bash
./run_lammps.sh smoke 1  # relax periodic polymer
./run_lammps.sh smoke 2  # unwrap, enlarge box, free z, relax polymer slab
./run_lammps.sh smoke 3  # derive type offsets and merge silica/polymer
./run_lammps.sh smoke 4  # minimize and thermally relax/cool interface
./run_lammps.sh smoke 5  # sample interface interaction and summarize
```

The exact stage inputs are in [lammps/](lammps/); the executable commands are in
[run_lammps.sh](run_lammps.sh). In stage 3,
`python3 ../../merge_parameters.py substrate.data 04_polymer_slab.data` is executed
from `output/smoke/` to generate every type offset and per-atom reservation. These
values are passed to LAMMPS with `-var`; no manual type-number editing is needed.

## Surface/interface interaction analysis

The measurement stage runs on the relaxed/cooled system with the bottom 3 Å of
the substrate fixed and any applied load removed. It samples:

```text
compute EINT polymer group/group substrate pair yes kspace yes
```

`interface_room.dat` contains step, cross-interface energy (kcal/mol) and geometric
gap (Å). `analyze.py` averages the second half of the samples, reports the sample
standard deviation and computes `-E_interface / area` in J/m².

To repeat only the numerical summary:

```bash
python3 analyze.py output/smoke/interface_room.dat \
  output/smoke/09_interface_final.data
```

This is **surface/interface interaction energy**, including pair and reciprocal
contributions. Its negative per-area value is an energy-based adhesion proxy;
it is not a reversible work of separation, PMF, or free energy. This example does
not perform a peeling/Jarzynski calculation.

## Outputs and success checks

| File | Meaning |
|---|---|
| `structure/silica.mol2`, `structure/conversion.json` | Converted published model and conservation checks |
| `substrate_slab/output/substrate.data` | Parameterized silica slab |
| `polymer_bulk/output/polymer.data` | Packed parameterized PMMA melt |
| `output/smoke/02_polymer_bulk_relaxed.data` | Periodic polymer after initial relaxation |
| `output/smoke/04_polymer_slab.data` | Whole molecules, free z, slab geometry |
| `output/smoke/05_interface_merged.data` | Merged interface with type offsets |
| `output/smoke/08_interface_cooled.data` | Relaxed/cooled interface |
| `output/smoke/09_interface_final.data` | Interface after measurement |
| `output/smoke/interface_room.dat` | Sampled pair + kspace interaction energy |
| `output/smoke/interaction_summary.json` | Finite-value analysis and area normalization |
| `output/smoke/*density*.dat` | Polymer/interface density profiles |

Exit code 0 and final `PASS` lines indicate successful execution and basic
consistency. The expected component and merged counts are in
[validation](../../docs/validation.md). Generated data are checked for finite
numbers, positive cell lengths, count agreement and valid topology references.
Examine `output/smoke/01.log` through `04b.log` for LAMMPS results. Atom loss or
LAMMPS errors are failures, not warnings to ignore. Expected image-flag and
`run 0` warnings observed for this specific workflow are explained in the
validation document.

The substrate is periodic in x/y but free in z; its continuous bond network must
not be unwrapped as a finite molecule. Only the polymer is unwrapped. Atoms outside
a periodic face in initial PolyCE files are remapped by LAMMPS on reading.

The required force-field and silica source files are tracked under `external/`,
so this example's PolyCE construction stage runs offline immediately after clone.
Generated structures and outputs remain ignored.
