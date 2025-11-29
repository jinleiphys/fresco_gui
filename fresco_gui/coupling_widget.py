"""
Widget for managing coupling definitions in FRESCO calculations

Handles &COUPLING namelists for inelastic scattering and transfer reactions
Also handles &CFP namelists for fractional parentage coefficients
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QSpinBox, QDoubleSpinBox, QLabel, QComboBox,
    QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, Signal


class SingleCFPWidget(QWidget):
    """Widget for a single CFP (Coefficient of Fractional Parentage) definition"""

    removed = Signal(object)

    def __init__(self, cfp_index=1):
        super().__init__()
        self.cfp_index = cfp_index
        self.init_ui()

    def init_ui(self):
        """Initialize single CFP widget"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # CFP parameters in a compact row
        self.in_val = QSpinBox()
        self.in_val.setRange(1, 20)
        self.in_val.setValue(1)
        self.in_val.setToolTip("Overlap function index (in)")
        self.in_val.setFixedWidth(60)

        self.ib = QSpinBox()
        self.ib.setRange(1, 20)
        self.ib.setValue(1)
        self.ib.setToolTip("State index in partition ib")
        self.ib.setFixedWidth(60)

        self.ia = QSpinBox()
        self.ia.setRange(1, 20)
        self.ia.setValue(1)
        self.ia.setToolTip("State index in partition ia")
        self.ia.setFixedWidth(60)

        self.kn = QSpinBox()
        self.kn.setRange(1, 20)
        self.kn.setValue(1)
        self.kn.setToolTip("Overlap function number (kn)")
        self.kn.setFixedWidth(60)

        self.a = QDoubleSpinBox()
        self.a.setRange(-10.0, 10.0)
        self.a.setDecimals(4)
        self.a.setValue(1.0)
        self.a.setToolTip("Spectroscopic amplitude (a)")
        self.a.setFixedWidth(80)

        # Add labels and widgets
        layout.addWidget(QLabel("in:"))
        layout.addWidget(self.in_val)
        layout.addWidget(QLabel("ib:"))
        layout.addWidget(self.ib)
        layout.addWidget(QLabel("ia:"))
        layout.addWidget(self.ia)
        layout.addWidget(QLabel("kn:"))
        layout.addWidget(self.kn)
        layout.addWidget(QLabel("a:"))
        layout.addWidget(self.a)

        # Remove button
        remove_btn = QPushButton("✕")
        remove_btn.setFixedWidth(30)
        remove_btn.setToolTip("Remove this CFP")
        remove_btn.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(remove_btn)

        layout.addStretch()

    def get_cfp_data(self):
        """Get CFP data as dictionary"""
        return {
            'in': self.in_val.value(),
            'ib': self.ib.value(),
            'ia': self.ia.value(),
            'kn': self.kn.value(),
            'a': self.a.value(),
        }

    def set_cfp_data(self, data):
        """Set CFP data from dictionary"""
        if 'in' in data:
            self.in_val.setValue(data['in'])
        if 'ib' in data:
            self.ib.setValue(data['ib'])
        if 'ia' in data:
            self.ia.setValue(data['ia'])
        if 'kn' in data:
            self.kn.setValue(data['kn'])
        if 'a' in data:
            self.a.setValue(data['a'])

    def generate_namelist(self):
        """Generate &CFP namelist text"""
        data = self.get_cfp_data()
        return f"&CFP in={data['in']} ib={data['ib']} ia={data['ia']} kn={data['kn']} a={data['a']:.2f} /"


