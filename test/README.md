# FRESCO Test Examples

This directory contains test input files and reference outputs for the FRESCO Quantum Studio GUI.

## Test Cases

### B1 - Elastic Scattering
**Directory**: `B1/`
**Input file**: `B1-example-el.in`
**Reaction**: p + Ni78 → p + Ni78 (elastic scattering)
**Energies**: 6.9, 11.0, 49.35 MeV (three energy points)
**Description**: Proton elastic scattering on Ni-78 with Coulomb and nuclear potentials

**Key features**:
- Multiple energy points
- Woods-Saxon optical potential
- Angular distribution from 0° to 180°
- Step size: hcm=0.0001 for high precision

**Output files**:
- `fort.201` - Elastic angular distributions for each energy
- `fort.16` - Cross sections
- `fort.7` - S-matrix elements
- `fort.45` - Phase shifts
- `fort.39` - Integrated cross sections vs energy

**Used as default preset in**: Elastic Scattering Form Builder

---

### B2 - Inelastic Scattering
**Directory**: `B2/`
**Input file**: `B2-example-inel2.in`
**Reaction**: α + 12C → α + 12C* (inelastic to 2+ state at 4.43 MeV)
**Energy**: 100.0 MeV
**Description**: Alpha particle inelastic scattering on C-12, exciting the first 2+ state

**Key features**:
- Two nuclear states (ground state + 2+ excited state)
- Multiple optical potentials including deformation potentials (type 11)
- Coupled-channels calculation
- Nuclear deformation coupling

**Output files**:
- `fort.201` - Elastic angular distribution
- `fort.202` - Inelastic angular distribution to 2+ state
- `fort.16` - Cross sections
- `fort.7` - S-matrix elements
- `fort.39` - Integrated cross sections

**Note**: The GUI uses a custom simplified preset for Inelastic Scattering Form Builder
(30 MeV Alpha + 12C with simpler potential setup)

---

### B5 - Transfer Reaction
**Directory**: `B5/`
**Input file**: `B5-example-tr.in`
**Reaction**: 14N(17F, 18Ne)13C @ 170 MeV
**Description**: Heavy ion transfer reaction with multiple partitions

**Key features**:
- **Two partitions** (entrance and exit channels):
  - Entrance: 17F + 14N (projectile + target, nex=2)
  - Exit: p + 41Ca (ejectile + residual, nex=1)
- **Multiple states**:
  - Entrance channel: 2 states (ground + excited)
  - Exit channel: 1 state
- **13 optical potentials** including:
  - Coulomb potentials for each partition
  - Woods-Saxon volume potentials
  - Spin-orbit potentials (type 3)
  - Binding potentials for transfer
- **2 OVERLAP definitions**:
  - kn1=1: KIND=0 (L,S coupling), l=2, be=3.922 MeV
  - kn1=2: KIND=3 (coupled core), l=1, be=7.551 MeV
- **1 COUPLING**: KIND=7 (finite-range transfer)

**Output files**:
- `fort.201` - Angular distribution (elastic/entrance channel)
- `fort.202` - Transfer angular distribution
- `fort.16` - Cross sections
- `fort.7` - S-matrix elements
- `fort.39` - Integrated cross sections

**Used as default preset in**: Transfer Reaction Form Builder

---

## File Formats

### FRESCO Output Files

Common FRESCO output files found in these directories:

- **fort.201**: Angular distributions (elastic or dominant channel)
- **fort.202**: Secondary channel angular distributions (inelastic/transfer)
- **fort.16**: Detailed cross section data
- **fort.7**: S-matrix elements
- **fort.39**: Integrated cross sections vs energy
- **fort.45**: Phase shifts
- **fort.3, fort.4**: Additional calculation data
- **fort.13**: Input echo

### Running Tests

To run these examples with FRESCO:

```bash
# Navigate to test directory
cd test/B1/  # or B2/ or B5/

# Run FRESCO
../../fresco_code/source/fresco < B1-example-el.in > B1.out

# View results
cat fort.201  # Angular distribution
```

### Using in GUI

These examples are automatically loaded as presets in the FRESCO Quantum Studio Form Builder:

1. Open FRESCO Quantum Studio
2. Go to "Form Builder" tab
3. Select calculation type (Elastic/Inelastic/Transfer)
4. Click "Load Preset Example" button

The form will be populated with the default example for that calculation type.

---

## References

- FRESCO Manual: `../fresco_code/man/`
- FRESCO Website: http://www.fresco.org.uk/
- GUI Documentation: `../CLAUDE.md`

---

## Contact

For questions about these examples or the GUI:
- Email: jinlei@fewbody.com
- GUI Repository: https://github.com/your-repo/fresco_gui
