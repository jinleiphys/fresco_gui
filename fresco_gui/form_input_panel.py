"""
Form-based input panel for FRESCO with different calculation types
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox, QScrollArea,
    QPushButton, QLabel, QTabWidget, QTextEdit
)
from PySide6.QtCore import Qt, Signal


class ElasticScatteringForm(QWidget):
    """Form for elastic scattering calculations"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the elastic scattering form"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Header
        header_label = QLabel("Elastic Scattering Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007AFF;")
        main_layout.addWidget(header_label)

        # General Parameters
        general_group = QGroupBox("General FRESCO Parameters")
        general_layout = QFormLayout()

        self.header = QLineEdit("Alpha + 12C elastic scattering at 30 MeV")
        general_layout.addRow("Header:", self.header)

        self.hcm = QDoubleSpinBox()
        self.hcm.setRange(0.001, 1.0)
        self.hcm.setDecimals(3)
        self.hcm.setValue(0.05)
        general_layout.addRow("Integration step (hcm):", self.hcm)

        self.rmatch = QDoubleSpinBox()
        self.rmatch.setRange(1.0, 200.0)
        self.rmatch.setValue(30.0)
        general_layout.addRow("Matching radius (rmatch):", self.rmatch)

        self.absend = QDoubleSpinBox()
        self.absend.setRange(0.0, 1.0)
        self.absend.setDecimals(4)
        self.absend.setValue(0.01)
        general_layout.addRow("Absorption end (absend):", self.absend)

        self.thmax = QDoubleSpinBox()
        self.thmax.setRange(0.0, 180.0)
        self.thmax.setValue(180.0)
        general_layout.addRow("Maximum angle (thmax):", self.thmax)

        self.jtmax = QSpinBox()
        self.jtmax.setRange(1, 200)
        self.jtmax.setValue(40)
        general_layout.addRow("Maximum J (jtmax):", self.jtmax)

        self.thinc = QDoubleSpinBox()
        self.thinc.setRange(0.1, 10.0)
        self.thinc.setValue(5.0)
        general_layout.addRow("Angle increment (thinc):", self.thinc)

        self.elab = QDoubleSpinBox()
        self.elab.setRange(0.1, 1000.0)
        self.elab.setValue(30.0)
        general_layout.addRow("Lab energy (elab) [MeV]:", self.elab)

        self.iter = QSpinBox()
        self.iter.setRange(0, 10)
        self.iter.setValue(1)
        general_layout.addRow("Iterations (iter):", self.iter)

        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)

        # Projectile Parameters
        proj_group = QGroupBox("Projectile (Incoming Particle)")
        proj_layout = QFormLayout()

        self.proj_name = QLineEdit("alpha")
        proj_layout.addRow("Name:", self.proj_name)

        self.proj_mass = QDoubleSpinBox()
        self.proj_mass.setRange(0.001, 300.0)
        self.proj_mass.setDecimals(4)
        self.proj_mass.setValue(4.0)
        proj_layout.addRow("Mass (amu):", self.proj_mass)

        self.proj_charge = QDoubleSpinBox()
        self.proj_charge.setRange(0.0, 100.0)
        self.proj_charge.setValue(2.0)
        proj_layout.addRow("Charge:", self.proj_charge)

        self.proj_spin = QDoubleSpinBox()
        self.proj_spin.setRange(0.0, 20.0)
        self.proj_spin.setSingleStep(0.5)
        self.proj_spin.setValue(0.0)
        proj_layout.addRow("Spin:", self.proj_spin)

        proj_group.setLayout(proj_layout)
        main_layout.addWidget(proj_group)

        # Target Parameters
        targ_group = QGroupBox("Target (Stationary Nucleus)")
        targ_layout = QFormLayout()

        self.targ_name = QLineEdit("12C")
        targ_layout.addRow("Name:", self.targ_name)

        self.targ_mass = QDoubleSpinBox()
        self.targ_mass.setRange(0.001, 300.0)
        self.targ_mass.setDecimals(4)
        self.targ_mass.setValue(12.0)
        targ_layout.addRow("Mass (amu):", self.targ_mass)

        self.targ_charge = QDoubleSpinBox()
        self.targ_charge.setRange(0.0, 100.0)
        self.targ_charge.setValue(6.0)
        targ_layout.addRow("Charge:", self.targ_charge)

        self.targ_spin = QDoubleSpinBox()
        self.targ_spin.setRange(0.0, 20.0)
        self.targ_spin.setSingleStep(0.5)
        self.targ_spin.setValue(0.0)
        targ_layout.addRow("Spin:", self.targ_spin)

        targ_group.setLayout(targ_layout)
        main_layout.addWidget(targ_group)

        # Optical Potential Parameters
        pot_group = QGroupBox("Optical Potential Parameters")
        pot_layout = QFormLayout()

        pot_layout.addRow(QLabel("Real Potential (Woods-Saxon):"))

        self.pot_v = QDoubleSpinBox()
        self.pot_v.setRange(-500.0, 500.0)
        self.pot_v.setValue(50.0)
        pot_layout.addRow("  Depth V (MeV):", self.pot_v)

        self.pot_r = QDoubleSpinBox()
        self.pot_r.setRange(0.1, 5.0)
        self.pot_r.setDecimals(2)
        self.pot_r.setValue(1.2)
        pot_layout.addRow("  Radius r0 (fm):", self.pot_r)

        self.pot_a = QDoubleSpinBox()
        self.pot_a.setRange(0.1, 2.0)
        self.pot_a.setDecimals(2)
        self.pot_a.setValue(0.65)
        pot_layout.addRow("  Diffuseness a (fm):", self.pot_a)

        pot_layout.addRow(QLabel("\nImaginary Potential (Woods-Saxon):"))

        self.pot_w = QDoubleSpinBox()
        self.pot_w.setRange(-500.0, 500.0)
        self.pot_w.setValue(10.0)
        pot_layout.addRow("  Depth W (MeV):", self.pot_w)

        self.pot_rw = QDoubleSpinBox()
        self.pot_rw.setRange(0.1, 5.0)
        self.pot_rw.setDecimals(2)
        self.pot_rw.setValue(1.2)
        pot_layout.addRow("  Radius r0W (fm):", self.pot_rw)

        self.pot_aw = QDoubleSpinBox()
        self.pot_aw.setRange(0.1, 2.0)
        self.pot_aw.setDecimals(2)
        self.pot_aw.setValue(0.65)
        pot_layout.addRow("  Diffuseness aW (fm):", self.pot_aw)

        pot_layout.addRow(QLabel("\nCoulomb:"))

        self.pot_rc = QDoubleSpinBox()
        self.pot_rc.setRange(0.1, 5.0)
        self.pot_rc.setDecimals(2)
        self.pot_rc.setValue(1.3)
        pot_layout.addRow("  Coulomb radius rc (fm):", self.pot_rc)

        pot_group.setLayout(pot_layout)
        main_layout.addWidget(pot_group)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def generate_input(self):
        """Generate FRESCO input text from form values"""
        input_text = f"""! {self.header.text()}
! Generated by FRESCO Quantum Studio

&FRESCO
hcm={self.hcm.value()}
rmatch={self.rmatch.value()}
absend={self.absend.value()}
thmax={self.thmax.value()}
jtmax={self.jtmax.value()}
thinc={self.thinc.value()}
elab={self.elab.value()}
iter={self.iter.value()}
/

&PARTITION
namep='{self.proj_name.text()}'
massp={self.proj_mass.value()}
zp={self.proj_charge.value()}
jp={self.proj_spin.value()}
namet='{self.targ_name.text()}'
masst={self.targ_mass.value()}
zt={self.targ_charge.value()}
jt={self.targ_spin.value()}
/

&STATES
jp={self.proj_spin.value()}
bandp=1
ep=0.0
cpot=1
jt={self.targ_spin.value()}
bandt=1
et=0.0
/

&POT
kp=1
type=0
p1=0.0
p2=0.0
p3=0.0
ap=1.0
at=1.0
rc={self.pot_rc.value()}
/

&POT
kp=1
type=1
p1={self.pot_v.value()}
p2={self.pot_r.value()}
p3={self.pot_a.value()}
ap=1.0
at=1.0
rc={self.pot_rc.value()}
/

&POT
kp=1
type=2
p1={self.pot_w.value()}
p2={self.pot_rw.value()}
p3={self.pot_aw.value()}
ap=1.0
at=1.0
rc={self.pot_rc.value()}
/
"""
        return input_text