class SingleCouplingWidget(QWidget):
    """Widget for a single coupling definition"""

    removed = Signal(object)  # Signal emitted when this coupling should be removed

    def __init__(self, coupling_index=1):
        super().__init__()
        self.coupling_index = coupling_index
        self.init_ui()

    def init_ui(self):
        """Initialize single coupling widget"""
        # Create collapsible group box
        self.group_box = QGroupBox(f"Coupling #{self.coupling_index}")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(True)  # Start expanded

        layout = QVBoxLayout(self.group_box)

        # Use a form layout
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Coupling type
        self.kind = QComboBox()
        self.kind.addItems([
            "0 - No coupling",
            "1 - Rotational (E2, E4, ...)",
            "2 - Vibrational",
            "3 - Two-phonon vibrational",
            "7 - Transfer",
            "8 - Reorientation",
            "11 - Deformation potential"
        ])
        self.kind.setCurrentIndex(6)  # Default to deformation (type 11)
        self.kind.currentIndexChanged.connect(self.on_kind_changed)
        self.kind.setToolTip("Type of coupling mechanism")
        form_layout.addRow("Coupling type (kind):", self.kind)

        # State indices
        self.icfrom = QSpinBox()
        self.icfrom.setRange(1, 20)
        self.icfrom.setValue(1)
        self.icfrom.setToolTip("Initial state index (partition.state)")
        form_layout.addRow("From state (icfrom):", self.icfrom)

        self.icto = QSpinBox()
        self.icto.setRange(-20, 20)
        self.icto.setValue(2)
        self.icto.setToolTip("Final state index. Negative value = all states in partition |icto|")
        form_layout.addRow("To state (icto):", self.icto)

        # Partition indices
        self.iafrom = QSpinBox()
        self.iafrom.setRange(1, 10)
        self.iafrom.setValue(1)
        self.iafrom.setToolTip("Partition index for initial state")
        form_layout.addRow("From partition (iafrom):", self.iafrom)

        self.iato = QSpinBox()
        self.iato.setRange(1, 10)
        self.iato.setValue(1)
        self.iato.setToolTip("Partition index for final state")
        form_layout.addRow("To partition (iato):", self.iato)

        # Potential indices
        self.ip1 = QSpinBox()
        self.ip1.setRange(0, 20)
        self.ip1.setValue(0)
        self.ip1.setToolTip("Index of coupling potential (0 = use default)")
        form_layout.addRow("Potential 1 (ip1):", self.ip1)

        self.ip2 = QSpinBox()
        self.ip2.setRange(-20, 20)
        self.ip2.setValue(0)
        self.ip2.setToolTip("Index of second potential. Negative = use remnant potentials")
        form_layout.addRow("Potential 2 (ip2):", self.ip2)

        self.ip3 = QSpinBox()
        self.ip3.setRange(0, 20)
        self.ip3.setValue(0)
        self.ip3.setToolTip("Index of non-orthogonality potential (for transfer reactions)")
        form_layout.addRow("Potential 3 (ip3):", self.ip3)

        # Multipolarity (for rotational/vibrational)
        self.lambda_val = QSpinBox()
        self.lambda_val.setRange(0, 10)
        self.lambda_val.setValue(2)
        self.lambda_val.setToolTip("Multipolarity λ (for rotational/vibrational coupling)")
        form_layout.addRow("Multipolarity (λ):", self.lambda_val)

        # Collective parameter (deformation)
        self.jbeta = QDoubleSpinBox()
        self.jbeta.setRange(0.0, 2.0)
        self.jbeta.setDecimals(4)
        self.jbeta.setValue(0.5)
        self.jbeta.setToolTip("Deformation parameter β (for kind=11)")
        form_layout.addRow("Deformation (jbeta):", self.jbeta)

        layout.addLayout(form_layout)

        # CFP section (for transfer reactions, kind=7)
        self.cfp_group = QGroupBox("CFP (Coefficients of Fractional Parentage)")
        self.cfp_group.setCheckable(True)
        self.cfp_group.setChecked(True)
        cfp_layout = QVBoxLayout(self.cfp_group)

        cfp_info = QLabel("Define spectroscopic amplitudes for transfer reactions")
        cfp_info.setStyleSheet("color: #6b7280; font-size: 11px;")
        cfp_layout.addWidget(cfp_info)

        # Container for CFP widgets
        self.cfp_container = QWidget()
        self.cfp_container_layout = QVBoxLayout(self.cfp_container)
        self.cfp_container_layout.setContentsMargins(0, 0, 0, 0)
        cfp_layout.addWidget(self.cfp_container)

        # Add CFP button
        add_cfp_btn = QPushButton("➕ Add CFP")
        add_cfp_btn.clicked.connect(self.add_cfp)
        cfp_layout.addWidget(add_cfp_btn)

        layout.addWidget(self.cfp_group)

        # Initialize CFP widgets list
        self.cfp_widgets = []

        # Remove button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        remove_btn = QPushButton("Remove Coupling")
        remove_btn.setObjectName("removeButton")
        remove_btn.clicked.connect(lambda: self.removed.emit(self))
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)

        # Update visibility based on initial kind
        self.update_cfp_visibility()

    def on_kind_changed(self, index):
        """Update UI based on coupling type"""
        self.update_cfp_visibility()

    def update_cfp_visibility(self):
        """Show/hide CFP section based on coupling type"""
        kind_text = self.kind.currentText()
        kind_value = int(kind_text.split('-')[0].strip())
        # Show CFP only for transfer reactions (kind=7)
        self.cfp_group.setVisible(kind_value == 7)

    def add_cfp(self):
        """Add a new CFP definition"""
        cfp_index = len(self.cfp_widgets) + 1
        cfp_widget = SingleCFPWidget(cfp_index=cfp_index)
        cfp_widget.removed.connect(self.remove_cfp)

        self.cfp_widgets.append(cfp_widget)
        self.cfp_container_layout.addWidget(cfp_widget)

    def remove_cfp(self, cfp_widget):
        """Remove a CFP widget"""
        if cfp_widget in self.cfp_widgets:
            self.cfp_widgets.remove(cfp_widget)
            cfp_widget.deleteLater()

    def get_coupling_data(self):
        """Get coupling data as dictionary"""
        kind_value = int(self.kind.currentText().split('-')[0].strip())

        data = {
            'kind': kind_value,
            'icfrom': self.icfrom.value(),
            'icto': self.icto.value(),
            'iafrom': self.iafrom.value(),
            'iato': self.iato.value(),
            'ip1': self.ip1.value(),
            'ip2': self.ip2.value(),
            'ip3': self.ip3.value(),
        }

        # Add type-specific parameters
        if kind_value in [1, 2, 3, 11]:  # Rotational/vibrational/deformation
            data['lambda'] = self.lambda_val.value()
        if kind_value == 11:  # Deformation potential
            data['jbeta'] = self.jbeta.value()

        # Add CFP data for transfer reactions
        if kind_value == 7:
            data['cfp_list'] = [w.get_cfp_data() for w in self.cfp_widgets]

        return data

    def set_coupling_data(self, data):
        """Set coupling data from dictionary"""
        if 'kind' in data:
            # Find index in combo box
            for i in range(self.kind.count()):
                if self.kind.itemText(i).startswith(f"{data['kind']} -"):
                    self.kind.setCurrentIndex(i)
                    break
        if 'icfrom' in data:
            self.icfrom.setValue(data['icfrom'])
        if 'icto' in data:
            self.icto.setValue(data['icto'])
        if 'iafrom' in data:
            self.iafrom.setValue(data['iafrom'])
        if 'iato' in data:
            self.iato.setValue(data['iato'])
        if 'ip1' in data:
            self.ip1.setValue(data['ip1'])
        if 'ip2' in data:
            self.ip2.setValue(data['ip2'])
        if 'ip3' in data:
            self.ip3.setValue(data['ip3'])
        if 'lambda' in data:
            self.lambda_val.setValue(data['lambda'])
        if 'jbeta' in data:
            self.jbeta.setValue(data['jbeta'])

        # Set CFP data
        if 'cfp_list' in data:
            # Clear existing CFPs
            while self.cfp_widgets:
                self.remove_cfp(self.cfp_widgets[0])
            # Add new CFPs
            for cfp_data in data['cfp_list']:
                self.add_cfp()
                self.cfp_widgets[-1].set_cfp_data(cfp_data)

        # Update visibility
        self.update_cfp_visibility()

    def generate_namelist(self):
        """Generate &COUPLING namelist text"""
        data = self.get_coupling_data()

        # Build namelist string
        parts = []
        parts.append(f"kind={data['kind']}")
        parts.append(f"icfrom={data['icfrom']}")
        parts.append(f"icto={data['icto']}")

        # Only include partition indices if not equal to 1 (default)
        if data['iafrom'] != 1:
            parts.append(f"iafrom={data['iafrom']}")
        if data['iato'] != 1:
            parts.append(f"iato={data['iato']}")

        # Include potential indices
        parts.append(f"ip1={data['ip1']}")
        parts.append(f"ip2={data['ip2']}")
        if data['ip3'] != 0:
            parts.append(f"ip3={data['ip3']}")

        # Add type-specific parameters
        if 'lambda' in data:
            parts.append(f"lambda={data['lambda']}")
        if 'jbeta' in data:
            parts.append(f"jbeta={data['jbeta']}")

        coupling_line = f"&Coupling {' '.join(parts)} /"

        # Add CFP namelists for transfer reactions
        if data['kind'] == 7 and self.cfp_widgets:
            cfp_lines = [w.generate_namelist() for w in self.cfp_widgets]
            cfp_lines.append("&CFP /")  # Terminating CFP
            return coupling_line + "\n" + "\n".join(cfp_lines)

        return coupling_line


