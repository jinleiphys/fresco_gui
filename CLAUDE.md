# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FRESCO Studio is a modern graphical user interface for FRESCO (Finite Range Extended Search Code for coupled reaction channels), a quantum scattering calculation program. The project consists of a Python/PySide6 GUI wrapper (`fresco_gui/`) and the underlying FRESCO Fortran code (`fresco_code/`).

## Development Setup

### Quick Start
```bash
# Automated setup (recommended)
chmod +x setup_gui.sh
./setup_gui.sh

# Run the application
./run_fresco_gui.sh
```

### Manual Setup
```bash
# Create and activate conda environment
conda create -n fresco_gui python=3.10
conda activate fresco_gui

# Install Python dependencies
cd fresco_gui
pip install -r requirements.txt

# Build FRESCO executable
cd ../fresco_code/source
make
```

### Running the Application
```bash
# Using launcher script
./run_fresco_gui.sh

# Manual launch
conda activate fresco_gui
cd fresco_gui
python main.py
```

## Architecture

### High-Level Structure

The application follows a **Qt Model-View architecture** with signal-slot communication:

```
MainWindow (fresco_gui/main_window.py)
├── InputPanel (input_panel.py)
│   ├── Text Editor Tab (QTextEdit - direct input editing)
│   └── Form Builder Tab (form_input_panel.py)
│       ├── ElasticScatteringForm
│       ├── InelasticScatteringForm
│       └── TransferReactionForm
│           ├── PotentialManagerWidget (pot_widget.py)
│           └── AdvancedParametersWidget (advanced_parameters_widget.py)
├── PlotWidget (plot_widget.py) - matplotlib integration
├── LogWidget (log_widget.py) - output monitoring
└── FrescoRunner (runner.py) - QProcess wrapper
```

### Key Design Patterns

1. **Dual Input System**: Users can either edit raw FRESCO input text OR use form-based builders that generate input text. The two systems are synchronized via Qt signals (`input_generated` signal).

2. **Dynamic Parameter System** (NEW): `parameter_manager.py` implements adaptive parameter categorization:
   - **Calculation-Type Defaults**: Different calculations (elastic, inelastic, transfer) have different default "General" parameters
   - **File-Based Promotion**: When loading an input file, parameters found in the file are automatically promoted from "Advanced" to "General"
   - **Auto-Detection**: Automatically detects calculation type from input file structure (counts &PARTITION, &COUPLING, &OVERLAP namelists)
   - **UI Synchronization**: `AdvancedParametersWidget` dynamically rebuilds to show only non-General parameters
   - **Conservation**: Total parameter count always equals General + Advanced (typically 43 total)

3. **Namelist Parameter System**: `fresco_namelist.py` defines ALL FRESCO parameters with metadata (tooltips, ranges, defaults, categories). This enables dynamic UI generation and validation. The `FrescoNamelist` class provides:
   - Parameter definitions organized by category (radial, partialWaves, angular, etc.)
   - Type information (number, text, select, checkbox)
   - Validation constraints (min/max/step)
   - Default values and calculation-type-specific defaults
   - Automatic namelist text generation

4. **POT Namelist Management**: `pot_namelist.py` and `pot_widget.py` implement a dynamic system for managing multiple optical potential definitions. Each potential type (Coulomb, Volume, Surface, etc.) has specific parameter sets.

5. **Path Resolution**: `path_utils.py` implements intelligent executable finding:
   - Searches environment variables (FRESCO_EXE)
   - Auto-detects repository structure
   - Falls back to PATH and common locations
   - Caches results for performance

6. **Process Management**: `runner.py` uses QProcess with merged channels for real-time output streaming. Input is written to stdin, allowing FRESCO to run interactively.

### Signal-Slot Communication

Critical signal flows:
- `FormInputPanel.input_generated → InputPanel.set_input_text`: Form generates text
- `FrescoRunner.output_ready → LogWidget.append_output`: Stream stdout
- `FrescoRunner.finished → MainWindow.on_calculation_finished`: Handle completion, load results

### Working Directory Semantics

The GUI maintains a `working_directory` concept:
- Set to input file's directory when opened/saved
- FRESCO runs in this directory (important for fort.* output files)
- PlotWidget loads results from this directory

## Common Development Tasks

