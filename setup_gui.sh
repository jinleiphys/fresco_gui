#!/bin/bash

# FRESCO Quantum Studio Setup Script
# This script sets up the conda environment, installs dependencies, and builds FRESCO

set -e  # Exit on error

echo "=================================================="
echo "  FRESCO Quantum Studio Setup Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_info "Working directory: $SCRIPT_DIR"
echo ""

# Step 0: Initialize conda for this script session
# This ensures conda-installed tools (like gfortran) are available
init_conda() {
    # Try common conda locations
    local CONDA_LOCATIONS=(
        "$HOME/miniconda3"
        "$HOME/anaconda3"
        "$HOME/miniforge3"
        "/opt/miniconda3"
        "/opt/anaconda3"
        "/opt/homebrew/Caskroom/miniconda/base"
        "/usr/local/miniconda3"
    )

    # First try conda info if conda command exists
    if command -v conda &> /dev/null; then
        CONDA_BASE=$(conda info --base 2>/dev/null)
        if [ -n "$CONDA_BASE" ] && [ -f "$CONDA_BASE/etc/profile.d/conda.sh" ]; then
            source "$CONDA_BASE/etc/profile.d/conda.sh"
            return 0
        fi
    fi

    # Otherwise search common locations
    for loc in "${CONDA_LOCATIONS[@]}"; do
        if [ -f "$loc/etc/profile.d/conda.sh" ]; then
            source "$loc/etc/profile.d/conda.sh"
            return 0
        fi
    done

    return 1
}

# Try to initialize conda early (for gfortran detection)
if init_conda; then
    print_info "Conda initialized for this session"
else
    print_warning "Could not initialize conda yet (will install if needed)"
fi
echo ""

# Step 1: Check and install conda if needed
print_info "Checking for conda installation..."
if ! command -v conda &> /dev/null; then
    print_warning "conda not found!"
    echo ""
    read -p "Do you want to install Miniconda? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing Miniconda..."

        # Detect OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if [[ $(uname -m) == "arm64" ]]; then
                MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
            else
                MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        else
            print_error "Unsupported operating system: $OSTYPE"
            exit 1
        fi

        # Download and install Miniconda
        TEMP_INSTALLER="/tmp/miniconda_installer.sh"
        print_info "Downloading Miniconda from $MINICONDA_URL..."
        curl -L -o "$TEMP_INSTALLER" "$MINICONDA_URL"

        print_info "Running Miniconda installer..."
        bash "$TEMP_INSTALLER" -b -p "$HOME/miniconda3"
        rm "$TEMP_INSTALLER"

        # Initialize conda
        print_info "Initializing conda..."
        "$HOME/miniconda3/bin/conda" init bash

        # Source conda for current session
        source "$HOME/miniconda3/etc/profile.d/conda.sh"

        print_success "Miniconda installed successfully!"
        print_warning "Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
    else
        print_error "conda is required to continue. Exiting."
        exit 1
    fi
else
    print_success "conda found: $(conda --version)"
fi
echo ""

# Step 2: Check and install gfortran if needed
print_info "Checking for Fortran compiler..."
if ! command -v gfortran &> /dev/null; then
    print_warning "gfortran not found!"
    echo ""
    read -p "Do you want to install gfortran? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing gfortran..."

        # Initialize conda if not already done
        if ! command -v conda &> /dev/null; then
            source "$HOME/miniconda3/etc/profile.d/conda.sh"
        fi

        # Install gfortran via conda
        print_info "Installing gfortran via conda-forge..."
        conda install -y -c conda-forge gfortran

        print_success "gfortran installed successfully!"
    else
        print_error "gfortran is required to compile FRESCO. Exiting."
        exit 1
    fi
else
    print_success "Fortran compiler found: $(gfortran --version | head -n 1)"
fi
echo ""

# Step 3: Create or update conda environment
ENV_NAME="fresco_gui"
print_info "Setting up conda environment: $ENV_NAME"

if conda env list | grep -q "^$ENV_NAME "; then
    print_warning "Environment $ENV_NAME already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing environment..."
        conda env remove -n $ENV_NAME -y
        print_info "Creating new environment..."
        conda create -n $ENV_NAME python=3.10 -y
    else
        print_info "Using existing environment"
    fi
else
    print_info "Creating new environment..."
    conda create -n $ENV_NAME python=3.10 -y
fi

print_success "Conda environment ready"
echo ""

# Step 4: Activate environment and install Python packages
print_info "Installing Python dependencies..."

# Get conda base path
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# Verify we're using the correct Python and pip
print_info "Using Python: $(which python)"
print_info "Using pip: $(which pip)"
print_info "Python version: $(python --version)"

# Check if pip is from conda environment (critical check!)
PIP_PATH=$(which pip)

# Smart detection: Check if pip is from the active conda environment
if [ -n "$CONDA_PREFIX" ]; then
    # If pip path contains the conda environment prefix, it's the correct pip
    if [[ "$PIP_PATH" == "$CONDA_PREFIX"* ]]; then
        print_success "pip is correctly from conda environment"
        PIP_CMD="pip"
    else
        print_warning "pip is NOT from the conda environment!"
        print_warning "  Conda environment: $CONDA_PREFIX"
        print_warning "  pip location: $PIP_PATH"
        print_info "Using 'python -m pip' instead to ensure correct environment"
        PIP_CMD="python -m pip"
    fi
else
    print_warning "CONDA_PREFIX not set, using 'python -m pip' for safety"
    PIP_CMD="python -m pip"
