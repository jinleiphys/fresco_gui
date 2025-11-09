"""
Plot widget for displaying FRESCO results using matplotlib
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QCheckBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import os
import re


class PlotWidget(QWidget):
    """Widget for plotting FRESCO results"""

    def __init__(self):
        super().__init__()
        self.current_data = {}
        self.working_directory = None  # Store working directory for refresh
        self.calculation_type = "elastic"  # Track calculation type (elastic/inelastic/transfer)
        self.energy_datasets = []  # Store multiple energy datasets from fort.201
        self.energy_datasets_202 = []  # Store multiple energy datasets from fort.202 (inelastic/transfer)
        self.smatrix_datasets = []  # Store S-matrix datasets from fort.7
        self.phaseshift_datasets = []  # Store phase shift datasets from fort.45
        self.init_ui()

    def init_ui(self):
        """Initialize the plot widget"""
        layout = QVBoxLayout(self)

        # Control panel
        control_layout = QHBoxLayout()

        self.plot_type = QComboBox()
        self.plot_type.addItems([
            "Elastic Scattering",
            "Cross Section vs Energy",
            "Phase Shifts",
            "S-Matrix Elements"
        ])
        self.plot_type.currentIndexChanged.connect(self.update_plot)
        control_layout.addWidget(QLabel("Plot Type:"))
        control_layout.addWidget(self.plot_type)

        # Energy selector for multi-energy datasets
        control_layout.addWidget(QLabel("Energy:"))
        self.energy_selector = QComboBox()
        self.energy_selector.currentIndexChanged.connect(self.update_plot)
        control_layout.addWidget(self.energy_selector)

        # Show all energies checkbox
        self.show_all_energies = QCheckBox("Show All")
        self.show_all_energies.setChecked(True)
        self.show_all_energies.stateChanged.connect(self.update_plot)
        control_layout.addWidget(self.show_all_energies)

        control_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_results)
        control_layout.addWidget(refresh_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_plot)
        control_layout.addWidget(clear_btn)

        layout.addLayout(control_layout)

        # Matplotlib figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Initial plot
        self.clear_plot()

    def set_calculation_type(self, calc_type):
        """Set the calculation type and update plot type labels"""
        self.calculation_type = calc_type
        self.update_plot_type_labels()

    def update_plot_type_labels(self):
        """Update plot type labels based on calculation type"""
        current_selection = self.plot_type.currentIndex()

        # Update the second plot type based on calculation type
        self.plot_type.blockSignals(True)  # Prevent triggering update_plot

        if self.calculation_type == "elastic":
            self.plot_type.setItemText(0, "Elastic Scattering")
        elif self.calculation_type == "inelastic":
            self.plot_type.setItemText(0, "Inelastic Scattering")
        elif self.calculation_type == "transfer":
            self.plot_type.setItemText(0, "Transfer Reaction")
        else:
            self.plot_type.setItemText(0, "Angular Distribution")

        self.plot_type.setCurrentIndex(current_selection)
        self.plot_type.blockSignals(False)

    def load_results(self, working_dir=None, calc_type=None):
        """Load results from FRESCO output files"""
        try:
            # Update calculation type if provided
            if calc_type is not None:
                self.set_calculation_type(calc_type)

            # Store working directory for future refreshes
            if working_dir is not None:
                self.working_directory = working_dir

            # Use stored working directory if available
            if self.working_directory is None:
                self.working_directory = os.getcwd()

            # Try to read common FRESCO output files
            # fort.16 - cross sections
            # fort.201 - angular distributions (may contain multiple energies)
            # fort.202 - elastic cross sections

            fort16 = os.path.join(self.working_directory, 'fort.16')
            if os.path.exists(fort16):
                data = self.read_fort_file(fort16)
                self.current_data['fort16'] = data

            fort201 = os.path.join(self.working_directory, 'fort.201')
            if os.path.exists(fort201):
                # Read multi-energy datasets
                self.energy_datasets = self.read_fort201_multi_energy(fort201)
                # Also keep single dataset for backward compatibility
                if self.energy_datasets:
                    self.current_data['fort201'] = self.energy_datasets[0]['data']

                # Update energy selector
                self.energy_selector.clear()
                for dataset in self.energy_datasets:
                    energy = dataset['energy']
                    self.energy_selector.addItem(f"{energy:.4f} MeV")

            fort202 = os.path.join(self.working_directory, 'fort.202')
            if os.path.exists(fort202):
                # Read multi-energy datasets for inelastic/transfer
                self.energy_datasets_202 = self.read_fort201_multi_energy(fort202)
                # Also keep single dataset for backward compatibility
                if self.energy_datasets_202:
                    self.current_data['fort202'] = self.energy_datasets_202[0]['data']

            # Read integrated cross sections from fort.39
            fort39 = os.path.join(self.working_directory, 'fort.39')
            if os.path.exists(fort39):
                data = self.read_fort_file(fort39)
                self.current_data['fort39'] = data

            # Read S-matrix data from fort.7
            fort7 = os.path.join(self.working_directory, 'fort.7')
            if os.path.exists(fort7):
                self.smatrix_datasets = self.read_fort7_smatrix(fort7)

            # Read phase shift data from fort.45
            fort45 = os.path.join(self.working_directory, 'fort.45')
            if os.path.exists(fort45):
                self.phaseshift_datasets = self.read_fort45_phaseshift(fort45)

            self.update_plot()

        except Exception as e:
            print(f"Error loading results: {e}")

    def read_fort201_multi_energy(self, filename):
        """
        Read fort.201 file with multiple energy datasets

        Returns:
            List of dicts, each containing:
                - 'energy': float (lab energy in MeV)
                - 'data': numpy array (angle, cross section columns)
        """
        datasets = []

        with open(filename, 'r') as f:
            lines = f.readlines()

        current_energy = None
        current_data = []

        for line in lines:
            line_stripped = line.strip()

            # Check for energy label
            energy_match = re.search(r'Lab energy\s*=\s*([\d.]+)', line)
            if energy_match:
                # Save previous dataset if exists
                if current_energy is not None and current_data:
                    datasets.append({
                        'energy': current_energy,
                        'data': np.array(current_data)
                    })
                    current_data = []

                # Start new dataset
                current_energy = float(energy_match.group(1))
                continue

            # Check for END marker (end of current dataset)
            if line_stripped == 'END' or line_stripped == '&':
                if current_energy is not None and current_data:
                    datasets.append({
                        'energy': current_energy,
                        'data': np.array(current_data)
                    })
                    current_data = []
                    current_energy = None
                continue

            # Skip comment and directive lines
            if (line_stripped.startswith('#') or
                line_stripped.startswith('@') or
                line_stripped.startswith('!') or
                not line_stripped):
                continue

            # Try to parse data line
            try:
                values = [float(x) for x in line_stripped.split()]
                if len(values) >= 2:  # At least angle and cross section
                    current_data.append(values)
            except ValueError:
                continue

        # Save last dataset if exists
        if current_energy is not None and current_data:
            datasets.append({
                'energy': current_energy,
                'data': np.array(current_data)
            })

        return datasets

    def read_fort7_smatrix(self, filename):
        """
        Read fort.7 S-matrix file with multiple energy datasets

        Returns:
            List of dicts, each containing:
                - 'energy_index': int (energy dataset index, 0-based)
                - 'J': numpy array (total angular momentum values)
                - 'S_magnitude': numpy array (|S| = sqrt(Re^2 + Im^2))
                - 'Re': numpy array (real part)
                - 'Im': numpy array (imaginary part)
                - 'L': numpy array (orbital angular momentum)
        """
        datasets = []

        with open(filename, 'r') as f:
            lines = f.readlines()

        current_dataset = {
            'J': [],
            'S_magnitude': [],
            'Re': [],
            'Im': [],
            'L': []
        }
        energy_index = 0
        prev_j = -1

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # Parse data: Re(S) Im(S) L J JT
            parts = line_stripped.split(':')[0].strip().split()
            if len(parts) >= 5:
                try:
                    re_s = float(parts[0])
                    im_s = float(parts[1])
                    L = float(parts[2])
                    J = float(parts[3])

                    # Detect new energy dataset (J resets to 0 or lower value)
                    if J <= prev_j and current_dataset['J']:
                        # Save previous dataset
                        datasets.append({
                            'energy_index': energy_index,
                            'J': np.array(current_dataset['J']),
                            'S_magnitude': np.array(current_dataset['S_magnitude']),
                            'Re': np.array(current_dataset['Re']),
                            'Im': np.array(current_dataset['Im']),
                            'L': np.array(current_dataset['L'])
                        })
                        # Start new dataset
                        current_dataset = {
                            'J': [],
                            'S_magnitude': [],
                            'Re': [],
                            'Im': [],
                            'L': []
                        }
                        energy_index += 1

                    # Calculate |S|
                    s_mag = np.sqrt(re_s**2 + im_s**2)

                    # Append to current dataset
                    current_dataset['J'].append(J)
                    current_dataset['S_magnitude'].append(s_mag)
                    current_dataset['Re'].append(re_s)
                    current_dataset['Im'].append(im_s)
                    current_dataset['L'].append(L)

                    prev_j = J

                except ValueError:
                    continue

        # Save last dataset
        if current_dataset['J']:
            datasets.append({
                'energy_index': energy_index,
                'J': np.array(current_dataset['J']),
                'S_magnitude': np.array(current_dataset['S_magnitude']),
                'Re': np.array(current_dataset['Re']),
                'Im': np.array(current_dataset['Im']),
                'L': np.array(current_dataset['L'])
            })

        return datasets

    def read_fort45_phaseshift(self, filename):
        """
        Read fort.45 phase shift file with multiple energy datasets

        Returns:
            List of dicts, each containing:
                - 'energy': float (CM energy in MeV)
                - 'J': numpy array (total angular momentum values)
                - 'L': numpy array (orbital angular momentum)
                - 'phase1': numpy array (phase shift 1, possibly Coulomb)
                - 'phase2': numpy array (phase shift 2, possibly nuclear)
        """
        datasets = []

        with open(filename, 'r') as f:
            lines = f.readlines()

        current_dataset = {
            'J': [],
            'L': [],
            'phase1': [],
            'phase2': []
        }
        current_energy = None
        prev_l = -1

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # Parse data: energy phase1 phase2 for LJin = L J
            parts = line_stripped.split()
            if len(parts) >= 8 and 'for' in line_stripped and 'LJin' in line_stripped:
                try:
                    energy = float(parts[0])
                    phase1 = float(parts[1])
                    phase2 = float(parts[2])
                    L = float(parts[6])  # parts: [energy, p1, p2, 'for', 'LJin', '=', L, J]
                    J = float(parts[7])

                    # Detect new energy dataset (L resets to 0 or lower value)
                    if L <= prev_l and current_dataset['J']:
                        # Save previous dataset
                        datasets.append({
                            'energy': current_energy,
                            'J': np.array(current_dataset['J']),
                            'L': np.array(current_dataset['L']),
                            'phase1': np.array(current_dataset['phase1']),
                            'phase2': np.array(current_dataset['phase2'])
                        })
                        # Start new dataset
                        current_dataset = {
                            'J': [],
                            'L': [],
                            'phase1': [],
                            'phase2': []
                        }

                    # Store energy
                    current_energy = energy

                    # Append to current dataset
                    current_dataset['J'].append(J)
                    current_dataset['L'].append(L)
                    current_dataset['phase1'].append(phase1)
                    current_dataset['phase2'].append(phase2)

                    prev_l = L

                except (ValueError, IndexError):
                    continue

        # Save last dataset
        if current_dataset['J']:
            datasets.append({
                'energy': current_energy,
                'J': np.array(current_dataset['J']),
                'L': np.array(current_dataset['L']),
                'phase1': np.array(current_dataset['phase1']),
                'phase2': np.array(current_dataset['phase2'])
            })

        return datasets

    def read_fort_file(self, filename):
        """Read a FORTRAN output file"""
        try:
            data = np.loadtxt(filename)
            return data
        except:
            # Try reading with more flexible parsing
            with open(filename, 'r') as f:
                lines = f.readlines()

            data_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('!'):
                    try:
                        values = [float(x) for x in line.split()]
                        if values:
                            data_lines.append(values)
                    except:
                        continue

            if data_lines:
                return np.array(data_lines)
            return None

    def update_plot(self):
        """Update the plot based on selected type"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        plot_idx = self.plot_type.currentIndex()

        if plot_idx == 0:  # Elastic Scattering
            self.plot_angular_distribution(ax)
        elif plot_idx == 1:  # Cross Section vs Energy
            self.plot_energy_distribution(ax)
        elif plot_idx == 2:  # Phase Shifts
            self.plot_phaseshift(ax)
        elif plot_idx == 3:  # S-Matrix Elements
            self.plot_smatrix(ax)

        self.canvas.draw()

    def plot_angular_distribution(self, ax):
        """Plot angular distribution from fort.201 (supports multiple energies)"""
        # Always use fort.201 for all calculation types
        datasets = self.energy_datasets
        source_file = 'fort.201'

        # Set title prefix based on calculation type
        if self.calculation_type == "elastic":
            title_prefix = 'Elastic Scattering'
        elif self.calculation_type == "inelastic":
            title_prefix = 'Inelastic Scattering'
        else:  # transfer
            title_prefix = 'Transfer Reaction'

        if not datasets:
            self._show_no_data(ax, source_file)
            return

        # Color cycle for different energies
        colors = plt.cm.tab10(np.linspace(0, 1, 10))

        if self.show_all_energies.isChecked():
            # Plot all energies
            for i, dataset in enumerate(datasets):
                energy = dataset['energy']
                data = dataset['data']
                if data is not None and len(data.shape) >= 2 and data.shape[1] >= 2:
                    color = colors[i % len(colors)]
                    ax.plot(data[:, 0], data[:, 1], '-', linewidth=2, marker='o',
                           markersize=3, label=f'{energy:.2f} MeV', color=color)

            ax.legend(loc='best', fontsize=10)
        else:
            # Plot selected energy only
            idx = self.energy_selector.currentIndex()
            if 0 <= idx < len(datasets):
                dataset = datasets[idx]
                energy = dataset['energy']
                data = dataset['data']
                if data is not None and len(data.shape) >= 2 and data.shape[1] >= 2:
                    ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2, marker='o',
                           markersize=4, label=f'{energy:.4f} MeV')
                    ax.legend(loc='best', fontsize=10)

        ax.set_xlabel('Angle (degrees)', fontsize=12)
        ax.set_ylabel('dσ/dΩ (mb/sr)', fontsize=12)
        ax.set_title(f'{title_prefix} - Angular Distribution (CM Frame)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_yscale('log')

    def plot_energy_distribution(self, ax):
        """Plot integrated cross sections vs energy (from fort.39)"""
        if 'fort39' in self.current_data:
            data = self.current_data['fort39']
            if data is not None and len(data.shape) >= 2 and data.shape[1] >= 4:
                # fort.39 format: Ecm, elastic, elastic(dup), total, absorption, reaction
                ecm = data[:, 0]

                # Plot different cross section types
                ax.plot(ecm, data[:, 1], 'b-o', linewidth=2, marker='o',
                       markersize=6, label='Elastic')
                ax.plot(ecm, data[:, 3], 'r-s', linewidth=2, marker='s',
                       markersize=6, label='Total')
                if data.shape[1] >= 6:
                    # Plot reaction cross section if available
                    reaction = data[:, 5]
                    if not np.allclose(reaction, 0):  # Only plot if non-zero
                        ax.plot(ecm, reaction, 'g-^', linewidth=2, marker='^',
                               markersize=6, label='Reaction')

                ax.set_xlabel('E$_{cm}$ (MeV)', fontsize=12)
                ax.set_ylabel('Cross Section (mb)', fontsize=12)
                ax.set_title('Integrated Cross Sections vs Energy', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.legend(loc='best', fontsize=10)
            else:
                self._show_no_data(ax, 'fort.39')
        else:
            self._show_no_data(ax, 'fort.39')

    def plot_phaseshift(self, ax):
        """Plot phase shifts (Nuclear phase shift vs J)"""
        if not self.phaseshift_datasets:
            self._show_no_data(ax, 'fort.45 (phase shifts)')
            return

        # Color cycle for different energies
        colors = plt.cm.tab10(np.linspace(0, 1, 10))

        if self.show_all_energies.isChecked():
            # Plot all energies
            for i, dataset in enumerate(self.phaseshift_datasets):
                J = dataset['J']
                phase2 = dataset['phase2']  # Nuclear phase shift
                color = colors[i % len(colors)]

                # Get energy label (use CM energy from fort.45)
                energy = dataset['energy']
                label = f'{energy:.2f} MeV (CM)'

                ax.plot(J, phase2, '-o', linewidth=2, markersize=4,
                       label=label, color=color)

            ax.legend(loc='best', fontsize=10)
        else:
            # Plot selected energy only
            idx = self.energy_selector.currentIndex()
            if 0 <= idx < len(self.phaseshift_datasets):
                dataset = self.phaseshift_datasets[idx]
                J = dataset['J']
                phase2 = dataset['phase2']  # Nuclear phase shift
                energy = dataset['energy']
                label = f'{energy:.4f} MeV (CM)'

                ax.plot(J, phase2, 'b-o', linewidth=2, markersize=4, label=label)
                ax.legend(loc='best', fontsize=10)

        ax.set_xlabel('Total Angular Momentum J', fontsize=12)
        ax.set_ylabel('Nuclear Phase Shift (degrees)', fontsize=12)
        ax.set_title('Nuclear Phase Shifts', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linestyle='--', alpha=0.3, linewidth=1)

    def plot_smatrix(self, ax):
        """Plot S-matrix elements (|S| vs J)"""
        if not self.smatrix_datasets:
            self._show_no_data(ax, 'fort.7 (S-matrix)')
            return

        # Color cycle for different energies
        colors = plt.cm.tab10(np.linspace(0, 1, 10))

        if self.show_all_energies.isChecked():
            # Plot all energies
            for i, dataset in enumerate(self.smatrix_datasets):
                J = dataset['J']
                S_mag = dataset['S_magnitude']
                color = colors[i % len(colors)]

                # Get corresponding energy from fort.201 if available
                if i < len(self.energy_datasets):
                    energy = self.energy_datasets[i]['energy']
                    label = f'{energy:.2f} MeV'
                else:
                    label = f'Energy {i+1}'

                ax.plot(J, S_mag, '-o', linewidth=2, markersize=4,
                       label=label, color=color)

            ax.legend(loc='best', fontsize=10)
        else:
            # Plot selected energy only
            idx = self.energy_selector.currentIndex()
            if 0 <= idx < len(self.smatrix_datasets):
                dataset = self.smatrix_datasets[idx]
                J = dataset['J']
                S_mag = dataset['S_magnitude']

                # Get corresponding energy label
                if idx < len(self.energy_datasets):
                    energy = self.energy_datasets[idx]['energy']
                    label = f'{energy:.4f} MeV'
                else:
                    label = f'Energy {idx+1}'

                ax.plot(J, S_mag, 'b-o', linewidth=2, markersize=4, label=label)
                ax.legend(loc='best', fontsize=10)

        ax.set_xlabel('Total Angular Momentum J', fontsize=12)
        ax.set_ylabel('|S|', fontsize=12)
        ax.set_title('S-Matrix Elements', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.1)  # |S| ranges from 0 to ~1

    def _show_no_data(self, ax, filename):
        """Display no data message"""
        ax.text(0.5, 0.5, f'No data available for {filename}\n\nRun FRESCO to generate results',
               ha='center', va='center', transform=ax.transAxes,
               fontsize=12, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    def clear_plot(self):
        """Clear the plot"""
        self.current_data = {}
        self.energy_datasets = []
        self.energy_datasets_202 = []
        self.smatrix_datasets = []
        self.phaseshift_datasets = []
        self.energy_selector.clear()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No data to display\n\nRun a calculation to see results',
               ha='center', va='center', transform=ax.transAxes,
               fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
