"""
POT Widget for managing optical potentials in FRESCO
Allows adding/removing/editing multiple potential components
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QGroupBox, QScrollArea, QDoubleSpinBox, QSpinBox,
    QLineEdit, QComboBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from pot_namelist import POT_NAMELIST


class SinglePotentialWidget(QWidget):
    """Widget for a single &POT namelist entry"""

    remove_requested = Signal(object)  # Emitted when user wants to remove this potential

    def __init__(self, pot_number=1, parent=None):
        super().__init__(parent)
        self.pot_number = pot_number
        self.parameter_widgets = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI for a single potential"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create collapsible group box
        self.group_box = QGroupBox(f"🔬 Potential Component #{self.pot_number}")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(True)  # Expanded by default
        self.group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #007AFF;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Header with type selector and remove button
        header_layout = QHBoxLayout()

        type_label = QLabel("Potential Type:")
        type_label.setStyleSheet("font-weight: normal;")
        header_layout.addWidget(type_label)

        self.type_combo = QComboBox()
        self.type_combo.addItem("0: Coulomb (defines radii)", 0)
        self.type_combo.addItem("1: Volume potential", 1)
        self.type_combo.addItem("2: Surface potential", 2)
        self.type_combo.addItem("3: Spin-orbit (projectile)", 3)
        self.type_combo.addItem("4: Spin-orbit (target)", 4)
        self.type_combo.addItem("8: Deformation", 8)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        header_layout.addWidget(self.type_combo, 1)

        header_layout.addStretch()

        remove_btn = QPushButton("❌ Remove")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #FF2D20;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        header_layout.addWidget(remove_btn)

        content_layout.addLayout(header_layout)

        # Parameters form (dynamic based on type)
        self.params_form = QFormLayout()
        self.params_form.setSpacing(8)
        content_layout.addLayout(self.params_form)

        # Add to group box
        group_layout = QVBoxLayout()
        group_layout.addWidget(content_widget)
        self.group_box.setLayout(group_layout)

        # Connect collapse/expand
        self.group_box.toggled.connect(lambda checked: content_widget.setVisible(checked))

        layout.addWidget(self.group_box)

        # Initialize with type 0 (Coulomb)
        self.on_type_changed()

    def on_type_changed(self):
        """Update parameter fields based on selected type"""
        # Clear existing parameter widgets
        while self.params_form.count():
            item = self.params_form.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.parameter_widgets.clear()

        pot_type = self.type_combo.currentData()

        # Always add KP (partition number)
        self.add_parameter_widget("kp", "Partition number (kp):",
                                   "Which partition this potential applies to", 1, 1, 20, 1)

        # Add SHAPE selector for type > 0
        if pot_type > 0:
            shape_combo = QComboBox()
            shape_combo.addItem("0: Woods-Saxon", 0)
            shape_combo.addItem("1: WS Squared", 1)
            shape_combo.addItem("2: Gaussian", 2)
            shape_combo.addItem("3: Yukawa", 3)
            shape_combo.addItem("4: Exponential", 4)
            shape_combo.addItem("-1: Fourier-Bessel", -1)
            self.parameter_widgets["shape"] = shape_combo
            shape_label = QLabel("Shape:")
            shape_label.setToolTip("Radial form factor shape")
            self.params_form.addRow(shape_label, shape_combo)

        # Add parameters based on type
        if pot_type == 0:  # Coulomb
            self.add_coulomb_params()
        elif pot_type == 1:  # Volume
            self.add_volume_params()
        elif pot_type == 2:  # Surface
            self.add_surface_params()
        elif pot_type in [3, 4]:  # Spin-orbit
            self.add_spinorbit_params()
        elif pot_type == 8:  # Deformation
            self.add_deformation_params()

    def add_parameter_widget(self, name, label, tooltip, default, minimum, maximum, step):
        """Helper to add a numeric parameter widget"""
        if step and step < 1:
            widget = QDoubleSpinBox()
            widget.setDecimals(len(str(step).split('.')[-1]) if '.' in str(step) else 2)
        else:
            widget = QSpinBox()

        widget.setMinimum(minimum)
        widget.setMaximum(maximum)
        if step:
            widget.setSingleStep(step)
        widget.setValue(default)
        widget.setToolTip(tooltip)

        self.parameter_widgets[name] = widget

        label_widget = QLabel(label)
        label_widget.setToolTip(tooltip)
        label_widget.setStyleSheet("font-weight: normal;")
        self.params_form.addRow(label_widget, widget)

    def add_coulomb_params(self):
        """Add TYPE=0 (Coulomb) parameters"""
        self.add_parameter_widget("at", "Target mass At:",
                                   "Target mass number (for radius calculation)", 12.0, 1.0, 300.0, 0.1)
        self.add_parameter_widget("ap", "Projectile mass Ap:",
                                   "Projectile mass number (for radius calculation)", 4.0, 0.1, 300.0, 0.1)
        self.add_parameter_widget("rc", "Coulomb radius rc (fm):",
                                   "Coulomb radius parameter", 1.3, 0.1, 5.0, 0.01)
        self.add_parameter_widget("ac", "Coulomb diffuseness ac (fm):",
                                   "Coulomb diffuseness parameter", 0.0, 0.0, 2.0, 0.01)

    def add_volume_params(self):
        """Add TYPE=1 (Volume) parameters"""
        # Real part
        self.add_parameter_widget("v", "Real depth V (MeV):",
                                   "Depth of real potential (negative for attractive)", 50.0, -500.0, 500.0, 1.0)
        self.add_parameter_widget("vr0", "Real radius r₀ (fm):",
                                   "Radius parameter for real potential", 1.2, 0.1, 5.0, 0.01)
        self.add_parameter_widget("va", "Real diffuseness a (fm):",
                                   "Diffuseness for real potential", 0.65, 0.1, 2.0, 0.01)

        # Imaginary part
        self.add_parameter_widget("w", "Imaginary depth W (MeV):",
                                   "Depth of imaginary potential (for absorption)", 10.0, -500.0, 500.0, 1.0)
        self.add_parameter_widget("wr0", "Imaginary radius r₀W (fm):",
                                   "Radius parameter for imaginary potential", 1.2, 0.1, 5.0, 0.01)
        self.add_parameter_widget("wa", "Imaginary diffuseness aW (fm):",
                                   "Diffuseness for imaginary potential", 0.65, 0.1, 2.0, 0.01)

    def add_surface_params(self):
        """Add TYPE=2 (Surface) parameters"""
        # Real part (volume form)
        self.add_parameter_widget("v", "Volume depth V (MeV):",
                                   "Volume part of potential", 50.0, -500.0, 500.0, 1.0)
        self.add_parameter_widget("vr0", "Volume radius r₀ (fm):",
                                   "Radius for volume part", 1.2, 0.1, 5.0, 0.01)
        self.add_parameter_widget("va", "Volume diffuseness a (fm):",
                                   "Diffuseness for volume part", 0.65, 0.1, 2.0, 0.01)

        # Surface derivative part
        self.add_parameter_widget("wd", "Surface depth WD (MeV):",
                                   "Depth of surface imaginary potential", 10.0, -500.0, 500.0, 1.0)
        self.add_parameter_widget("wdr0", "Surface radius r₀D (fm):",
                                   "Radius for surface imaginary", 1.2, 0.1, 5.0, 0.01)
        self.add_parameter_widget("awd", "Surface diffuseness aD (fm):",
                                   "Diffuseness for surface imaginary", 0.65, 0.1, 2.0, 0.01)

    def add_spinorbit_params(self):
        """Add TYPE=3,4 (Spin-orbit) parameters"""
        self.add_parameter_widget("vso", "Spin-orbit V_SO (MeV):",
                                   "Spin-orbit strength (multiplied by ℏ²/(mπ²c²)=2.0)", 6.0, -100.0, 100.0, 0.1)
        self.add_parameter_widget("rso0", "SO radius r_SO (fm):",
                                   "Radius parameter for spin-orbit", 1.2, 0.1, 5.0, 0.01)
        self.add_parameter_widget("aso", "SO diffuseness a_SO (fm):",
                                   "Diffuseness for spin-orbit", 0.65, 0.1, 2.0, 0.01)

    def add_deformation_params(self):
        """Add TYPE=8 (Deformation) parameters"""
        self.add_parameter_widget("beta", "Deformation β:",
                                   "Deformation parameter for collective model", 0.3, -2.0, 2.0, 0.01)
        self.add_parameter_widget("vr0", "Deformation radius r₀ (fm):",
                                   "Radius for deformation potential", 1.2, 0.1, 5.0, 0.01)
        self.add_parameter_widget("va", "Deformation diffuseness a (fm):",
                                   "Diffuseness for deformation", 0.65, 0.1, 2.0, 0.01)

    def get_pot_values(self):
        """Get current parameter values as dictionary"""
        values = {}

        # Add type
        pot_type = self.type_combo.currentData()
        values["type"] = pot_type

        # Add all parameter values
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                values[param_name] = widget.value()
            elif isinstance(widget, QComboBox):
                values[param_name] = widget.currentData()
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    values[param_name] = text

        return values

    def set_pot_number(self, number):
        """Update the potential number displayed"""
        self.pot_number = number
        self.group_box.setTitle(f"🔬 Potential Component #{self.pot_number}")


class PotentialManagerWidget(QWidget):
    """Widget for managing multiple optical potentials"""

    potentials_changed = Signal()  # Emitted when potentials are added/removed/modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self.potential_widgets = []
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main group box
        self.group_box = QGroupBox("⚛️ Optical Potentials")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Collapsed by default
        self.group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Info label
        info_label = QLabel(
            "Add one or more potential components. Each &POT namelist defines a part of the optical potential.\n"
            "Start with TYPE=0 (Coulomb) to define radii, then add volume, surface, or spin-orbit components."
        )
        info_label.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        # Scroll area for potentials
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        self.potentials_container = QWidget()
        self.potentials_layout = QVBoxLayout(self.potentials_container)
        self.potentials_layout.setSpacing(10)

        scroll.setWidget(self.potentials_container)
        content_layout.addWidget(scroll)

        # Add/Reset buttons
        buttons_layout = QHBoxLayout()

        add_btn = QPushButton("➕ Add Potential Component")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #30B956;
            }
        """)
        add_btn.clicked.connect(self.add_potential)
        buttons_layout.addWidget(add_btn)

        buttons_layout.addStretch()

        reset_btn = QPushButton("Reset All")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        reset_btn.clicked.connect(self.reset_potentials)
        buttons_layout.addWidget(reset_btn)

        content_layout.addLayout(buttons_layout)

        # Add content to group box
        group_layout = QVBoxLayout()
        group_layout.addWidget(content_widget)
        self.group_box.setLayout(group_layout)

        # Connect collapse/expand
        self.group_box.toggled.connect(lambda checked: content_widget.setVisible(checked))
        content_widget.setVisible(False)  # Start collapsed

        layout.addWidget(self.group_box)

        # Add initial Coulomb potential
        self.add_potential()

    def add_potential(self):
        """Add a new potential component"""
        pot_widget = SinglePotentialWidget(len(self.potential_widgets) + 1)
        pot_widget.remove_requested.connect(self.remove_potential)

        self.potential_widgets.append(pot_widget)
        self.potentials_layout.addWidget(pot_widget)

        self.potentials_changed.emit()

    def remove_potential(self, pot_widget):
        """Remove a potential component"""
        if len(self.potential_widgets) <= 1:
            # Keep at least one potential
            return

        self.potential_widgets.remove(pot_widget)
        pot_widget.deleteLater()

        # Renumber remaining potentials
        for i, widget in enumerate(self.potential_widgets):
            widget.set_pot_number(i + 1)

        self.potentials_changed.emit()

    def reset_potentials(self):
        """Reset to single Coulomb potential"""
        # Remove all potentials
        for widget in self.potential_widgets:
            widget.deleteLater()
        self.potential_widgets.clear()

        # Add fresh Coulomb potential
        self.add_potential()

        self.potentials_changed.emit()

    def get_all_potentials(self):
        """Get all potential values as list of dictionaries"""
        return [widget.get_pot_values() for widget in self.potential_widgets]

    def generate_pot_namelists(self):
        """Generate all &POT namelist blocks as text"""
        all_pots = self.get_all_potentials()

        if not all_pots:
            return ""

        pot_blocks = []
        for pot_values in all_pots:
            pot_text = POT_NAMELIST.generate_pot_namelist(pot_values)
            if pot_text:
                pot_blocks.append(pot_text)

        return "\n".join(pot_blocks)