class InelasticScatteringForm(QWidget):
    """Form for inelastic scattering calculations"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the inelastic scattering form"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Header
        header_label = QLabel("Inelastic Scattering Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007AFF;")
        main_layout.addWidget(header_label)

        info_label = QLabel("Configure inelastic scattering to excited states")
        info_label.setStyleSheet("color: #6c757d; font-style: italic;")
        main_layout.addWidget(info_label)

        # Placeholder for now
        placeholder = QLabel("\n\nInelastic scattering form under construction...\n\n"
                           "This will include:\n"
                           "• Ground and excited state configurations\n"
                           "• Collective model parameters\n"
                           "• Deformation parameters\n"
                           "• Transition potentials\n")
        placeholder.setStyleSheet("font-size: 12px; color: #666;")
        main_layout.addWidget(placeholder)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def generate_input(self):
        """Generate FRESCO input text from form values"""
        return "! Inelastic scattering input (under construction)\n"


class TransferReactionForm(QWidget):
    """Form for transfer reaction calculations"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the transfer reaction form"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Header
        header_label = QLabel("Transfer Reaction Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007AFF;")
        main_layout.addWidget(header_label)

        info_label = QLabel("Configure one-nucleon or cluster transfer reactions")
        info_label.setStyleSheet("color: #6c757d; font-style: italic;")
        main_layout.addWidget(info_label)

        # Placeholder
        placeholder = QLabel("\n\nTransfer reaction form under construction...\n\n"
                           "This will include:\n"
                           "• Incoming and outgoing channel definitions\n"
                           "• Transferred particle properties\n"
                           "• Overlap integrals\n"
                           "• DWBA coupling parameters\n")
        placeholder.setStyleSheet("font-size: 12px; color: #666;")
        main_layout.addWidget(placeholder)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def generate_input(self):
        """Generate FRESCO input text from form values"""
        return "! Transfer reaction input (under construction)\n"


