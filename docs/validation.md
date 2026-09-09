# Binary validation

The public build was made with the project's existing CMake Release configuration,
GCC 13.3, C++23, `-O3 -DNDEBUG`, without sanitizer or debug flags. Build products
were kept outside the development and publication trees. Compiler path-prefix
mapping removed private source/build paths. Configure-time private Git revision
embedding was disabled. The compiled builder's physics, force-field assignment,
packing and periodic-boundary code were not modified.

Only `polyce-build` was copied to the distribution and stripped with
`strip --strip-all`. The binary is an x86_64 PIE ELF, requiring baseline x86-64 ISA.
It contains no `.debug*` sections or ordinary `.symtab`; `nm` reports no symbols.
ELF dynamic symbols needed by the system loader remain. `strings` found no private
home paths, development-project names or temporary build paths. No RPATH/RUNPATH
is present. This reduces incidental implementation information; it cannot make
reverse engineering impossible.

## Runtime

Test host: Ubuntu 24.04.3 LTS x86_64, Python 3.12.3. The tested separate LAMMPS
executable identifies itself as **30 Mar 2026 – Development**. Other LAMMPS
versions must supply the features documented in the interface example; they were
not independently validated here. No LAMMPS executable is distributed.

`ldd bin/polyce-build` resolves only:

- `libstdc++.so.6`
- `libm.so.6`
- `libgcc_s.so.1`
- `libc.so.6`
- `/lib64/ld-linux-x86-64.so.2` (plus the kernel-provided vDSO)

Required maximum symbol versions include GLIBC 2.38 and GLIBCXX 3.4.31.
Install Ubuntu's `libc6`, `libstdc++6`, `libgcc-s1`. No private shared library is
required or shipped. No `-march=native` optimization was used.

## Isolation and comparison method

The distribution was copied to a separate temporary directory. Excluded external
data were installed **only in that test copy**, using the documented installer.
A private Linux user/mount namespace replaced `/home` with an empty tmpfs, making
the development tree, installed personal libraries and original data inaccessible.
Tests used system utilities, the copied public binary, local external data and a
separately staged LAMMPS executable. No network was used to run the examples.

Both `--help` and `-h` returned 0. All four example launchers were also checked
without external data: they return 2 with the documented setup instruction.
Bash and Python syntax checks passed.

Nine existing tests passed: core, sequence, class-II fields, force-field-file
reading, LAMMPS I/O, structure import, image flags, periodic topology and system
sizing. They were run from the separate build directory. The full reference-corpus
script was not run against the original checkout because it writes results there.

Reference comparison uses the pre-existing development Release executable copied
to a separate test location, fed the same published inputs and external data.
Coordinates, topology, parameters, identities, sequences and styles are compared
byte-for-byte. Timing/host reports are excluded from byte comparison. The small
PMMA input also matches the existing PMMA reference's LAMMPS data byte-for-byte.
See [machine-readable results](validation_results.json) for checks and counts.

Generated LAMMPS data are checked for finite numeric values, header/section count
agreement, positive box dimensions and valid atom/topology IDs. Coordinates outside
periodic faces are allowed by LAMMPS; nonperiodic z coordinates are checked for
slab and interface outputs. Parameter reports must contain no MISSING terms/types
and no UNSUPPORTED entries. Polymer LAMMPS `run 0` energies are checked against
PolyCE for every reported family with relative tolerance 1e-6.

## Interpretation and excluded data

The short LAMMPS workflow is an execution/finite-energy smoke test. Full-duration
simulation, equilibration, convergence of material properties and peeling free
energies are not claimed. The input's full-duration mode is provided separately.
Force-field tables, structure coordinates, generated parameterized outputs,
logs and internal test code are not part of the release.

The development core sources, headers, application sources and CMake inputs
were checked against a pre-work hash inventory and remained unchanged. Concurrent
changes were observed in pre-existing reference results/logs and a reference runner;
this packaging task neither ran that runner nor restored or modified those files.

## Observed LAMMPS warnings

The smoke run emits image-flag warnings for the continuous silica network and
`No fixes with time integration` at intentional `run 0` evaluations. A continuous
periodic silica network has no globally consistent finite-molecule image flags;
the polymer's image flags are separately provided before unwrapping. Merge also
prints the generic warning about nonzero flags when growing a box. The merge
inputs retain identical x/y dimensions and the polymer slab has zero z image flags;
only free-z space is enlarged. These warnings were retained, not suppressed.
They do not constitute a failed run in these validated circumstances. Atom counts,
bonded topology, finite energies and free-z coordinate bounds were checked. A
new system or a changed periodic cell needs its own validation.

## Measured results

| Model/stage | Atoms | Bonds | Angles | Dihedrals | Impropers | Box lengths (Å) |
|---|---:|---:|---:|---:|---:|---|
| homopolymer | 158 | 157 | 292 | 389 | 178 | 11.486260 × 11.486260 × 11.486260 |
| block_copolymer | 388 | 398 | 720 | 1050 | 388 | 15.545824 × 15.545824 × 15.545824 |
| random_copolymer | 388 | 398 | 720 | 1050 | 388 | 15.545824 × 15.545824 × 15.545824 |
| substrate_slab | 2928 | 3736 | 7220 | 10704 | 3568 | 40.314800 × 41.432000 × 60.000000 |
| polymer_bulk | 6160 | 6140 | 11440 | 15380 | 6960 | 40.314800 × 41.432000 × 34.245854 |
| Interface final | 9088 | 9876 | 18660 | 26084 | 10528 | 40.314800 × 41.432000 × 167.294668 |

All three polymer examples and both interface components have exit code 0 and
byte-identical `.data`, `.in.styles`, `.identity` and `.chains.csv` compared with
the existing Release executable. The worst polymer family energy residual against
LAMMPS is **8.51e-11 relative**, below the 1e-6 acceptance threshold.

All five LAMMPS interface stages passed, including a complete rerun of
`./run_lammps.sh` after finalizing the inputs. The final model retains 9088 atoms
and 9876 bonds, with no atom loss. Surface/interface analysis produced 11 finite
samples (6 in the reported second-half average). The measured mean interaction
energy is approximately **-1.739806 kcal/mol** in this very short smoke run;
it is an execution-test result, not a converged material prediction.

No NaN/Infinity was found in numeric model records, parsed numeric thermo rows or
interaction samples. No source/object/debug files, build intermediates, development
logs, private configuration, source Git history, private paths or bundled external
force-field/structure data are present in the package.