### Building FRESCO
```bash
cd fresco_code/source
make clean  # Clean previous builds
make        # Build fresco executable
```

The Makefile in `fresco_code/source/` handles Fortran compilation. The executable `fresco` is created in the same directory.

### Testing GUI Changes
```bash
conda activate fresco_gui
cd fresco_gui
python main.py
```

Test input files are in `fresco_code/test/`.

### Working with Dynamic Parameter System

The dynamic parameter system adapts the UI based on calculation type and loaded files:

```python
# Create parameter manager for a specific calculation type
from parameter_manager import ParameterManager
pm = ParameterManager(calculation_type="elastic")

# Parse parameters from an input file
from parameter_manager import parse_fresco_input_parameters
file_params = parse_fresco_input_parameters(input_text)

# Update categorization based on file
pm.update_from_input_file(file_params)

# Get categorization summary
summary = pm.get_categorization_summary()
print(f"General: {summary['general_count']}, Advanced: {summary['advanced_count']}")
print(f"Promoted: {summary['promoted_params']}")
```

**How it works:**
- Default state: Shows calculation-type-specific General parameters (12-16 params)
- After loading file: Promotes file parameters to General section
- UI refreshes automatically via `AdvancedParametersWidget.refresh()` and `DynamicGeneralParametersWidget.refresh()`

### Complete File Loading System

The GUI now supports full parsing and loading of FRESCO input files:

**Supported Components:**
1. **FRESCO Namelist Parameters** - All parameters from &FRESCO namelist
2. **Partition Information** - Projectile/target names, masses, charges from &PARTITION
3. **Optical Potentials (POT)** - Multiple &POT namelists with parameter mapping

**POT Parameter Mapping:**
FRESCO uses array syntax `p(1:n)=` for potential parameters. The system maps these to named parameters based on potential type:
- **Type 0 (Coulomb)**: p1→ap (projectile mass), p2→at (target), p3→rc (radius)
- **Type 1 (Volume)**: p1→V, p2→r0, p3→a, p4→W, p5→r0W, p6→aW
- **Type 2 (Surface)**: Same as Volume
- **Type 3 (Spin-orbit)**: p1→Vso, p2→rso, p3→aso

**Example:**
```python
# Load complete input file
from form_input_panel import FormInputPanel
panel = FormInputPanel()
with open("input.in", "r") as f:
    input_text = f.read()

# Parse and populate all sections
panel.update_from_input_file(input_text)
# → Parameters updated in General/Advanced widgets
# → Partition info populated
# → POT components created and configured
```

### Adding New Form Parameters

When adding new FRESCO parameters to form builders:

1. Add parameter definition to `fresco_namelist.py`:
   ```python
   params["new_param"] = FrescoParameter(
       "new_param", "Display Label",
       "Tooltip description",
       default=1.0, step=0.1, minimum=0.0, maximum=10.0,
       category="appropriate_category"
   )
   ```

2. Optionally add to calculation-type defaults in `DEFAULT_GENERAL_PARAMS`:
   ```python
   DEFAULT_GENERAL_PARAMS = {
       "elastic": ["hcm", "rmatch", ..., "new_param"],  # If commonly used
       ...
   }
   ```

3. Add widget in form class (e.g., `ElasticScatteringForm`):
   ```python
   self.new_param = QDoubleSpinBox()
   self.new_param.setRange(0.0, 10.0)
   self.new_param.setValue(1.0)
   ```

4. Include in `generate_input()` method to output to namelist

### Adding New Potential Types

1. Add type definition to `POTNamelist.POTENTIAL_TYPES` in `pot_namelist.py`
2. Define parameters in `POTNamelist.PARAMETER_DEFINITIONS`
3. Widget automatically generates UI from definitions

### Theming and UI Design

Theme system in `styles.py` provides `apply_modern_style(widget, theme="light"|"dark")`. Custom widget styles use QObjectName matching:
- `runButton` - Green action button
- `stopButton` - Red stop button

