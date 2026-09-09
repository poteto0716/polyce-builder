# Getting started

1. Use Ubuntu 24.04 x86_64 and install `libc6 libstdc++6 libgcc-s1 python3`.
2. Clone the repository and read [LICENSE](../LICENSE).
3. Run `bin/polyce-build --help` from the repository root.
4. Follow [external data setup](external_data.md) for the examples you want.
5. Run `examples/polymer_pcff/homopolymer/run.sh` or enter that directory and run
   `./run.sh`. Scripts determine their own location, so the working directory
   used to launch them does not matter.

The first example writes `output/pmma10.data`. Run reports, chain sequences,
identity information and LAMMPS styles are placed in the same `output/` directory.
Repeating a script overwrites its generated files; save results elsewhere first
if you need them. No generated outputs are shipped with this repository.

For an optional LAMMPS energy evaluation, install LAMMPS with CLASS2 and MOLECULE:

```bash
cd examples/polymer_pcff/homopolymer/output
lmp -in ../in.check.lmp
```

For the silica interface, install IFF and LAMMPS with the additional KSPACE and
EXTRA-FIX features. `./run.sh` creates independent components;
`./run_lammps.sh` merges and runs a short simulation/analysis demonstration.
See the [interface README](../examples/interface_iff_pcff_silica/README.md) for
all stages and the difference between smoke and full run lengths.

If an example reports missing external files, follow its error message and the
setup document. If the executable reports `GLIBC` or `GLIBCXX` version errors,
use the supported Ubuntu version. LAMMPS errors name missing packages/styles;
install an appropriate LAMMPS build rather than changing the force-field styles.
