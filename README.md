# PolyCE — Polymer Construction Engine

**Molecular System Builder for Molecular Dynamics**

PolyCE constructs molecular starting structures from monomer SMILES, polymer
sequences and imported structures. It builds and packs chains, assigns force-field
parameters and charges, and writes topology and LAMMPS input data. This repository
distributes an optimized Linux executable, example inputs and runtime scripts.
PolyCE is proprietary; see [LICENSE](LICENSE) for permitted use and restrictions.

## Supported platform

Tested on **Ubuntu 24.04.3 LTS, Linux x86_64** with Python 3.12.
The executable needs `libc6`, `libstdc++6` and `libgcc-s1` (glibc >= 2.38,
GLIBCXX >= 3.4.31). Ubuntu 22.04 is not supported by this build. No compiler,
CMake, GPU, CUDA or development checkout is required.

LAMMPS is a separate dependency for simulation and interface merging/analysis.
The interface example needs CLASS2, KSPACE, MOLECULE and EXTRA-FIX functionality;
see its [README](examples/interface_iff_pcff_silica/README.md).

## Installation

Clone this repository using its GitHub **Code → HTTPS** URL:

```bash
git clone <repository-url> polyce-builder
cd polyce-builder
chmod +x bin/polyce-build
sudo apt-get install libc6 libstdc++6 libgcc-s1 python3
bin/polyce-build --help
sha256sum -c SHA256SUMS
```

**One-time external-data setup is required before the examples run.** PCFF/IFF
parameter databases and the IFF silica model are not bundled because their
redistribution permission has not been established. Obtain them from their owners,
review their terms and follow [external data setup](docs/external_data.md).
The setup helper verifies the exact files used for validation; it does not download
anything or grant permission to use third-party materials. After setup, the
examples run offline using paths entirely within this distribution.

## Quick start

After installing the PCFF files as described above:

```bash
cd examples/polymer_pcff/homopolymer
./run.sh
```

This builds a packed PMMA DP10 chain and prints `PASS` after basic data checks.
LAMMPS data is written to **`output/pmma10.data`**; the accompanying
`output/pmma10.in.styles` selects the styles and reads the data file.
The example is a small construction demonstration, not an equilibrated material.

## Examples

| Example | What it demonstrates |
|---|---|
| [PCFF homopolymer](examples/polymer_pcff/homopolymer/README.md) | PMMA, 10 repeat units, one chain |
| [PCFF block copolymer](examples/polymer_pcff/block_copolymer/README.md) | PMMA6-b-PS6, two chains |
| [PCFF random copolymer](examples/polymer_pcff/random_copolymer/README.md) | Six MMA and six styrene units per chain, shuffled reproducibly |
| [iFF-PCFF silica/polymer interface](examples/interface_iff_pcff_silica/README.md) | Imported silica + independently packed PMMA → LAMMPS merge → relaxation |
| [Surface/interface interaction analysis](examples/interface_iff_pcff_silica/README.md#surfaceinterface-interaction-analysis) | Pair + reciprocal group/group interaction energy and area normalization |

Each directory supplies `run.sh`, inputs and exact commands. The interface
`run.sh` builds the two components; `run_lammps.sh` performs the LAMMPS stages.

## CLI reference and documentation

```bash
bin/polyce-build --help
bin/polyce-build -h
bin/polyce-build path/to/build.polyce
bin/polyce-build path/to/build.polyce chains=2 seed=1234
```

See [getting started](docs/getting_started.md), [examples](docs/examples.md),
[CLI reference](docs/cli_reference.md), [validation](docs/validation.md) and
[third-party notices](THIRD_PARTY_LICENSES.md). Only `polyce-build` is distributed;
internal fixture and benchmark executables are excluded.

The repository contains no PolyCE C/C++ source, object files, build tree or debug
symbols. The small Python and shell files are necessary example execution,
external-data preparation and output checking scripts. They are covered by the
supplied binary software license along with the documentation and examples.
