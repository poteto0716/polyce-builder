# PCFF homopolymer

One packed PMMA chain with ten repeat units at 1.13 g/cm³. This is a small model-construction example, not an equilibrated
bulk sample.

## Requirements

Ubuntu 24.04 x86_64, PolyCE, Bash, Python 3 and the separately obtained PCFF
parameter/template files. Follow [external data setup](../../../docs/external_data.md)
once. LAMMPS with CLASS2 and MOLECULE is optional for energy evaluation.

## Monomers and sequence

The complete input is [build.polyce](build.polyce). MMA is
`*CC(C)(C(=O)OC)*`; STY is `*C(c1ccccc1)C*` where present. The stars are the
two repeat-unit attachment ports. `terminator '*C'` supplies methyl end caps.

Sequence: `A-A-A-A-A-A-A-A-A-A (A = MMA)`.

PolyCE compiles chains, assigns database types and parameters, packs the requested
chains into the density-derived periodic box, and writes LAMMPS topology/data.
The force field is [pcff.ff](../../common/pcff.ff), using class-II terms, 9.5 Å
cutoffs, sixth-power mixing and the original PCFF template database.

## Run and exact command

```bash
cd examples/polymer_pcff/homopolymer
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

- `output/pmma10.data`: LAMMPS data, including coordinates, box, topology and coefficients.
- `output/pmma10.in.styles`: LAMMPS settings and data-file loading command.
- `output/pmma10.chains.csv`: actual repeat-unit sequence for every chain.
- `output/pmma10.identity`: atom identity information.
- `output/report.json`, `output/run.log`, `output/timing.json`: local run reports.

Success is exit code 0 and a final `PASS` line. Repeat the basic checks with:

```bash
python3 ../../common/check_data.py output/pmma10.data
cat output/pmma10.chains.csv
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