**Modern UI Design (2024 Update):**
The GUI uses a unified, modern design system:
- **Color Palette**: Tailwind-inspired (#d1d5db borders, #374151 text, #007AFF accents)
- **Card-based Layout**: All major sections (General Parameters, Advanced Parameters, Optical Potentials) use rounded card design
- **Unified Title Style**: All GroupBox titles use consistent font (600 weight, 14px), padding (16px), and colors
- **Master-Detail Layout**: Advanced Parameters uses a two-panel layout with category buttons on the left and shared content display on the right
- **Grid Layouts**: POT parameters use compact grid layouts for space efficiency
- **Collapsible Sections**: All sections start collapsed to reduce visual clutter

**GroupBox Standard Style:**
```css
QGroupBox {
    font-weight: 600;
    font-size: 14px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    margin-top: 8px;
    padding: 16px;
    background-color: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 8px;
    background-color: white;
    color: #374151;
}
```

## File Locations and Conventions

### Important Paths
- GUI entry point: `fresco_gui/main.py`
- FRESCO executable: `fresco_code/source/fresco`
- Test inputs: `fresco_code/test/*.in`
- FRESCO output: `fort.16`, `fort.201`, `fort.202` (in working directory)

### Python Package Structure
All GUI code is in `fresco_gui/` as standalone modules (no `__init__.py`). Import using direct names:
```python
from input_panel import InputPanel
from runner import FrescoRunner
from parameter_manager import ParameterManager, parse_fresco_input_parameters, detect_calculation_type
```

### Key Files for Dynamic Parameters
- `parameter_manager.py` - Core dynamic parameter system
  - `ParameterManager` class: Manages General/Advanced categorization
  - `parse_fresco_input_parameters()`: Extracts parameters from &FRESCO namelist
  - `parse_partition_namelist()`: Extracts projectile/target information from &PARTITION
  - `parse_pot_namelists()`: Extracts optical potential definitions from &POT (supports FRESCO array syntax `p(1:n)=`)
  - `detect_calculation_type()`: Auto-detects elastic/inelastic/transfer from input structure
- `advanced_parameters_widget.py` - UI for Advanced parameters (master-detail layout with category buttons and shared content area, supports dynamic refresh)
- `dynamic_general_params_widget.py` - UI for General parameters (dynamically rebuilds based on categorization)
- `fresco_namelist.py` - Parameter definitions and DEFAULT_GENERAL_PARAMS
- `pot_widget.py` - Dynamic optical potential management (supports multiple potential components)
- `pot_namelist.py` - POT parameter definitions and type-specific mappings

### Output File Formats
FRESCO produces Fortran-style output files:
- `fort.16` - Cross sections
- `fort.201` - Angular distributions
- `fort.202` - Elastic cross sections
- Output parsed as space-separated float columns

## Testing

### Manual Testing
The GUI provides keyboard shortcuts for rapid iteration:
- `Ctrl+O` - Open test file
- `Ctrl+S` - Save
- `Ctrl+R` - Run FRESCO
- `Ctrl+.` - Stop calculation

Test workflow:
1. Load example from `fresco_code/test/`
2. Run calculation (monitor in Output Log tab)
3. View results (automatically switches to Plot tab)
4. Verify plots display correctly

### Common Issues
- **FRESCO not found**: Ensure `fresco_code/source/fresco` is built and executable
- **No plots after run**: Check working directory has fort.* files
- **Import errors**: Ensure conda environment is activated

## Code Style

- Follow PEP 8
- Use Qt signal/slot mechanism (not direct method calls between widgets)
- All user-facing messages go through LogWidget with severity levels:
  - `append_output()` - Normal stdout
  - `append_info()` - Informational (blue)
  - `append_warning()` - Warnings (yellow)
  - `append_error()` - Errors (red)
  - `append_success()` - Success (green)
- Keep theme compatibility (test both light and dark modes)

## FRESCO-Specific Knowledge

FRESCO input files use Fortran namelists (`&NAMELIST ... /`):
- `&FRESCO` - Global calculation parameters
- `&PARTITION` - Define particles (projectile/target or ejectile/residual)
- `&STATES` - Define quantum states
- `&POT` - Optical potential definitions
- `&COUPLING` - Channel coupling specifications
- `&OVERLAP` - Overlap functions for transfer reactions

Calculation types:
- **Elastic scattering**: Single partition, single state, optical potentials
- **Inelastic scattering**: Single partition, multiple states with couplings
- **Transfer reactions**: Multiple partitions (entrance/exit channels), overlap definitions

## Contact

- Project maintainer: jinlei@fewbody.com
- FRESCO documentation: `fresco_code/man/`