class CouplingManagerWidget(QWidget):
    """Manager widget for multiple coupling definitions"""

    def __init__(self):
        super().__init__()
        self.coupling_widgets = []
        self.init_ui()

    def init_ui(self):
        """Initialize the coupling manager widget"""
        self.group_box = QGroupBox("Coupling Definitions")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(True)  # Start expanded

        main_layout = QVBoxLayout(self.group_box)

        # Info label
        info = QLabel("Define how quantum states are coupled (e.g., through deformation, rotation, vibration).")
        info.setWordWrap(True)
        info.setStyleSheet("color: #6b7280; font-size: 12px;")
        main_layout.addWidget(info)

        # Scroll area for couplings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setMinimumHeight(600)  # Increased height for better visibility

        self.couplings_container = QWidget()
        self.couplings_layout = QVBoxLayout(self.couplings_container)
        self.couplings_layout.setContentsMargins(0, 0, 0, 0)
        self.couplings_layout.addStretch()

        scroll.setWidget(self.couplings_container)
        main_layout.addWidget(scroll)

        # Add coupling button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        add_btn = QPushButton("➕ Add Coupling")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self.add_coupling)
        btn_layout.addWidget(add_btn)
        main_layout.addLayout(btn_layout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.group_box)

    def add_coupling(self):
        """Add a new coupling definition"""
        coupling_index = len(self.coupling_widgets) + 1
        coupling_widget = SingleCouplingWidget(coupling_index=coupling_index)
        coupling_widget.removed.connect(self.remove_coupling)

        self.coupling_widgets.append(coupling_widget)
        # Insert before the stretch
        self.couplings_layout.insertWidget(len(self.coupling_widgets) - 1, coupling_widget)

    def remove_coupling(self, coupling_widget):
        """Remove a coupling widget"""
        if coupling_widget in self.coupling_widgets:
            self.coupling_widgets.remove(coupling_widget)
            coupling_widget.deleteLater()

            # Renumber remaining couplings
            for i, widget in enumerate(self.coupling_widgets):
                widget.coupling_index = i + 1
                widget.group_box.setTitle(f"Coupling #{i + 1}")

    def get_all_couplings_data(self):
        """Get data for all couplings"""
        return [widget.get_coupling_data() for widget in self.coupling_widgets]

    def set_all_couplings_data(self, couplings_data_list):
        """Set data for all couplings from a list of dictionaries"""
        # Clear existing couplings
        while self.coupling_widgets:
            self.remove_coupling(self.coupling_widgets[0])

        # Add new couplings
        for coupling_data in couplings_data_list:
            self.add_coupling()
            self.coupling_widgets[-1].set_coupling_data(coupling_data)

    def generate_couplings_namelists(self):
        """Generate all &COUPLING namelists"""
        if not self.coupling_widgets:
            return ""

        namelists = []
        for widget in self.coupling_widgets:
            namelists.append(widget.generate_namelist())
        return '\n'.join(namelists)

    def clear_all_couplings(self):
        """Remove all coupling definitions"""
        while self.coupling_widgets:
            self.remove_coupling(self.coupling_widgets[0])
