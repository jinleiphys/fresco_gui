"""
Widget for managing multiple excited states in FRESCO calculations

Handles &STATES namelists with full parameter support according to FRESCO manual:
- Jp, COPYp, BANDp, Ep, KKp, Tp (projectile state)
- Jt, COPYt, BANDt, Et, KKt, Tt (target state)
- KP, FEXCH, IGNORE, INFAM, OUTFAM (additional parameters)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QSpinBox, QDoubleSpinBox, QCheckBox, QLabel,
    QComboBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal


class SingleStateWidget(QWidget):
    """Widget for a single excited state configuration"""

    removed = Signal(object)  # Signal emitted when this state should be removed

    def __init__(self, state_index=1, is_ground_state=False):
        super().__init__()
        self.state_index = state_index
        self.is_ground_state = is_ground_state
        self.init_ui()

    def init_ui(self):
        """Initialize single state widget"""
        # Create collapsible group box
        title = "Ground State (0+)" if self.is_ground_state else f"Excited State #{self.state_index}"
        self.group_box = QGroupBox(title)
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Start collapsed

        layout = QVBoxLayout(self.group_box)

        # Use a form layout for better organization
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Projectile state parameters
        proj_label = QLabel("<b>Projectile State:</b>")
        form_layout.addRow(proj_label)

        self.jp = QDoubleSpinBox()
        self.jp.setRange(0.0, 20.0)
        self.jp.setSingleStep(0.5)
        self.jp.setValue(0.0 if self.is_ground_state else 0.0)
        self.jp.setToolTip("Spin of projectile state")
        form_layout.addRow("Jp (spin):", self.jp)

        self.copyp = QSpinBox()
        self.copyp.setRange(-10, 10)
        self.copyp.setValue(1 if not self.is_ground_state else 0)
        self.copyp.setSpecialValueText("No copy")
        self.copyp.setToolTip("Copy from state number (0 = no copy, >0 = copy, <0 = exchange copy)")
        form_layout.addRow("COPYp:", self.copyp)

        self.bandp = QSpinBox()
        self.bandp.setRange(-10, 10)
        self.bandp.setValue(1)
        self.bandp.setToolTip("Rotational band (>0 for positive parity, <0 for negative parity)")
        form_layout.addRow("BANDp (parity):", self.bandp)

        self.ep = QDoubleSpinBox()
        self.ep.setRange(0.0, 50.0)
        self.ep.setDecimals(3)
        self.ep.setValue(0.0)
        self.ep.setToolTip("Excitation energy in MeV")
        form_layout.addRow("Ep (MeV):", self.ep)

        # Add spacing
        form_layout.addRow(QLabel(""))

        # Target state parameters
        targ_label = QLabel("<b>Target State:</b>")
        form_layout.addRow(targ_label)

        self.jt = QDoubleSpinBox()
        self.jt.setRange(0.0, 20.0)
        self.jt.setSingleStep(0.5)
        self.jt.setValue(0.0 if self.is_ground_state else 2.0)
        self.jt.setToolTip("Spin of target state")
        form_layout.addRow("Jt (spin):", self.jt)

        self.copyt = QSpinBox()
        self.copyt.setRange(-10, 10)
        self.copyt.setValue(0)
        self.copyt.setSpecialValueText("No copy")
        self.copyt.setToolTip("Copy from state number (0 = no copy, >0 = copy, <0 = exchange copy)")
        form_layout.addRow("COPYt:", self.copyt)

        self.bandt = QSpinBox()
        self.bandt.setRange(-10, 10)
        self.bandt.setValue(1)
        self.bandt.setToolTip("Rotational band (>0 for positive parity, <0 for negative parity)")
        form_layout.addRow("BANDt (parity):", self.bandt)

        self.et = QDoubleSpinBox()
        self.et.setRange(0.0, 50.0)
        self.et.setDecimals(3)
        self.et.setValue(0.0 if self.is_ground_state else 4.439)
        self.et.setToolTip("Excitation energy in MeV")
        form_layout.addRow("Et (MeV):", self.et)

        # Add spacing
        form_layout.addRow(QLabel(""))

        # Additional parameters
        addl_label = QLabel("<b>Additional Parameters:</b>")
        form_layout.addRow(addl_label)

        self.kp = QSpinBox()
        self.kp.setRange(0, 20)
        self.kp.setValue(1)
        self.kp.setToolTip("Index of optical potential (0 = use partition number)")
        form_layout.addRow("KP (potential):", self.kp)

        # Checkboxes for boolean parameters
        checkbox_layout = QHBoxLayout()

        self.fexch = QCheckBox("FEXCH")
        self.fexch.setToolTip("Calculate cross sections for 180° - θ")
        checkbox_layout.addWidget(self.fexch)

        self.ignore = QCheckBox("IGNORE")
        self.ignore.setToolTip("Ignore convergence of this state pair")
        checkbox_layout.addWidget(self.ignore)

        checkbox_layout.addStretch()
        form_layout.addRow("Options:", checkbox_layout)

        layout.addLayout(form_layout)

        # Remove button (only for excited states, not ground state)
        if not self.is_ground_state:
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            remove_btn = QPushButton("Remove State")
            remove_btn.setObjectName("removeButton")
            remove_btn.clicked.connect(lambda: self.removed.emit(self))
            btn_layout.addWidget(remove_btn)
            layout.addLayout(btn_layout)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)

    def get_state_data(self):
        """Get state data as dictionary"""
        return {
            'jp': self.jp.value(),
            'copyp': self.copyp.value() if self.copyp.value() != 0 else None,
            'bandp': self.bandp.value(),
            'ep': self.ep.value(),
            'jt': self.jt.value(),
            'copyt': self.copyt.value() if self.copyt.value() != 0 else None,
            'bandt': self.bandt.value(),
            'et': self.et.value(),
            'kp': self.kp.value(),
            'cpot': self.kp.value(),  # Alias for kp
            'fexch': self.fexch.isChecked(),
            'ignore': self.ignore.isChecked()
        }

    def set_state_data(self, data):
        """Set state data from dictionary"""
        if 'jp' in data:
            self.jp.setValue(data['jp'])
        if 'copyp' in data and data['copyp'] is not None:
            self.copyp.setValue(data['copyp'])
        if 'bandp' in data:
            self.bandp.setValue(data['bandp'])
        if 'ep' in data:
            self.ep.setValue(data['ep'])
        if 'jt' in data:
            self.jt.setValue(data['jt'])
        if 'copyt' in data and data['copyt'] is not None:
            self.copyt.setValue(data['copyt'])
        if 'bandt' in data:
            self.bandt.setValue(data['bandt'])
        if 'et' in data:
            self.et.setValue(data['et'])
        if 'kp' in data:
            self.kp.setValue(data['kp'])
        elif 'cpot' in data:
            self.kp.setValue(data['cpot'])
        if 'fexch' in data:
            self.fexch.setChecked(data['fexch'])
        if 'ignore' in data:
            self.ignore.setChecked(data['ignore'])

    def generate_namelist(self):
        """Generate &STATES namelist text"""
        data = self.get_state_data()

        # Build namelist string
        parts = []
        parts.append(f"jp={data['jp']}")
        if data['copyp'] is not None:
            parts.append(f"copyp={data['copyp']}")
        parts.append(f"bandp={data['bandp']}")
        parts.append(f"ep={data['ep']}")

        parts.append(f"cpot={data['cpot']}")

        parts.append(f"jt={data['jt']}")
        if data['copyt'] is not None:
            parts.append(f"copyt={data['copyt']}")
        parts.append(f"bandt={data['bandt']}")
        parts.append(f"et={data['et']}")

        # Add optional boolean parameters
        if data['fexch']:
            parts.append("fexch=T")
        if data['ignore']:
            parts.append("ignore=T")

        return f" &STATES {' '.join(parts)} /"


class StatesManagerWidget(QWidget):
    """Manager widget for multiple excited states"""

    def __init__(self):
        super().__init__()
        self.state_widgets = []
        self.init_ui()

        # Add ground state by default
        self.add_ground_state()

    def init_ui(self):
        """Initialize the states manager widget"""
        self.group_box = QGroupBox("Excited States Configuration")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(True)  # Start expanded

        main_layout = QVBoxLayout(self.group_box)

        # Info label
        info = QLabel("Define quantum states for inelastic scattering. Ground state (0+) is required, add excited states as needed.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #6b7280; font-size: 12px;")
        main_layout.addWidget(info)

        # Scroll area for states
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        self.states_container = QWidget()
        self.states_layout = QVBoxLayout(self.states_container)
        self.states_layout.setContentsMargins(0, 0, 0, 0)
        self.states_layout.addStretch()

        scroll.setWidget(self.states_container)
        main_layout.addWidget(scroll)

        # Add state button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        add_btn = QPushButton("➕ Add Excited State")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self.add_excited_state)
        btn_layout.addWidget(add_btn)
        main_layout.addLayout(btn_layout)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.group_box)

    def add_ground_state(self):
        """Add the ground state (always present)"""
        state_widget = SingleStateWidget(state_index=0, is_ground_state=True)
        state_widget.group_box.setChecked(True)  # Ground state starts expanded
        self.state_widgets.append(state_widget)
        # Insert before the stretch
        self.states_layout.insertWidget(len(self.state_widgets) - 1, state_widget)

    def add_excited_state(self):
        """Add a new excited state"""
        state_index = len(self.state_widgets)  # 0-indexed, ground state is 0
        state_widget = SingleStateWidget(state_index=state_index, is_ground_state=False)
        state_widget.removed.connect(self.remove_state)

        self.state_widgets.append(state_widget)
        # Insert before the stretch
        self.states_layout.insertWidget(len(self.state_widgets) - 1, state_widget)

        # Auto-expand the new state
        state_widget.group_box.setChecked(True)

    def remove_state(self, state_widget):
        """Remove a state widget"""
        if state_widget in self.state_widgets and not state_widget.is_ground_state:
            self.state_widgets.remove(state_widget)
            state_widget.deleteLater()

            # Renumber remaining excited states
            for i, widget in enumerate(self.state_widgets):
                if not widget.is_ground_state:
                    widget.state_index = i
                    widget.group_box.setTitle(f"Excited State #{i}")

    def get_nex(self):
        """Get the number of excited states (NEX parameter for &PARTITION)"""
        return len(self.state_widgets)

    def get_all_states_data(self):
        """Get data for all states"""
        return [widget.get_state_data() for widget in self.state_widgets]

    def set_all_states_data(self, states_data_list):
        """Set data for all states from a list of dictionaries"""
        # Clear existing excited states (keep ground state)
        while len(self.state_widgets) > 1:
            self.remove_state(self.state_widgets[-1])

        # Set data for each state
        for i, state_data in enumerate(states_data_list):
            if i == 0:
                # Update ground state
                self.state_widgets[0].set_state_data(state_data)
            else:
                # Add new excited state
                self.add_excited_state()
                self.state_widgets[i].set_state_data(state_data)

    def generate_states_namelists(self):
        """Generate all &STATES namelists"""
        namelists = []
        for widget in self.state_widgets:
            namelists.append(widget.generate_namelist())
        return '\n'.join(namelists)

    def clear_excited_states(self):
        """Remove all excited states (keep only ground state)"""
        while len(self.state_widgets) > 1:
            self.remove_state(self.state_widgets[-1])