class FormInputPanel(QWidget):
    """Main form-based input panel with multiple calculation types"""

    input_generated = Signal(str)  # Signal emitted when input is generated from form

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the form input panel"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Form-Based Input Generator")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Generate button
        self.generate_btn = QPushButton("Generate Input File")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0066DD;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_input)
        header_layout.addWidget(self.generate_btn)

        layout.addLayout(header_layout)

        # Calculation type tabs
        self.calc_tabs = QTabWidget()
        self.calc_tabs.setDocumentMode(True)

        # Add different calculation types
        self.elastic_form = ElasticScatteringForm()
        self.calc_tabs.addTab(self.elastic_form, "Elastic Scattering")

        self.inelastic_form = InelasticScatteringForm()
        self.calc_tabs.addTab(self.inelastic_form, "Inelastic Scattering")

        self.transfer_form = TransferReactionForm()
        self.calc_tabs.addTab(self.transfer_form, "Transfer Reactions")

        layout.addWidget(self.calc_tabs)

        # Footer with hints
        footer = QLabel("Tip: Fill in the parameters above and click 'Generate Input File' to create FRESCO input text.")
        footer.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
        footer.setWordWrap(True)
        layout.addWidget(footer)

    def generate_input(self):
        """Generate input from current form and emit signal"""
        current_index = self.calc_tabs.currentIndex()

        if current_index == 0:  # Elastic
            input_text = self.elastic_form.generate_input()
        elif current_index == 1:  # Inelastic
            input_text = self.inelastic_form.generate_input()
        elif current_index == 2:  # Transfer
            input_text = self.transfer_form.generate_input()
        else:
            input_text = "! Unknown calculation type\n"

        self.input_generated.emit(input_text)

    def get_current_input(self):
        """Get the current input text from the active form"""
        current_index = self.calc_tabs.currentIndex()

        if current_index == 0:
            return self.elastic_form.generate_input()
        elif current_index == 1:
            return self.inelastic_form.generate_input()
        elif current_index == 2:
            return self.transfer_form.generate_input()
        else:
            return ""
