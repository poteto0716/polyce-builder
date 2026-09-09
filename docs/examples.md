# Examples

Install external data first; see [setup](external_data.md). All lengths are Å,
energies kcal/mol, temperatures K and densities g/cm³ for these real-unit inputs.

| Directory below `examples/` | Model | Run |
|---|---|---|
| `polymer_pcff/homopolymer` | PMMA DP10, 1 chain, density 1.13 | `./run.sh` |
| `polymer_pcff/block_copolymer` | PMMA6-b-PS6, 2 chains, density 1.110 | `./run.sh` |
| `polymer_pcff/random_copolymer` | MMA/STY 50:50 exact, DP12, 2 chains | `./run.sh` |
| `interface_iff_pcff_silica` | Q3 amorphous silica + PMMA DP20 × 20 | `./run.sh`, then `./run_lammps.sh` |

The homopolymer retains the existing PMMA DP10 reference input. The copolymer
examples combine the existing PMMA/styrene monomer definitions, existing block
syntax and random-exact sequence syntax in small PCFF systems. The nominal
1.110 density is the existing PMMA/PS mixture estimate, not a measured copolymer
material property. Random-exact is a specified composition with a seeded shuffle,
not a kinetic polymerization model. All chains are packed by the unchanged
builder and use the database's typing templates and parameter assignment.

The interface retains the existing small bulk-first model. PolyCE constructs the
two components independently; LAMMPS relaxes the periodic polymer, unwraps its
molecules before removing z periodicity, merges by computed type offsets, relaxes
the interface and samples cross-interface interaction energy. IFF uses a single
PCFF-compatible class-II database for both components, with sixth-power mixing,
PPPM and the slab correction. No new force-field fit or interface mixing rule is
introduced.

The default LAMMPS smoke run reduces step counts, minimizer iteration budgets
and output sampling intervals. It checks execution and finite energies; it is
not an equilibrium or adhesion free-energy measurement. The full mode preserves
the existing input's full simulation/minimization defaults and was not run to
completion as part of the binary smoke validation.
