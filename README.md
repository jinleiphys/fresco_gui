# FRESCO Studio

Modern graphical user interface for FRESCO coupled channels calculations.

## Features

- **Input Editor**: Full-featured text editor for FRESCO input files with syntax support
- **Plotting Area**: Real-time visualization of calculation results with multiple plot types
- **Output Log**: Color-coded log display with real-time monitoring of FRESCO output
- **Modern Design**: Beautiful, responsive interface with light and dark theme support
- **File Operations**: Load/save input files, export results
- **Integrated Execution**: Run FRESCO directly from the GUI with real-time feedback

## Screenshots

The GUI features a split-panel layout:
- Left panel: Input file editor
- Right panel: Results plotting and output logs

## Installation

### Quick Setup (Recommended)

Run the automated setup script:

```bash
cd /path/to/fresco_gui
chmod +x setup_gui.sh
./setup_gui.sh
```

This script will:
1. Create a conda environment named `fresco_gui`
2. Install all Python dependencies
3. Build the FRESCO Fortran code
4. Set up the environment for immediate use

### Manual Setup

1. **Create conda environment**:
```bash
conda create -n fresco_gui python=3.10
conda activate fresco_gui
```

2. **Install Python dependencies**:
```bash
cd fresco_gui
pip install -r requirements.txt
```

3. **Build FRESCO**:
```bash
cd ../fresco_code/source
make
```

## Usage

### Running the GUI

```bash
# Activate the environment
conda activate fresco_gui

# Navigate to GUI directory
cd fresco_gui

# Launch the application
python main.py
```

### Or use the launcher script

```bash
./run_fresco_gui.sh
```

### Using the Application

1. **Input Parameters**:
   - Create a new input file or load an existing one (File → Open)
   - Edit the FRESCO input in the text editor
   - Use "Show Example" button to see a sample input file

2. **Run Calculation**:
   - Save your input file (File → Save)
   - Click the "Run" button in the toolbar or press Ctrl+R
   - Monitor progress in the Output Log tab
   - Results will automatically appear in the Plot tab when complete

3. **View Results**:
   - Switch to the Plot tab to visualize results
   - Choose different plot types from the dropdown menu
   - Use the matplotlib toolbar to zoom, pan, and save plots

4. **Save/Load**:
   - Save current inputs: File → Save (Ctrl+S)
   - Load previous inputs: File → Open (Ctrl+O)
   - Export plots using the matplotlib toolbar

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

### Project Structure

```
fresco_gui/
├── main.py              # Application entry point
├── main_window.py       # Main window and menu/toolbar
├── input_panel.py       # Input file editor
├── plot_widget.py       # Matplotlib plotting widget
├── log_widget.py        # Output log display
├── runner.py            # FRESCO execution handler
├── styles.py            # Theme definitions
├── path_utils.py        # Path detection utilities
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Contributing

To contribute to the GUI:
1. Follow PEP 8 style guidelines
2. Use Qt's signal/slot mechanism for inter-widget communication
3. Maintain compatibility with both light and dark themes
4. Test on multiple platforms when possible

## License

This GUI is part of the FRESCO project and follows the same license.

## Support

For issues or questions:
- Contact: jinlei@fewbody.com
- Visit the FRESCO documentation in fresco_code/man

## Credits

Built with:
- PySide6 (Qt for Python)
- matplotlib for scientific plotting
- Modern design inspired by macOS and web interfaces

**FRESCO Studio** - A modern interface for quantum coupled channels calculations

© 2024 FRESCO Team
