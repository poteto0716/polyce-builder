# External data setup

The force-field databases and silica coordinates are **not included** in this
repository. Public availability does not establish redistribution permission.
Obtain the files directly from their owners, check the terms applicable to your
use, then run the commands below from the repository root. No EMC executable is
used or linked by PolyCE.

## PCFF polymer examples

Obtain the EMC distribution from the
[author's download page](https://montecarlo.sourceforge.net/emc/Welcome.html) or
[official file listing](https://sourceforge.net/projects/montecarlo/files/).
The validated files in the official `emc_linux_x86_64_v9.4.4_20260701.tgz`
archive are under `v9.4.4/field/cff/pcff/` (some older/local installations
expose them as `field/pcff/`):

- `pcff.frc` (header includes version 5.1, 1 December 2020)
- `pcff_templates.dat`

After unpacking the distribution, pass the directory containing these two files:

```bash
python3 scripts/external_data.py pcff /path/to/v9.4.4/field/cff/pcff
```

The official archive was downloaded during package validation and both database
files matched the pinned hashes. This copies only the two checksum-verified files into `external/pcff/` for your
local use. The absolute path above is your one-time installation input; example
configurations use only relative paths within this repository.

The inspected EMC installation includes GPLv3 license text, while its SourceForge
project metadata labels the project MIT. Neither observation by itself establishes
rights to redistribute the separately sourced historical PCFF database. No PCFF
parameters or templates are included in this release, and no license is inferred.

## IFF silica/polymer interface

Use the [official INTERFACE MD page](https://bionanostructures.com/interface-md/)
and its release 1.5 link, also referenced by the
[authors' repository](https://github.com/hendrikheinz/INTERFACE-force-field-and-surface-models).
The exact archive used for validation is
[interface_ff_1_5.zip](https://bionanostructures.com/wp-content/uploads/2016/02/interface_ff_1_5.zip).

After obtaining that archive:

```bash
python3 scripts/external_data.py iff /path/to/interface_ff_1_5.zip
```

Archive SHA-256:

```text
42b26c36ee91254eb83b2e87f8ac4dd8258dd59b4d7aa966c5fd8123410a2086
```

Only these four archive members are installed under `external/iff/`:

| Archive member below `INTERFACE_FF_1_5/` | Installed filename |
|---|---|
| `FORCE_FIELDS/pcff_interface_v1_5.frc` | `pcff_interface_v1_5.frc` |
| `FORCE_FIELDS/pcff_interface_v1_5_templates.dat` | `pcff_interface_v1_5_templates.dat` |
| `MODEL_DATABASE/SILICA/silica_Q3_amorph_4_7OH_0pct_ion.car` | `silica.car` |
| `MODEL_DATABASE/SILICA/silica_Q3_amorph_4_7OH_0pct_ion.mdf` | `silica.mdf` |

The example converts the CAR/MDF pair to MOL2 locally. It wraps x/y and shifts z
by 2 Å while retaining the supplied types, charges and bond graph. Its conversion
report checks that minimum-image bond lengths have not changed. Generated MOL2,
LAMMPS files containing these parameters, and external data are excluded from
version control; they are not redistributed with the package.

## Verification and citations

```bash
python3 scripts/external_data.py verify pcff
python3 scripts/external_data.py verify iff
```

Individual hashes are in `scripts/external_checksums.json`. A mismatch is refused;
a newer file requires a separate validation, not disabling the checksum.

For IFF cite H. Heinz, T.-J. Lin, R. K. Mishra, F. S. Emami,
*Langmuir* 2013, 29, 1754, [DOI](https://doi.org/10.1021/la3038846).
For the silica models cite F. S. Emami et al., *Chem. Mater.* 2014, 26, 2647,
[DOI](https://doi.org/10.1021/cm500365c).
Consult the PCFF database's reference records for the original parameter sources.

The external-data directory must remain local. `.gitignore` is a convenience,
not a redistribution license; do not force-add these files or package them in a
release archive.