fi

# Install requirements
cd fresco_gui

# Upgrade pip first to avoid installation issues
print_info "Upgrading pip..."
$PIP_CMD install --upgrade pip

print_info "Installing requirements from requirements.txt..."
$PIP_CMD install -r requirements.txt

# Verify PySide6 installation
print_info "Verifying PySide6 installation..."
if python -c "import PySide6.QtWidgets; print('PySide6 version:', PySide6.__version__)" 2>/dev/null; then
    print_success "PySide6 installed and verified successfully"
else
    print_warning "PySide6 installation verification failed!"
    print_info "Attempting to reinstall PySide6 with verbose output..."

    # Try installing with verbose output to see what's wrong
    $PIP_CMD install --upgrade --force-reinstall --verbose PySide6>=6.5.0

    # Try again
    if python -c "import PySide6.QtWidgets; print('PySide6 version:', PySide6.__version__)" 2>/dev/null; then
        print_success "PySide6 reinstalled successfully"
    else
        print_error "Failed to install PySide6!"
        print_info "Diagnostic information:"
        echo "  Python executable: $(which python)"
        echo "  pip executable: $(which pip)"
        echo "  Python site-packages:"
        python -c "import site; print('  ', site.getsitepackages())"
        echo ""
        print_info "Trying alternative installation methods..."

        # Try conda installation as fallback
        print_info "Attempting conda installation of PySide6..."
        conda install -y -c conda-forge pyside6

        if python -c "import PySide6.QtWidgets" 2>/dev/null; then
            print_success "PySide6 installed via conda successfully"
        else
            print_error "All installation methods failed. Please try manually:"
            echo "  conda activate fresco_gui"
            echo "  pip install --upgrade pip"
            echo "  pip install PySide6"
            echo "  # OR try: conda install -c conda-forge pyside6"
            exit 1
        fi
    fi
fi

print_success "Python dependencies installed"
echo ""

# Step 5: Build FRESCO
print_info "Building FRESCO Fortran code..."
cd "$SCRIPT_DIR"

# Check if fresco_code exists
if [ ! -d "fresco_code" ]; then
    print_error "fresco_code directory not found!"
    print_info "Please ensure the FRESCO source code is in the fresco_code directory."
    exit 1
fi

# Build FRESCO
print_info "Building FRESCO main program..."
cd fresco_code/source

# Ensure gfortran is available for make
# gfortran might be in base conda env or system path, so we need to find it
GFORTRAN_PATH=""
if command -v gfortran &> /dev/null; then
    GFORTRAN_PATH=$(which gfortran)
else
    # Search common locations
    for gf_path in "/opt/miniconda3/bin/gfortran" "$HOME/miniconda3/bin/gfortran" \
                   "/opt/homebrew/bin/gfortran" "/usr/local/bin/gfortran" \
                   "$CONDA_BASE/bin/gfortran"; do
        if [ -x "$gf_path" ]; then
            GFORTRAN_PATH="$gf_path"
            break
        fi
    done
fi

if [ -z "$GFORTRAN_PATH" ]; then
    print_error "gfortran not found! Please install gfortran first."
    exit 1
fi

print_info "Using gfortran: $GFORTRAN_PATH"

# Add gfortran directory to PATH for make
export PATH="$(dirname "$GFORTRAN_PATH"):$PATH"

make clean 2>/dev/null || true
make

cd "$SCRIPT_DIR"
print_success "FRESCO compiled successfully"
echo ""

# Step 6: Create launcher script
print_info "Creating launcher script..."
cat > run_fresco_gui.sh << 'EOF'
#!/bin/bash

# FRESCO Quantum Studio Launcher Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get conda base path
CONDA_BASE=$(conda info --base 2>/dev/null)
if [ -z "$CONDA_BASE" ]; then
    echo "Error: conda not found!"
    exit 1
fi

# Activate environment
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate fresco_gui

# Launch GUI
cd "$SCRIPT_DIR/fresco_gui"
python main.py
EOF

chmod +x run_fresco_gui.sh
print_success "Launcher script created: run_fresco_gui.sh"
echo ""

# Step 7: Print completion message
echo "=================================================="
print_success "Setup completed successfully!"
echo "=================================================="
echo ""
echo "To run FRESCO Quantum Studio:"
echo ""
echo -e "  ${BLUE}Recommended - Use the launcher script:${NC}"
echo -e "    ${GREEN}./run_fresco_gui.sh${NC}"
echo ""
echo -e "  ${BLUE}Alternative - Manual launch:${NC}"
echo -e "    ${GREEN}conda activate $ENV_NAME${NC}"
echo -e "    ${GREEN}cd fresco_gui${NC}"
echo -e "    ${GREEN}python main.py${NC}"
echo ""
print_warning "IMPORTANT: You MUST activate the conda environment before running!"
echo -e "  ${RED}DON'T run:${NC} python main.py  (without activating environment)"
echo -e "  ${GREEN}DO run:${NC}    conda activate fresco_gui && cd fresco_gui && python main.py"
echo ""
print_info "The GUI provides:"
echo "  - Input file editor with syntax support"
echo "  - Real-time output monitoring"
echo "  - Integrated result plotting"
echo "  - Light and dark themes"
echo "  - File save/load functionality"
echo ""
print_info "For help and documentation, see fresco_gui/README.md"
print_info "Contact: jinl@tongji.edu.cn"
echo ""
