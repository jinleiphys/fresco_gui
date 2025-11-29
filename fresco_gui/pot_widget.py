"""
POT Widget for managing optical potentials in FRESCO
Allows adding/removing/editing multiple potential components
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout, QLabel,
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
        self.kp_value = pot_number  # Default kp equals pot_number
        self.parameter_widgets = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI for a single potential"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create collapsible group box with modern card design
        self.group_box = QGroupBox(f"POT #{self.pot_number}")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Collapsed by default to save space

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Header with type selector and remove button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        type_label = QLabel("Type:")
        type_label.setObjectName("potLabel")
        header_layout.addWidget(type_label)

        self.type_combo = QComboBox()
        self.type_combo.addItem("Coulomb", 0)
        self.type_combo.addItem("Volume", 1)
        self.type_combo.addItem("Surface", 2)
        self.type_combo.addItem("Spin-orbit (proj)", 3)
        self.type_combo.addItem("Spin-orbit (targ)", 4)
        self.type_combo.addItem("Deformation", 8)
        self.type_combo.addItem("Deformation (TYPE=11)", 11)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        header_layout.addWidget(self.type_combo, 1)

        header_layout.addStretch()

        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("removeButton")
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        header_layout.addWidget(remove_btn)

        content_layout.addLayout(header_layout)

        # Add a visual separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(separator)

        # Parameters grid (2 columns for more compact layout)
        self.params_grid = QGridLayout()
        self.params_grid.setSpacing(10)
        self.params_grid.setContentsMargins(5, 10, 5, 10)
        content_layout.addLayout(self.params_grid)

        # Keep track of row position
        self.current_row = 0

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
        while self.params_grid.count():
            item = self.params_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.parameter_widgets.clear()
        self.current_row = 0

        pot_type = self.type_combo.currentData()

        # Note: kp is stored in self.kp_value, not as a parameter widget
        # This is because kp is set during parsing and shouldn't be user-editable

        # Add SHAPE selector for type > 0
        if pot_type > 0:
            shape_combo = QComboBox()
            shape_combo.addItem("Woods-Saxon", 0)
            shape_combo.addItem("WS Squared", 1)
            shape_combo.addItem("Gaussian", 2)
            shape_combo.addItem("Yukawa", 3)
            shape_combo.addItem("Exponential", 4)
            shape_combo.addItem("Fourier-Bessel", -1)
            self.parameter_widgets["shape"] = shape_combo
            shape_label = QLabel("Shape:")
            shape_label.setToolTip("Radial form factor shape")
            shape_label.setObjectName("paramLabel")
            self.add_to_grid(shape_label, shape_combo)

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
        elif pot_type == 11:  # Deformation (TYPE=11)
            # For TYPE=11, typically only p2 (radius) is specified
            self.add_parameter_widget("vr0", "Deformation radius (p2, fm):",
                                       "Radius parameter for deformation", 1.3, 0.1, 5.0, 0.01)

    def add_to_grid(self, label, widget):
        """Add a label-widget pair to the grid layout (2 columns)"""
        col = (self.current_row % 2) * 2  # 0 or 2
        row = self.current_row // 2
        self.params_grid.addWidget(label, row, col)
        self.params_grid.addWidget(widget, row, col + 1)
        self.current_row += 1

    def add_parameter_widget(self, name, label_text, tooltip, default, minimum, maximum, step):
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

        label_widget = QLabel(label_text)
        label_widget.setToolTip(tooltip)
        label_widget.setObjectName("paramLabel")
        self.add_to_grid(label_widget, widget)

    def add_coulomb_params(self):
        """Add TYPE=0 (Coulomb) parameters"""
        self.add_parameter_widget("at", "At:",
                                   "Target mass number", 12.0, 0.0, 300.0, 0.1)
        self.add_parameter_widget("ap", "Ap:",
                                   "Projectile mass number", 4.0, 0.0, 300.0, 0.1)
        self.add_parameter_widget("rc", "rc (fm):",
                                   "Coulomb radius parameter", 1.3, 0.0, 5.0, 0.01)
        self.add_parameter_widget("ac", "ac (fm):",
                                   "Coulomb diffuseness", 0.0, 0.0, 2.0, 0.01)

    def add_volume_params(self):
        """Add TYPE=1 (Volume) parameters"""
        # Real part
        self.add_parameter_widget("v", "V (MeV):",
                                   "Real potential depth", 50.0, -500.0, 500.0, 0.1)
        self.add_parameter_widget("vr0", "r0:",
                                   "Real radius (fm)", 1.2, 0.0, 5.0, 0.01)
        self.add_parameter_widget("va", "a (fm):",
                                   "Real diffuseness", 0.65, 0.0, 2.0, 0.01)

        # Imaginary part
        self.add_parameter_widget("w", "W (MeV):",
                                   "Imaginary depth", 10.0, -500.0, 500.0, 0.1)
        self.add_parameter_widget("wr0", "r0W:",
                                   "Imaginary radius (fm)", 1.2, 0.0, 5.0, 0.01)
        self.add_parameter_widget("wa", "aW (fm):",
                                   "Imaginary diffuseness", 0.65, 0.0, 2.0, 0.01)

    def add_surface_params(self):
        """Add TYPE=2 (Surface) parameters"""
        # Real part (volume form)
        self.add_parameter_widget("v", "Volume depth V (MeV):",
                                   "Volume part of potential", 50.0, -500.0, 500.0, 0.1)
        self.add_parameter_widget("vr0", "Volume radius r₀ (fm):",
                                   "Radius for volume part", 1.2, 0.0, 5.0, 0.01)
        self.add_parameter_widget("va", "Volume diffuseness a (fm):",
                                   "Diffuseness for volume part", 0.65, 0.0, 2.0, 0.01)

        # Surface derivative part
        self.add_parameter_widget("wd", "Surface depth WD (MeV):",
                                   "Depth of surface imaginary potential", 10.0, -500.0, 500.0, 0.1)
        self.add_parameter_widget("wdr0", "Surface radius r₀D (fm):",
                                   "Radius for surface imaginary", 1.2, 0.0, 5.0, 0.01)
        self.add_parameter_widget("awd", "Surface diffuseness aD (fm):",
                                   "Diffuseness for surface imaginary", 0.65, 0.0, 2.0, 0.01)

    def add_spinorbit_params(self):
        """Add TYPE=3,4 (Spin-orbit) parameters"""
        self.add_parameter_widget("vso", "Spin-orbit V_SO (MeV):",
                                   "Spin-orbit strength (multiplied by ℏ²/(mπ²c²)=2.0)", 6.0, -100.0, 100.0, 0.1)
        self.add_parameter_widget("rso0", "SO radius r_SO (fm):",
                                   "Radius parameter for spin-orbit", 1.2, 0.0, 5.0, 0.01)
        self.add_parameter_widget("aso", "SO diffuseness a_SO (fm):",
                                   "Diffuseness for spin-orbit", 0.65, 0.0, 2.0, 0.01)

    def add_deformation_params(self):
        """Add TYPE=8 (Deformation) parameters"""
        self.add_parameter_widget("beta", "Deformation β:",
                                   "Deformation parameter for collective model", 0.3, -2.0, 2.0, 0.01)
        self.add_parameter_widget("vr0", "Deformation radius r₀ (fm):",
                                   "Radius for deformation potential", 1.2, 0.0, 5.0, 0.01)
        self.add_parameter_widget("va", "Deformation diffuseness a (fm):",
                                   "Diffuseness for deformation", 0.65, 0.0, 2.0, 0.01)

    def get_pot_values(self):
        """
        Get current parameter values as dictionary
        Returns values in FRESCO format (ap/at/rc for TYPE=0, p1-p6 for others)
        """
        values = {}

        # Add kp (potential set identifier)
        values["kp"] = self.kp_value

        # Add type
        pot_type = self.type_combo.currentData()
        values["type"] = pot_type

        # Define reverse mapping from user-friendly names to p1, p2, p3...
        # TYPE=0 (Coulomb) uses ap/at/rc/ac (NO mapping to p1/p2/p3)
        # TYPE=1,2,3,etc use p1-p6
        reverse_mapping = {}

        if pot_type == 0:  # Coulomb - NO reverse mapping, keep ap/at/rc/ac
            reverse_mapping = {}  # Keep original names
        elif pot_type == 1:  # Volume
            reverse_mapping = {
                'v':    'p1',  # Real depth V
                'vr0':  'p2',  # Real radius r0
                'va':   'p3',  # Real diffuseness a
                'w':    'p4',  # Imaginary depth W
                'wr0':  'p5',  # Imaginary radius r0W
                'wa':   'p6',  # Imaginary diffuseness aW
            }
        elif pot_type == 2:  # Surface
            reverse_mapping = {
                'v':    'p1',  # Real depth V
                'vr0':  'p2',  # Real radius r0
                'va':   'p3',  # Real diffuseness a
                'wd':   'p4',  # Surface imaginary depth WD
                'wdr0': 'p5',  # Surface imaginary radius r0D
                'awd':  'p6',  # Surface imaginary diffuseness aD
            }
        elif pot_type == 3:  # Spin-orbit
            reverse_mapping = {
                'vso':   'p1',  # Real S.O. strength
                'rso0':  'p2',  # Real S.O. radius
                'aso':   'p3',  # Real S.O. diffuseness
                'wso':   'p4',  # Imaginary S.O. strength
                'wsor0': 'p5',  # Imaginary S.O. radius
                'wsoa':  'p6',  # Imaginary S.O. diffuseness
            }
        elif pot_type == 11:  # Deformation
            reverse_mapping = {
                'vr0':  'p2',  # Deformation radius parameter (most common usage)
            }

        # Add all parameter values with mapping
        for param_name, widget in self.parameter_widgets.items():
            # Get the value
            value = None
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
            elif isinstance(widget, QComboBox):
                value = widget.currentData()
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    value = text

            if value is not None:
                # Use reverse mapping if available, otherwise use original name
                output_name = reverse_mapping.get(param_name, param_name)
                values[output_name] = value

        return values

    def set_pot_number(self, number):
        """Update the potential number displayed"""
        self.pot_number = number
        self.group_box.setTitle(f"POT #{self.pot_number}")

    def set_pot_values(self, values):
        """
        Set POT parameter values from a dictionary

        Args:
            values: Dictionary with keys like 'type', 'kp', 'shape', 'p1', 'p2', etc.
        """
        print(f"    [SinglePotWidget #{self.pot_number}] Setting values: {values}")
        print(f"      Initial kp_value (before set): {self.kp_value}")

        # Set kp value
        if 'kp' in values:
            self.kp_value = values['kp']
            print(f"      Set kp from values: kp = {self.kp_value}")
        else:
            print(f"      WARNING: 'kp' not in values! Keeping default kp_value={self.kp_value}")

        # Set potential type first (this determines which parameters are shown)
        if 'type' in values:
            pot_type = values['type']
            for i in range(self.type_combo.count()):
                if self.type_combo.itemData(i) == pot_type:
                    self.type_combo.setCurrentIndex(i)
                    print(f"      Set type = {pot_type}")
                    break

        # Map p1, p2, p3, etc. to actual parameter names based on type
        # This mapping follows FRESCO namelist conventions
        pot_type = values.get('type', 0)

        # Default parameter mapping (for most types)
        # p1-p6 typically map to: V, r0, a, W, r0W, aW (for volume/surface types)
        param_mapping = {}

        if pot_type == 0:  # Coulomb
            param_mapping = {
                'p1': 'ap',  # Projectile mass number
                'p2': 'at',  # Target parameter
                'p3': 'rc',  # Coulomb radius parameter
            }
        elif pot_type == 1:  # Volume
            param_mapping = {
                'p1': 'v',      # Real depth V
                'p2': 'vr0',    # Real radius r0
                'p3': 'va',     # Real diffuseness a
                'p4': 'w',      # Imaginary depth W
                'p5': 'wr0',    # Imaginary radius r0W
                'p6': 'wa',     # Imaginary diffuseness aW
            }
            # Reset all type=1 parameters to 0 if not provided
            for p_num in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']:
                if p_num not in values:
                    param_name = param_mapping.get(p_num)
                    if param_name and param_name in self.parameter_widgets:
                        widget = self.parameter_widgets[param_name]
                        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                            widget.setValue(0)
        elif pot_type == 2:  # Surface
            param_mapping = {
                'p1': 'v',      # Real depth V
                'p2': 'vr0',    # Real radius r0
                'p3': 'va',     # Real diffuseness a
                'p4': 'wd',     # Surface imaginary depth WD
                'p5': 'wdr0',   # Surface imaginary radius r0D
                'p6': 'awd',    # Surface imaginary diffuseness aD
            }
            # Reset all type=2 parameters to 0 if not provided
            for p_num in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']:
                if p_num not in values:
                    param_name = param_mapping.get(p_num)
                    if param_name and param_name in self.parameter_widgets:
                        widget = self.parameter_widgets[param_name]
                        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                            widget.setValue(0)
        elif pot_type == 3:  # Spin-orbit
            param_mapping = {
                'p1': 'vso',    # Real S.O. strength
                'p2': 'rso0',   # Real S.O. radius
                'p3': 'aso',    # Real S.O. diffuseness
                'p4': 'wso',    # Imaginary S.O. strength
                'p5': 'wsor0',  # Imaginary S.O. radius
                'p6': 'wsoa',   # Imaginary S.O. diffuseness
            }
            # Reset all type=3 parameters to 0 if not provided
            for p_num in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6']:
                if p_num not in values:
                    param_name = param_mapping.get(p_num)
                    if param_name and param_name in self.parameter_widgets:
                        widget = self.parameter_widgets[param_name]
                        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                            widget.setValue(0)
        elif pot_type == 11:  # Deformation (TYPE=11)
            param_mapping = {
                'p2': 'vr0',    # Deformation radius parameter
            }
        # For other types (deformation, etc.), we don't map p1-p6

        # Set parameters
        for param_name, param_value in values.items():
            if param_name in ['type', 'kp', 'shape']:
                continue  # Already handled or not a parameter widget

            # Try to map p1, p2, etc. to actual parameter names
            if param_name in param_mapping:
                actual_param = param_mapping[param_name]
                if actual_param in self.parameter_widgets:
                    widget = self.parameter_widgets[actual_param]
                    try:
                        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                            # For at and rc, allow 0 values by updating minimum if needed
                            old_min = widget.minimum()
                            if actual_param in ['at', 'rc', 'ap'] and param_value < widget.minimum():
                                widget.setMinimum(0.0)
                                print(f"        Updated minimum for {actual_param}: {old_min} -> 0.0", flush=True)
                            widget.setValue(param_value)
                            actual_value = widget.value()
                            print(f"      Set {actual_param} (from {param_name}) = {param_value}, actual value = {actual_value}", flush=True)
                    except Exception as e:
                        print(f"      Warning: Could not set {actual_param} = {param_value}: {e}")
            elif param_name in self.parameter_widgets:
                # Direct parameter name (not p1, p2, etc.)
                widget = self.parameter_widgets[param_name]
                try:
                    if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                        widget.setValue(param_value)
                        print(f"      Set {param_name} = {param_value}")
                    elif isinstance(widget, QComboBox):
                        for i in range(widget.count()):
                            if widget.itemData(i) == param_value:
                                widget.setCurrentIndex(i)
                                print(f"      Set {param_name} = {param_value}")
                                break
                    elif isinstance(widget, QLineEdit):
                        widget.setText(str(param_value))
                        print(f"      Set {param_name} = {param_value}")
                except Exception as e:
                    print(f"      Warning: Could not set {param_name} = {param_value}: {e}")


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

        # Main group box with unified style
        self.group_box = QGroupBox("Optical Potentials")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Collapsed by default

        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Info label with modern style
        info_label = QLabel(
            "💡 Add potential components (Coulomb, Volume, Surface, Spin-orbit). Hover over parameters for details."
        )
        info_label.setObjectName("infoBox")
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
        add_btn.setObjectName("presetButton")
        add_btn.clicked.connect(self.add_potential)
        buttons_layout.addWidget(add_btn)

        buttons_layout.addStretch()

        reset_btn = QPushButton("Reset All")
        reset_btn.setObjectName("resetButton")
        reset_btn.setProperty("styleClass", "secondary")
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

        # Add initial p+Ni78 potentials (Coulomb + Volume)
        self.reset_potentials()

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
        """Reset to p+Ni78 default potentials (Coulomb + Volume)"""
        # Remove all potentials
        for widget in self.potential_widgets:
            widget.deleteLater()
        self.potential_widgets.clear()

        # Add POT #1: Coulomb
        pot1 = SinglePotentialWidget(1)
        pot1.remove_requested.connect(self.remove_potential)
        # Set Coulomb parameters: ap=1.0, at=78.0, rc=1.2
        pot1.type_combo.setCurrentIndex(0)  # Coulomb
        pot1.kp_value = 1  # Set kp directly
        pot1.parameter_widgets['ap'].setValue(1.0)
        pot1.parameter_widgets['at'].setValue(78.0)
        pot1.parameter_widgets['rc'].setValue(1.2)
        pot1.parameter_widgets['ac'].setValue(0.0)
        self.potential_widgets.append(pot1)
        self.potentials_layout.addWidget(pot1)

        # Add POT #2: Volume
        pot2 = SinglePotentialWidget(2)
        pot2.remove_requested.connect(self.remove_potential)
        # Set Volume parameters: V=40.0, r0=1.2, a=0.65, W=10.0, r0W=1.2, aW=0.5
        pot2.type_combo.setCurrentIndex(1)  # Volume (index 1)
        pot2.kp_value = 1  # Set kp directly
        pot2.parameter_widgets['v'].setValue(40.0)
        pot2.parameter_widgets['vr0'].setValue(1.2)
        pot2.parameter_widgets['va'].setValue(0.65)
        pot2.parameter_widgets['w'].setValue(10.0)
        pot2.parameter_widgets['wr0'].setValue(1.2)
        pot2.parameter_widgets['wa'].setValue(0.5)
        self.potential_widgets.append(pot2)
        self.potentials_layout.addWidget(pot2)

        # Expand both POTs to show the configuration
        pot1.group_box.setChecked(True)
        pot2.group_box.setChecked(True)

        # Expand the main POT group box
        self.group_box.setChecked(True)

        self.potentials_changed.emit()

    def get_all_potentials(self):
        """Get all potential values as list of dictionaries"""
        print(f"\n[PotentialManager] get_all_potentials called, {len(self.potential_widgets)} widgets")
        result = []
        for i, widget in enumerate(self.potential_widgets):
            pot_values = widget.get_pot_values()
            print(f"  Widget #{i+1}: kp={pot_values.get('kp')}, type={pot_values.get('type')}")
            result.append(pot_values)
        return result

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

    def load_from_input_text(self, input_text):
        """
        Load POT definitions from FRESCO input file text

        Args:
            input_text: Content of FRESCO input file
        """
        from parameter_manager import parse_pot_namelists

        print(f"  [PotentialManager] Loading POT information from input...")

        # Parse all POT namelists
        pot_list = parse_pot_namelists(input_text)
        print(f"    Found {len(pot_list)} POT namelists")

        if not pot_list:
            print(f"    No POT namelists found, keeping defaults")
            return

        # Clear existing potentials
        for widget in self.potential_widgets:
            widget.deleteLater()
        self.potential_widgets.clear()

        # Create and populate new potential widgets
        for i, pot_params in enumerate(pot_list):
            # IMPORTANT: Don't use i+1 as default, that overwrites the parsed kp!
            # Create widget without setting kp_value yet
            pot_widget = SinglePotentialWidget(pot_number=i + 1)
            pot_widget.remove_requested.connect(self.remove_potential)
            print(f"    [POT #{i+1}] Parsed params: kp={pot_params.get('kp', 'NOT FOUND')}, type={pot_params.get('type')}")
            pot_widget.set_pot_values(pot_params)
            print(f"    [POT #{i+1}] After set_pot_values: kp_value={pot_widget.kp_value}")

            self.potential_widgets.append(pot_widget)
            self.potentials_layout.addWidget(pot_widget)

        print(f"    Successfully loaded {len(pot_list)} POT components")

        # Auto-expand the group box after loading
        self.group_box.setChecked(True)

        self.potentials_changed.emit()
