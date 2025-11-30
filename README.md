# FRESCO Studio

Modern graphical user interface for FRESCO coupled channels calculations.

**Coupled Channels Calculations for Direct Nuclear Reactions**

[中文说明](README_CN.md)

---

## Features

### Dual Input Modes
- **Interactive Wizard**: Step-by-step guided input for all reaction types
  - Elastic scattering
  - Inelastic scattering
  - Transfer reactions (with automatic quantum number setup)
- **Text Editor**: Full-featured editor for direct FRESCO input file editing

### Reaction Support
- **Elastic Scattering**: Simple projectile-target reactions with optical potentials
- **Inelastic Scattering**: Excited states with coupling definitions
- **Transfer Reactions**: Complete support including:
  - Automatic binding energy lookup (deuteron, triton, 3He, alpha)
  - Shell-model quantum numbers (p-shell, sd-shell)
  - Proper parity assignments from nuclear database
  - 5 potential sets (entrance, exit, projectile binding, residual binding, remnant)
  - Overlap functions and coupling configurations

### Visualization & Output
- **Real-time Plotting**: Visualization of cross sections and angular distributions
- **Output Log**: Color-coded log with real-time FRESCO output monitoring
- **Modern Design**: Clean interface with light and dark theme support

### Nuclear Database
- Automatic mass lookup from AME2020 atomic mass evaluation
- Ground state spins and parities for common nuclei
- Separation energies for transfer reaction binding

## Screenshots

The GUI features a split-panel layout:
- Left panel: Wizard interface or text editor
- Right panel: Results plotting and output logs

## Installation

### Step 0: Prerequisites

Before installing FRESCO Studio, you need:

1. **A computer running macOS or Linux** (Windows users can use WSL)
2. **Anaconda or Miniconda** - for Python environment management
3. **A Fortran compiler** - for building FRESCO

#### Installing Anaconda/Miniconda (if you don't have it)

**macOS:**
```bash
# Download and install Miniconda (lightweight version)
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
bash Miniconda3-latest-MacOSX-arm64.sh
# Follow the prompts, say "yes" to initialize conda
# Then restart your terminal
```

**Linux:**
```bash
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# Follow the prompts, say "yes" to initialize conda
# Then restart your terminal
```

#### Installing a Fortran Compiler

**macOS:**
```bash
# Install Homebrew first if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install gfortran
brew install gcc
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install gfortran
```

---

### Step 1: Download the Code

#### Option A: Download ZIP (Easiest - No Git Required)

1. Go to: https://github.com/jinleiphys/fresco_gui
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file to a folder (e.g., your Desktop or Documents)
5. Open Terminal and navigate to the folder:
   ```bash
   cd ~/Desktop/fresco_gui-main
   # or wherever you extracted it
   ```

#### Option B: Using Git (Recommended)

If you have Git installed:
```bash
cd ~  # Go to your home directory
git clone https://github.com/jinleiphys/fresco_gui.git
cd fresco_gui
```

---

### Step 2: Run the Setup Script (Recommended)

Once you're in the fresco_gui folder, run:

```bash
chmod +x setup_gui.sh
./setup_gui.sh
```

This script will automatically:
1. Create a conda environment named `fresco_gui`
2. Install all Python dependencies
3. Build the FRESCO Fortran code
4. Set up everything for immediate use

**Wait for the script to complete** (it may take a few minutes).

---

### Step 3: Run FRESCO Studio

After setup is complete:

```bash
./run_fresco_gui.sh
```

The GUI should now open!

---

### Manual Setup (Alternative)

If the automatic setup doesn't work, you can set up manually:

**1. Create and activate conda environment:**
```bash
conda create -n fresco_gui python=3.10
conda activate fresco_gui
```

**2. Install Python dependencies:**
```bash
cd fresco_gui
pip install -r requirements.txt
```

**3. Build FRESCO:**
```bash
cd ../fresco_code/source
make
```

**4. Run the GUI:**
```bash
cd ../../fresco_gui
python main.py
```

---

### Updating FRESCO Studio

To get the latest version:

**If you used Git:**
```bash
cd fresco_gui
git pull
```

**If you downloaded ZIP:**
Download the new ZIP and replace the old folder.

## Usage

### Running the GUI

```bash
# Using the launcher script (recommended)
./run_fresco_gui.sh

# Or manually
conda activate fresco_gui
cd fresco_gui
python main.py
```

### Using the Wizard

