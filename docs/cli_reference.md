# CLI reference

## polyce-build

The distributed executable builds and packs polymers and imported environments,
assigns the selected force-field parameters and writes LAMMPS data and styles.
Both `bin/polyce-build --help` and `bin/polyce-build -h` return exit code 0:

```text
PolyCE - Polymer Construction Engine
Molecular system builder for molecular dynamics

usage: polyce-build INPUT [key=value ...]      build a system from a request
```

The native CLI accepts one configuration file followed by optional `key=value`
overrides. It has no separate `merge` or `analyze` subcommand. Those operations in
the interface example are performed by LAMMPS and the example analysis script.

```bash
bin/polyce-build examples/polymer_pcff/homopolymer/build.polyce
bin/polyce-build examples/polymer_pcff/homopolymer/build.polyce chains=2 seed=1234
```

Quote multiword overrides as a single shell argument, for example
`'cell=40.3148 41.4320 density' 'density=1.18'`. The `density` cell edge is solved
from molecular mass and density when the amount of material is specified.

## Configuration used by these examples

Input starts with `polyce-build 1`. Paths in a build input are relative to that
input file; parameter/template paths in a `.ff` file are relative to that file.

| Record | Meaning / example |
|---|---|
| `name pmma` | System label |
| `seed 12345` | Structure-generation seed |
| `sequence_seed 7` | Sequence randomization seed |
| `forcefield ../../common/pcff.ff` | Force-field descriptor |
| `monomer A '*CC(C)(C(=O)OC)*'` | MMA repeat unit with two attachment ports |
| `monomer STY '*C(c1ccccc1)C*'` | Styrene repeat unit |
| `terminator '*C'` | Methyl cap on both ends |
| `degree 10` | Repeat units per chain |
| `chains 2` | Number of whole chains |
| `density 1.110` | Requested packing density, g/cm³ in real units |
| `temperature 300` | Growth sampling temperature, K |
| `cell 40.3148 41.4320 34.245854` | Explicit orthorhombic lengths, Å |
| `periodic 1 1 0` | Periodic x/y, free z |
| `replicate 2 2 1` | Tile an imported structure twice in x/y and once in z |
| `image_flags yes` | Write molecular image flags for subsequent unwrapping |
| `output output polymer` | Directory and filename prefix |

A single monomer gives a homopolymer. Blocks use `architecture blocks` followed
by ordered `block MMA 6` and `block STY 6` records. Random exact composition uses
`architecture random-exact` and `fraction 0.5` at the end of each monomer record.
The twelve-unit example has exactly six of each monomer on each chain;
`sequence_seed` determines their shuffle. The realized sequences are written to
`*.chains.csv`.

The silica input uses `environment silica file ../structure/silica.mol2 format
mol2 replicate 2 2 1 parameterization preserve mobility fixed`. The existing
surface supplies its types, charges and connectivity; it does not undergo organic
template typing. `replicate` builds the 2×2 in-plane supercell from the CRYSIN
lattice in the MOL2 file. For the continuous periodic silica network, molecular
image flags are omitted.

## Force-field descriptors

`parameters class2 PATH` loads a parameter database and `typing templates PATH`
loads its typing rules. `special_bonds`, `pair_style` and `pair_modify` describe
the corresponding LAMMPS treatment. IFF descriptors use `electrostatics pppm`
with `accuracy 1e-5`; the free-surface descriptor additionally specifies `slab 3.0`.
The ordinary PCFF polymer examples retain the existing 9.5 Å Coulomb/dispersion
cutoffs. See [examples](examples.md) for the scope of these demonstrations.

## Outputs and exit status

`PREFIX.data` contains atoms, box, bonded topology and force-field coefficients.
`PREFIX.in.styles` selects LAMMPS styles and reads the data file by basename, so
run LAMMPS from the output directory. `PREFIX.chains.csv` records sequences;
`PREFIX.identity` records atom identity. JSON on stdout is captured by the example
as `report.json`; generated `run.log` and `timing.json` report the local run.
These generated reports describe the user's own machine and inputs and are not
part of the distribution.

Exit code 0 denotes successful construction; nonzero denotes an error. Missing
CLI input returns 2. The example scripts stop on errors and print `PASS` only
after output validation. Construction does not establish thermodynamic equilibrium.
