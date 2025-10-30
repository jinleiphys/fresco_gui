"""
Plot widget for displaying FRESCO results using matplotlib
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import os


class PlotWidget(QWidget):
    """Widget for plotting FRESCO results"""

    def __init__(self):
        super().__init__()
        self.current_data = {}
        self.working_directory = None  # Store working directory for refresh
        self.init_ui()

    def init_ui(self):
        """Initialize the plot widget"""
        layout = QVBoxLayout(self)

        # Control panel
        control_layout = QHBoxLayout()

        self.plot_type = QComboBox()
        self.plot_type.addItems([
            "Cross Section vs Angle",
            "Cross Section vs Energy",
            "Elastic Scattering",
            "Inelastic Scattering",
            "Transfer Reactions",
            "S-Matrix Elements"
        ])
        self.plot_type.currentIndexChanged.connect(self.update_plot)
        control_layout.addWidget(QLabel("Plot Type:"))
        control_layout.addWidget(self.plot_type)

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

    def load_results(self, working_dir=None):
        """Load results from FRESCO output files"""
        try:
            # Store working directory for future refreshes
            if working_dir is not None:
                self.working_directory = working_dir

            # Use stored working directory if available
            if self.working_directory is None:
                self.working_directory = os.getcwd()

            # Try to read common FRESCO output files
            # fort.16 - cross sections
            # fort.201 - angular distributions
            # fort.202 - elastic cross sections

            fort16 = os.path.join(self.working_directory, 'fort.16')
            if os.path.exists(fort16):
                data = self.read_fort_file(fort16)
                self.current_data['fort16'] = data

            fort201 = os.path.join(self.working_directory, 'fort.201')
            if os.path.exists(fort201):
                data = self.read_fort_file(fort201)
                self.current_data['fort201'] = data

            fort202 = os.path.join(self.working_directory, 'fort.202')
            if os.path.exists(fort202):
                data = self.read_fort_file(fort202)
                self.current_data['fort202'] = data

            self.update_plot()

        except Exception as e:
            print(f"Error loading results: {e}")

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

        if plot_idx == 0:  # Cross Section vs Angle
            self.plot_angular_distribution(ax)
        elif plot_idx == 1:  # Cross Section vs Energy
            self.plot_energy_distribution(ax)
        elif plot_idx == 2:  # Elastic Scattering
            self.plot_elastic(ax)
        elif plot_idx == 3:  # Inelastic Scattering
            self.plot_inelastic(ax)
        elif plot_idx == 4:  # Transfer Reactions
            self.plot_transfer(ax)
        elif plot_idx == 5:  # S-Matrix Elements
            self.plot_smatrix(ax)

        self.canvas.draw()

    def plot_angular_distribution(self, ax):
        """Plot angular distribution"""
        if 'fort201' in self.current_data:
            data = self.current_data['fort201']
            if data is not None and len(data.shape) >= 2 and data.shape[1] >= 2:
                ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2, marker='o', markersize=4)
                ax.set_xlabel('Angle (degrees)', fontsize=12)
                ax.set_ylabel('dσ/dΩ (mb/sr)', fontsize=12)
                ax.set_title('Angular Distribution', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.set_yscale('log')
            else:
                self._show_no_data(ax, 'fort.201')
        else:
            self._show_no_data(ax, 'fort.201')

    def plot_energy_distribution(self, ax):
        """Plot energy distribution"""
        if 'fort202' in self.current_data:
            data = self.current_data['fort202']
            if data is not None and len(data.shape) >= 2 and data.shape[1] >= 2:
                ax.plot(data[:, 0], data[:, 1], 'r-', linewidth=2, marker='s', markersize=4)
                ax.set_xlabel('Energy (MeV)', fontsize=12)
                ax.set_ylabel('Cross Section (mb)', fontsize=12)
                ax.set_title('Energy Distribution', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
            else:
                self._show_no_data(ax, 'fort.202')
        else:
            self._show_no_data(ax, 'fort.202')

    def plot_elastic(self, ax):
        """Plot elastic scattering"""
        if 'fort16' in self.current_data:
            data = self.current_data['fort16']
            if data is not None and len(data.shape) >= 2 and data.shape[1] >= 2:
                ax.plot(data[:, 0], data[:, 1], 'g-', linewidth=2, marker='^', markersize=4)
                ax.set_xlabel('Angle (degrees)', fontsize=12)
                ax.set_ylabel('dσ/dΩ (mb/sr)', fontsize=12)
                ax.set_title('Elastic Scattering', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.set_yscale('log')
            else:
                self._show_no_data(ax, 'fort.16')
        else:
            self._show_no_data(ax, 'fort.16')

    def plot_inelastic(self, ax):
        """Plot inelastic scattering"""
        self._show_no_data(ax, 'inelastic data')

    def plot_transfer(self, ax):
        """Plot transfer reactions"""
        self._show_no_data(ax, 'transfer data')

    def plot_smatrix(self, ax):
        """Plot S-matrix elements"""
        self._show_no_data(ax, 'S-matrix data')

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
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No data to display\n\nRun a calculation to see results',
               ha='center', va='center', transform=ax.transAxes,
               fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        self.canvas.draw()