1. **Reaction Setup**:
   - Enter reaction equation (e.g., `c12(d,p)c13` for transfer, `p+ni58` for elastic)
   - Set beam energy
   - The wizard automatically detects reaction type

2. **Particle Configuration**:
   - Review/modify particle properties (masses, spins, parities)
   - Values are pre-filled from the nuclear database

3. **Potentials** (for elastic/inelastic):
   - Configure optical potentials
   - Add multiple potential components (Coulomb, volume, surface, spin-orbit)

4. **Transfer-specific Steps**:
   - **Exit Channel**: Configure ejectile and residual nucleus
   - **Overlap Functions**: Set binding energies and spectroscopic factors
   - Quantum numbers are auto-calculated from shell model

5. **Generate & Run**:
   - Review generated input
   - Run FRESCO calculation
   - View results in plot panel

### Using the Text Editor

1. **Input Parameters**:
   - Create a new input file or load an existing one (File → Open)
   - Edit the FRESCO input directly
   - Use "Show Example" button to see sample inputs

2. **Run Calculation**:
   - Save your input file (File → Save)
   - Click "Run" or press Ctrl+R
   - Monitor progress in the Output Log tab

3. **View Results**:
   - Switch to the Plot tab
   - Choose plot types from dropdown
   - Use matplotlib toolbar for zoom/pan/save

### Keyboard Shortcuts

- `Ctrl+N`: New file
- `Ctrl+O`: Open file
- `Ctrl+S`: Save file
- `Ctrl+R`: Run FRESCO
- `Ctrl+.`: Stop calculation
- `Ctrl+Q`: Quit application

## Themes

The GUI supports both light and dark themes:
- Switch themes via View → Theme menu
- Light theme: Clean, bright interface (default)
- Dark theme: Easy on the eyes for extended use

## Requirements

- Python 3.8 or higher
- PySide6 (Qt for Python)
- matplotlib
- numpy
- scipy (optional)
- FRESCO compiled executable

## Project Structure

```
fresco_gui/
├── main.py                    # Application entry point
├── main_window.py             # Main window and menu/toolbar
├── input_panel.py             # Input panel with wizard/editor tabs
├── wizard_controller.py       # Wizard flow controller
├── wizard_navigator.py        # Step navigation and progress
├── wizard_step_widget.py      # Base wizard step widget
├── wizard_steps/              # Individual wizard steps
│   ├── reaction_input_step.py
│   ├── particle_config_step.py
│   ├── potential_setup_step.py
│   ├── exit_channel_step.py
│   ├── overlap_step.py
│   └── review_step.py
├── reaction_parser.py         # Reaction equation parser
├── mass_database.py           # Nuclear mass/spin/parity database
├── plot_widget.py             # Matplotlib plotting widget
├── log_widget.py              # Output log display
├── runner.py                  # FRESCO execution handler
├── fresco_namelist.py         # FRESCO parameter definitions
├── pot_namelist.py            # Potential parameter definitions
├── styles.py                  # Theme definitions
├── path_utils.py              # Path detection utilities
└── requirements.txt           # Python dependencies
```

## Troubleshooting

### FRESCO executable not found

If you see an error about the FRESCO executable:
1. Ensure FRESCO is built: `cd fresco_code/source && make`
2. Check the executable path in the error message
3. You can set the FRESCO_EXE environment variable to point to your executable

### Import errors

If you encounter import errors:
```bash
conda activate fresco_gui
pip install --upgrade -r requirements.txt
```

### GUI doesn't start

On macOS, you may need to install system dependencies:
```bash
brew install qt6
```

## Development

### Contributing

To contribute to the GUI:
1. Follow PEP 8 style guidelines
2. Use Qt's signal/slot mechanism for inter-widget communication
3. Maintain compatibility with both light and dark themes
4. Test on multiple platforms when possible

### Adding New Reaction Types

1. Add step classes in `wizard_steps/`
2. Register steps in `wizard_controller.py`
3. Implement input generation in `_generate_*_input()` methods

### Extending the Nuclear Database

Add entries to `mass_database.py`:
- `DEFAULT_SPINS` for ground state spins
- `DEFAULT_PARITIES` for ground state parities
- Mass data is loaded from AME2020

## License

This GUI is part of the FRESCO project and follows the same license.

## Support

For issues or questions:
- Contact: jinl@tongji.edu.cn
- Visit the FRESCO documentation in fresco_code/man

## Credits

Built with:
- PySide6 (Qt for Python)
- matplotlib for scientific plotting
- AME2020 atomic mass evaluation data
