# PCFF random copolymer

Two packed DP12 MMA/styrene chains at 1.110 g/cm³, each with exactly six of each repeat unit. This is a small model-construction example, not an equilibrated
bulk sample.

## Requirements

Ubuntu 24.04 x86_64, PolyCE, Bash, Python 3 and the separately obtained PCFF
parameter/template files. Follow [external data setup](../../../docs/external_data.md)
once. LAMMPS with CLASS2 and MOLECULE is optional for energy evaluation.

## Monomers and sequence

The complete input is [build.polyce](build.polyce). MMA is
`*CC(C)(C(=O)OC)*`; STY is `*C(c1ccccc1)C*` where present. The stars are the
two repeat-unit attachment ports. `terminator '*C'` supplies methyl end caps.

Sequence: `random-exact, fractions 0.5/0.5, sequence_seed 7`.

PolyCE compiles chains, assigns database types and parameters, packs the requested
chains into the density-derived periodic box, and writes LAMMPS topology/data.
The force field is [pcff.ff](../../common/pcff.ff), using class-II terms, 9.5 Å
cutoffs, sixth-power mixing and the original PCFF template database.

## Run and exact command

```bash
cd examples/polymer_pcff/random_copolymer
./run.sh
```

From this directory, the actual PolyCE command inside the script is:

```bash
../../../bin/polyce-build build.polyce > output/report.json
```

The script creates `output/`, verifies external data and checks the generated data.
For manual execution first run `mkdir -p output`. Rerunning overwrites generated
outputs.

## Generated files and success checks

- `output/polymer.data`: LAMMPS data, including coordinates, box, topology and coefficients.
- `output/polymer.in.styles`: LAMMPS settings and data-file loading command.
- `output/polymer.chains.csv`: actual repeat-unit sequence for every chain.
- `output/polymer.identity`: atom identity information.
- `output/report.json`, `output/run.log`, `output/timing.json`: local run reports.

Success is exit code 0 and a final `PASS` line. Repeat the basic checks with:

```bash
python3 ../../common/check_data.py output/polymer.data
cat output/polymer.chains.csv
```

The checker verifies finite numeric values, header/section counts, valid topology
IDs and positive box lengths. Coordinates outside periodic faces are permitted:
LAMMPS remaps them when it reads the file. Expected counts and measured validation
are in [validation](../../../docs/validation.md).

To evaluate the generated model with LAMMPS:

```bash
cd output
lmp -in ../in.check.lmp
```

A successful `run 0` evaluates this initial geometry; it does not relax it.
