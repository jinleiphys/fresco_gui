"""
Form-based input panel for FRESCO with different calculation types
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox, QScrollArea,
    QPushButton, QLabel, QTabWidget, QTextEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from advanced_parameters_widget import AdvancedParametersWidget


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

        # Header with preset examples
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_label = QLabel("Elastic Scattering Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007AFF;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        preset_btn = QPushButton("Load Preset Example")
        preset_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #30B956;
            }
        """)
        preset_btn.clicked.connect(self.load_preset)
        header_layout.addWidget(preset_btn)

        main_layout.addWidget(header_widget)

        # General Parameters
        general_group = QGroupBox("General FRESCO Parameters")
        general_layout = QFormLayout()

        self.header = QLineEdit("Alpha + 12C elastic scattering at 30 MeV")
        general_layout.addRow("Header:", self.header)

        self.hcm = QDoubleSpinBox()
        self.hcm.setRange(0.001, 1.0)
        self.hcm.setDecimals(3)
        self.hcm.setValue(0.05)
        self.hcm.setToolTip("Step size for integration (typical: 0.05-0.1)")
        general_layout.addRow("Integration step (hcm):", self.hcm)

        self.rmatch = QDoubleSpinBox()
        self.rmatch.setRange(1.0, 200.0)
        self.rmatch.setValue(30.0)
        self.rmatch.setToolTip("Matching radius in fm (typical: 20-60)")
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

        # Advanced FRESCO Parameters
        self.advanced_params = AdvancedParametersWidget()
        main_layout.addWidget(self.advanced_params)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def load_preset(self):
        """Load a preset example"""
        self.header.setText("Alpha + 12C elastic scattering at 30 MeV")
        self.hcm.setValue(0.05)
        self.rmatch.setValue(30.0)
        self.absend.setValue(0.01)
        self.thmax.setValue(180.0)
        self.jtmax.setValue(40)
        self.thinc.setValue(5.0)
        self.elab.setValue(30.0)
        self.iter.setValue(1)

        self.proj_name.setText("alpha")
        self.proj_mass.setValue(4.0)
        self.proj_charge.setValue(2.0)
        self.proj_spin.setValue(0.0)

        self.targ_name.setText("12C")
        self.targ_mass.setValue(12.0)
        self.targ_charge.setValue(6.0)
        self.targ_spin.setValue(0.0)

        self.pot_v.setValue(50.0)
        self.pot_r.setValue(1.2)
        self.pot_a.setValue(0.65)
        self.pot_w.setValue(10.0)
        self.pot_rw.setValue(1.2)
        self.pot_aw.setValue(0.65)
        self.pot_rc.setValue(1.3)

    def generate_input(self):
        """Generate FRESCO input text from form values"""
        # Collect basic parameters for the &FRESCO namelist
        basic_params = {
            'hcm': self.hcm.value(),
            'rmatch': self.rmatch.value(),
            'absend': self.absend.value(),
            'thmax': self.thmax.value(),
            'jtmax': self.jtmax.value(),
            'thinc': self.thinc.value(),
            'elab': self.elab.value(),
            'iter': self.iter.value(),
        }

        # Generate &FRESCO namelist with advanced parameters
        fresco_namelist = self.advanced_params.generate_namelist_text(basic_params)

        # Build complete input file
        input_text = f"""! {self.header.text()}
! Generated by FRESCO Quantum Studio

{fresco_namelist}

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

        # Header with preset
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_label = QLabel("Inelastic Scattering Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007AFF;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        preset_btn = QPushButton("Load Preset Example")
        preset_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #30B956;
            }
        """)
        preset_btn.clicked.connect(self.load_preset)
        header_layout.addWidget(preset_btn)

        main_layout.addWidget(header_widget)

        info_label = QLabel("Configure inelastic scattering to excited states")
        info_label.setStyleSheet("color: #6c757d; font-style: italic;")
        main_layout.addWidget(info_label)

        # General Parameters
        general_group = QGroupBox("General FRESCO Parameters")
        general_layout = QFormLayout()

        self.header = QLineEdit("Alpha + 12C inelastic to 2+ state")
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

        self.thmax = QDoubleSpinBox()
        self.thmax.setRange(0.0, 180.0)
        self.thmax.setValue(180.0)
        general_layout.addRow("Maximum angle (thmax):", self.thmax)

        self.jtmax = QSpinBox()
        self.jtmax.setRange(1, 200)
        self.jtmax.setValue(60)
        general_layout.addRow("Maximum J (jtmax):", self.jtmax)

        self.thinc = QDoubleSpinBox()
        self.thinc.setRange(0.1, 10.0)
        self.thinc.setValue(2.0)
        general_layout.addRow("Angle increment (thinc):", self.thinc)

        self.elab = QDoubleSpinBox()
        self.elab.setRange(0.1, 1000.0)
        self.elab.setValue(30.0)
        general_layout.addRow("Lab energy (elab) [MeV]:", self.elab)

        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)

        # Particles
        part_group = QGroupBox("Projectile and Target")
        part_layout = QFormLayout()

        self.proj_name = QLineEdit("alpha")
        part_layout.addRow("Projectile name:", self.proj_name)

        self.proj_mass = QDoubleSpinBox()
        self.proj_mass.setRange(0.001, 300.0)
        self.proj_mass.setDecimals(4)
        self.proj_mass.setValue(4.0)
        part_layout.addRow("Projectile mass (amu):", self.proj_mass)

        self.proj_charge = QDoubleSpinBox()
        self.proj_charge.setRange(0.0, 100.0)
        self.proj_charge.setValue(2.0)
        part_layout.addRow("Projectile charge:", self.proj_charge)

        part_layout.addRow(QLabel(""))  # Spacer

        self.targ_name = QLineEdit("12C")
        part_layout.addRow("Target name:", self.targ_name)

        self.targ_mass = QDoubleSpinBox()
        self.targ_mass.setRange(0.001, 300.0)
        self.targ_mass.setDecimals(4)
        self.targ_mass.setValue(12.0)
        part_layout.addRow("Target mass (amu):", self.targ_mass)

        self.targ_charge = QDoubleSpinBox()
        self.targ_charge.setRange(0.0, 100.0)
        self.targ_charge.setValue(6.0)
        part_layout.addRow("Target charge:", self.targ_charge)

        part_group.setLayout(part_layout)
        main_layout.addWidget(part_group)

        # Excited State Parameters
        excited_group = QGroupBox("Excited State Configuration")
        excited_layout = QFormLayout()

        self.exc_spin = QDoubleSpinBox()
        self.exc_spin.setRange(0.0, 20.0)
        self.exc_spin.setSingleStep(0.5)
        self.exc_spin.setValue(2.0)
        self.exc_spin.setToolTip("Spin of the excited state (e.g., 2+ state = 2.0)")
        excited_layout.addRow("Excited state spin:", self.exc_spin)

        self.exc_energy = QDoubleSpinBox()
        self.exc_energy.setRange(0.0, 50.0)
        self.exc_energy.setDecimals(3)
        self.exc_energy.setValue(4.439)
        self.exc_energy.setToolTip("Excitation energy in MeV")
        excited_layout.addRow("Excitation energy (MeV):", self.exc_energy)

        self.lambda_multipolarity = QSpinBox()
        self.lambda_multipolarity.setRange(0, 10)
        self.lambda_multipolarity.setValue(2)
        self.lambda_multipolarity.setToolTip("Multipolarity of transition (λ)")
        excited_layout.addRow("Multipolarity (λ):", self.lambda_multipolarity)

        excited_group.setLayout(excited_layout)
        main_layout.addWidget(excited_group)

        # Deformation Parameters
        deform_group = QGroupBox("Collective Model / Deformation")
        deform_layout = QFormLayout()

        self.beta = QDoubleSpinBox()
        self.beta.setRange(0.0, 2.0)
        self.beta.setDecimals(4)
        self.beta.setValue(0.5)
        self.beta.setToolTip("Deformation parameter β")
        deform_layout.addRow("Deformation β:", self.beta)

        self.deform_radius = QDoubleSpinBox()
        self.deform_radius.setRange(0.1, 5.0)
        self.deform_radius.setDecimals(2)
        self.deform_radius.setValue(1.2)
        deform_layout.addRow("Deformation radius (fm):", self.deform_radius)

        deform_group.setLayout(deform_layout)
        main_layout.addWidget(deform_group)

        # Optical Potentials (simplified)
        pot_group = QGroupBox("Optical Potential (Ground State)")
        pot_layout = QFormLayout()

        self.pot_v = QDoubleSpinBox()
        self.pot_v.setRange(-500.0, 500.0)
        self.pot_v.setValue(100.0)
        pot_layout.addRow("Real depth V (MeV):", self.pot_v)

        self.pot_r = QDoubleSpinBox()
        self.pot_r.setRange(0.1, 5.0)
        self.pot_r.setDecimals(2)
        self.pot_r.setValue(1.2)
        pot_layout.addRow("Radius r0 (fm):", self.pot_r)

        self.pot_a = QDoubleSpinBox()
        self.pot_a.setRange(0.1, 2.0)
        self.pot_a.setDecimals(2)
        self.pot_a.setValue(0.65)
        pot_layout.addRow("Diffuseness a (fm):", self.pot_a)

        self.pot_w = QDoubleSpinBox()
        self.pot_w.setRange(-500.0, 500.0)
        self.pot_w.setValue(20.0)
        pot_layout.addRow("Imaginary depth W (MeV):", self.pot_w)

        pot_group.setLayout(pot_layout)
        main_layout.addWidget(pot_group)

        # Advanced FRESCO Parameters
        self.advanced_params = AdvancedParametersWidget()
        main_layout.addWidget(self.advanced_params)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def load_preset(self):
        """Load preset example for 12C(α,α')12C* 2+ state"""
        self.header.setText("Alpha + 12C inelastic to 2+ state at 4.439 MeV")
        self.hcm.setValue(0.05)
        self.rmatch.setValue(30.0)
        self.thmax.setValue(180.0)
        self.jtmax.setValue(60)
        self.thinc.setValue(2.0)
        self.elab.setValue(30.0)

        self.proj_name.setText("alpha")
        self.proj_mass.setValue(4.0)
        self.proj_charge.setValue(2.0)

        self.targ_name.setText("12C")
        self.targ_mass.setValue(12.0)
        self.targ_charge.setValue(6.0)

        self.exc_spin.setValue(2.0)
        self.exc_energy.setValue(4.439)
        self.lambda_multipolarity.setValue(2)

        self.beta.setValue(0.5)
        self.deform_radius.setValue(1.2)

        self.pot_v.setValue(100.0)
        self.pot_r.setValue(1.2)
        self.pot_a.setValue(0.65)
        self.pot_w.setValue(20.0)

    def generate_input(self):
        """Generate FRESCO input text for inelastic scattering"""
        # Collect basic parameters for the &FRESCO namelist
        basic_params = {
            'hcm': self.hcm.value(),
            'rmatch': self.rmatch.value(),
            'thmax': self.thmax.value(),
            'jtmax': self.jtmax.value(),
            'thinc': self.thinc.value(),
            'elab': self.elab.value(),
            'chans': 1,
            'smats': 2,
            'xstabl': 1,
        }

        # Generate &FRESCO namelist with advanced parameters
        fresco_namelist = self.advanced_params.generate_namelist_text(basic_params)

        # Build complete input file
        input_text = f"""! {self.header.text()}
! Generated by FRESCO Quantum Studio

{fresco_namelist}

! Ground state partition
&PARTITION
namep='{self.proj_name.text()}'
massp={self.proj_mass.value()}
zp={self.proj_charge.value()}
namet='{self.targ_name.text()}'
masst={self.targ_mass.value()}
zt={self.targ_charge.value()}
qval=0.0
/

! Ground state
&STATES
jp=0.0
bandp=1
ep=0.0
cpot=1
jt=0.0
bandt=1
et=0.0
/

! Excited state partition (same particles)
&PARTITION
namep='{self.proj_name.text()}'
massp={self.proj_mass.value()}
zp={self.proj_charge.value()}
namet='{self.targ_name.text()}'
masst={self.targ_mass.value()}
zt={self.targ_charge.value()}
qval=-{self.exc_energy.value()}
/

! Excited state
&STATES
jp=0.0
bandp=1
ep=0.0
cpot=2
jt={self.exc_spin.value()}
bandt=2
et={self.exc_energy.value()}
/

! Optical potential for ground state
&POT
kp=1
type=1
p1={self.pot_v.value()}
p2={self.pot_r.value()}
p3={self.pot_a.value()}
/

&POT
kp=1
type=2
p1={self.pot_w.value()}
p2={self.pot_r.value()}
p3={self.pot_a.value()}
/

! Optical potential for excited state (same form)
&POT
kp=2
type=1
p1={self.pot_v.value()}
p2={self.pot_r.value()}
p3={self.pot_a.value()}
/

&POT
kp=2
type=2
p1={self.pot_w.value()}
p2={self.pot_r.value()}
p3={self.pot_a.value()}
/

! Coupling potential (deformation)
&POT
kp=3
type=8
p1={self.beta.value()}
p2={self.deform_radius.value()}
p3={self.pot_a.value()}
/

! Coupling between ground and excited state
&COUPLING
icto=2
icfrom=1
kind=3
ip1=0
ip2=3
p1={self.lambda_multipolarity.value()}
/
"""
        return input_text


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

        # Header with preset
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_label = QLabel("Transfer Reaction Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007AFF;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        preset_btn = QPushButton("Load Preset Example")
        preset_btn.setStyleSheet("""
            QPushButton {
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #30B956;
            }
        """)
        preset_btn.clicked.connect(self.load_preset)
        header_layout.addWidget(preset_btn)

        main_layout.addWidget(header_widget)

        info_label = QLabel("Configure one-nucleon or cluster transfer reactions (DWBA)")
        info_label.setStyleSheet("color: #6c757d; font-style: italic;")
        main_layout.addWidget(info_label)

        # General Parameters
        general_group = QGroupBox("General FRESCO Parameters")
        general_layout = QFormLayout()

        self.header = QLineEdit("Deuteron + 40Ca -> proton + 41Ca (d,p) reaction")
        general_layout.addRow("Header:", self.header)

        self.hcm = QDoubleSpinBox()
        self.hcm.setRange(0.001, 1.0)
        self.hcm.setDecimals(3)
        self.hcm.setValue(0.1)
        general_layout.addRow("Integration step (hcm):", self.hcm)

        self.rmatch = QDoubleSpinBox()
        self.rmatch.setRange(1.0, 200.0)
        self.rmatch.setValue(20.0)
        general_layout.addRow("Matching radius (rmatch):", self.rmatch)

        self.thmax = QDoubleSpinBox()
        self.thmax.setRange(0.0, 180.0)
        self.thmax.setValue(180.0)
        general_layout.addRow("Maximum angle (thmax):", self.thmax)

        self.jtmax = QSpinBox()
        self.jtmax.setRange(1, 200)
        self.jtmax.setValue(50)
        general_layout.addRow("Maximum J (jtmax):", self.jtmax)

        self.thinc = QDoubleSpinBox()
        self.thinc.setRange(0.1, 10.0)
        self.thinc.setValue(5.0)
        general_layout.addRow("Angle increment (thinc):", self.thinc)

        self.elab = QDoubleSpinBox()
        self.elab.setRange(0.1, 1000.0)
        self.elab.setValue(15.0)
        general_layout.addRow("Lab energy (elab) [MeV]:", self.elab)

        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)

        # Entrance Channel (a + A)
        entrance_group = QGroupBox("Entrance Channel (a + A)")
        entrance_layout = QFormLayout()

        self.proj_name = QLineEdit("d")
        entrance_layout.addRow("Projectile (a) name:", self.proj_name)

        self.proj_mass = QDoubleSpinBox()
        self.proj_mass.setRange(0.001, 300.0)
        self.proj_mass.setDecimals(4)
        self.proj_mass.setValue(2.0)
        entrance_layout.addRow("Projectile mass (amu):", self.proj_mass)

        self.proj_charge = QDoubleSpinBox()
        self.proj_charge.setRange(0.0, 100.0)
        self.proj_charge.setValue(1.0)
        entrance_layout.addRow("Projectile charge:", self.proj_charge)

        entrance_layout.addRow(QLabel(""))  # Spacer

        self.targ_name = QLineEdit("40Ca")
        entrance_layout.addRow("Target (A) name:", self.targ_name)

        self.targ_mass = QDoubleSpinBox()
        self.targ_mass.setRange(0.001, 300.0)
        self.targ_mass.setDecimals(4)
        self.targ_mass.setValue(40.0)
        entrance_layout.addRow("Target mass (amu):", self.targ_mass)

        self.targ_charge = QDoubleSpinBox()
        self.targ_charge.setRange(0.0, 100.0)
        self.targ_charge.setValue(20.0)
        entrance_layout.addRow("Target charge:", self.targ_charge)

        entrance_group.setLayout(entrance_layout)
        main_layout.addWidget(entrance_group)

        # Exit Channel (b + B)
        exit_group = QGroupBox("Exit Channel (b + B)")
        exit_layout = QFormLayout()

        self.eject_name = QLineEdit("p")
        exit_layout.addRow("Ejectile (b) name:", self.eject_name)

        self.eject_mass = QDoubleSpinBox()
        self.eject_mass.setRange(0.001, 300.0)
        self.eject_mass.setDecimals(4)
        self.eject_mass.setValue(1.0078)
        exit_layout.addRow("Ejectile mass (amu):", self.eject_mass)

        self.eject_charge = QDoubleSpinBox()
        self.eject_charge.setRange(0.0, 100.0)
        self.eject_charge.setValue(1.0)
        exit_layout.addRow("Ejectile charge:", self.eject_charge)

        exit_layout.addRow(QLabel(""))  # Spacer

        self.resid_name = QLineEdit("41Ca")
        exit_layout.addRow("Residual (B) name:", self.resid_name)

        self.resid_mass = QDoubleSpinBox()
        self.resid_mass.setRange(0.001, 300.0)
        self.resid_mass.setDecimals(4)
        self.resid_mass.setValue(41.0)
        exit_layout.addRow("Residual mass (amu):", self.resid_mass)

        self.resid_charge = QDoubleSpinBox()
        self.resid_charge.setRange(0.0, 100.0)
        self.resid_charge.setValue(20.0)
        exit_layout.addRow("Residual charge:", self.resid_charge)

        exit_layout.addRow(QLabel(""))  # Spacer

        self.qvalue = QDoubleSpinBox()
        self.qvalue.setRange(-50.0, 50.0)
        self.qvalue.setDecimals(3)
        self.qvalue.setValue(5.08)
        self.qvalue.setToolTip("Q-value of reaction in MeV (positive for exothermic)")
        exit_layout.addRow("Q-value (MeV):", self.qvalue)

        exit_group.setLayout(exit_layout)
        main_layout.addWidget(exit_group)

        # Transferred Particle
        transfer_group = QGroupBox("Transferred Particle (x)")
        transfer_layout = QFormLayout()

        self.trans_name = QLineEdit("n")
        transfer_layout.addRow("Particle name:", self.trans_name)

        self.trans_mass = QDoubleSpinBox()
        self.trans_mass.setRange(0.001, 300.0)
        self.trans_mass.setDecimals(4)
        self.trans_mass.setValue(1.0087)
        transfer_layout.addRow("Mass (amu):", self.trans_mass)

        self.trans_charge = QDoubleSpinBox()
        self.trans_charge.setRange(0.0, 100.0)
        self.trans_charge.setValue(0.0)
        transfer_layout.addRow("Charge:", self.trans_charge)

        transfer_layout.addRow(QLabel(""))  # Spacer

        self.trans_l = QSpinBox()
        self.trans_l.setRange(0, 20)
        self.trans_l.setValue(1)
        self.trans_l.setToolTip("Orbital angular momentum of transferred particle")
        transfer_layout.addRow("Orbital L:", self.trans_l)

        self.trans_j = QDoubleSpinBox()
        self.trans_j.setRange(0.0, 20.0)
        self.trans_j.setSingleStep(0.5)
        self.trans_j.setValue(0.5)
        self.trans_j.setToolTip("Total angular momentum j = l ± 1/2")
        transfer_layout.addRow("Total j:", self.trans_j)

        self.trans_nodes = QSpinBox()
        self.trans_nodes.setRange(0, 20)
        self.trans_nodes.setValue(0)
        self.trans_nodes.setToolTip("Number of radial nodes")
        transfer_layout.addRow("Radial nodes (n-1):", self.trans_nodes)

        self.binding_energy = QDoubleSpinBox()
        self.binding_energy.setRange(0.0, 50.0)
        self.binding_energy.setDecimals(3)
        self.binding_energy.setValue(2.224)
        self.binding_energy.setToolTip("Binding energy of transferred particle")
        transfer_layout.addRow("Binding energy (MeV):", self.binding_energy)

        transfer_group.setLayout(transfer_layout)
        main_layout.addWidget(transfer_group)

        # Optical Potentials (simplified)
        pot_group = QGroupBox("Optical Potential Parameters")
        pot_layout = QFormLayout()

        pot_layout.addRow(QLabel("Entrance channel (a+A):"))

        self.ent_v = QDoubleSpinBox()
        self.ent_v.setRange(-500.0, 500.0)
        self.ent_v.setValue(80.0)
        pot_layout.addRow("  Real depth V (MeV):", self.ent_v)

        self.ent_w = QDoubleSpinBox()
        self.ent_w.setRange(-500.0, 500.0)
        self.ent_w.setValue(10.0)
        pot_layout.addRow("  Imag depth W (MeV):", self.ent_w)

        pot_layout.addRow(QLabel("\nExit channel (b+B):"))

        self.exit_v = QDoubleSpinBox()
        self.exit_v.setRange(-500.0, 500.0)
        self.exit_v.setValue(60.0)
        pot_layout.addRow("  Real depth V (MeV):", self.exit_v)

        self.exit_w = QDoubleSpinBox()
        self.exit_w.setRange(-500.0, 500.0)
        self.exit_w.setValue(8.0)
        pot_layout.addRow("  Imag depth W (MeV):", self.exit_w)

        pot_group.setLayout(pot_layout)
        main_layout.addWidget(pot_group)

        # Advanced FRESCO Parameters
        self.advanced_params = AdvancedParametersWidget()
        main_layout.addWidget(self.advanced_params)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def load_preset(self):
        """Load preset example for d(40Ca,p)41Ca stripping reaction"""
        self.header.setText("40Ca(d,p)41Ca neutron transfer reaction")
        self.hcm.setValue(0.1)
        self.rmatch.setValue(20.0)
        self.thmax.setValue(180.0)
        self.jtmax.setValue(50)
        self.thinc.setValue(5.0)
        self.elab.setValue(15.0)

        # Entrance
        self.proj_name.setText("d")
        self.proj_mass.setValue(2.0)
        self.proj_charge.setValue(1.0)
        self.targ_name.setText("40Ca")
        self.targ_mass.setValue(40.0)
        self.targ_charge.setValue(20.0)

        # Exit
        self.eject_name.setText("p")
        self.eject_mass.setValue(1.0078)
        self.eject_charge.setValue(1.0)
        self.resid_name.setText("41Ca")
        self.resid_mass.setValue(41.0)
        self.resid_charge.setValue(20.0)
        self.qvalue.setValue(5.08)

        # Transfer
        self.trans_name.setText("n")
        self.trans_mass.setValue(1.0087)
        self.trans_charge.setValue(0.0)
        self.trans_l.setValue(1)
        self.trans_j.setValue(0.5)
        self.trans_nodes.setValue(0)
        self.binding_energy.setValue(2.224)

        # Potentials
        self.ent_v.setValue(80.0)
        self.ent_w.setValue(10.0)
        self.exit_v.setValue(60.0)
        self.exit_w.setValue(8.0)

    def generate_input(self):
        """Generate FRESCO input text for transfer reaction"""
        # Collect basic parameters for the &FRESCO namelist
        basic_params = {
            'hcm': self.hcm.value(),
            'rmatch': self.rmatch.value(),
            'thmax': self.thmax.value(),
            'jtmax': self.jtmax.value(),
            'thinc': self.thinc.value(),
            'elab': self.elab.value(),
            'chans': 1,
            'smats': 2,
            'xstabl': 1,
            'iter': 1,
        }

        # Generate &FRESCO namelist with advanced parameters
        fresco_namelist = self.advanced_params.generate_namelist_text(basic_params)

        # Build complete input file
        input_text = f"""! {self.header.text()}
! Generated by FRESCO Quantum Studio - Transfer Reaction

{fresco_namelist}

! Entrance channel: {self.proj_name.text()} + {self.targ_name.text()}
&PARTITION
namep='{self.proj_name.text()}'
massp={self.proj_mass.value()}
zp={self.proj_charge.value()}
namet='{self.targ_name.text()}'
masst={self.targ_mass.value()}
zt={self.targ_charge.value()}
qval=0.0
/

! Entrance channel state
&STATES
jp=0.5
bandp=1
ep=0.0
cpot=1
jt=0.0
bandt=1
et=0.0
/

! Exit channel: {self.eject_name.text()} + {self.resid_name.text()}
&PARTITION
namep='{self.eject_name.text()}'
massp={self.eject_mass.value()}
zp={self.eject_charge.value()}
namet='{self.resid_name.text()}'
masst={self.resid_mass.value()}
zt={self.resid_charge.value()}
qval={self.qvalue.value()}
nex=1
/

! Exit channel state
&STATES
jp=0.5
bandp=2
ep=0.0
cpot=2
jt={self.trans_j.value()}
bandt=2
et=0.0
/

! Optical potential - entrance channel
&POT
kp=1
type=1
p1={self.ent_v.value()}
p2=1.17
p3=0.75
/

&POT
kp=1
type=2
p1={self.ent_w.value()}
p2=1.32
p3=0.51
/

! Optical potential - exit channel
&POT
kp=2
type=1
p1={self.exit_v.value()}
p2=1.25
p3=0.65
/

&POT
kp=2
type=2
p1={self.exit_w.value()}
p2=1.25
p3=0.47
/

! Binding potential for transferred particle
&POT
kp=3
type=1
shape=0
p1=50.0
p2=1.25
p3=0.65
/

! Overlap for entrance partition (projectile structure)
&OVERLAP
kn1=1
ic1=1
ic2=1
kind=0
/

! Overlap for transfer (defines transferred particle)
&OVERLAP
kn1=2
ic1=1
ic2=2
kind=7
ch1=1
ch2=2
nn={self.trans_nodes.value() + 1}
l={self.trans_l.value()}
j={self.trans_j.value()}
kbpot=3
be={self.binding_energy.value()}
isc=1
ipc=1
/

! Coupling for transfer
&COUPLING
icto=2
icfrom=1
kind=7
ip1=0
ip2=0
/
"""
        return input_text


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
        self.calc_tabs.addTab(self.elastic_form, "⚛️ Elastic Scattering")

        self.inelastic_form = InelasticScatteringForm()
        self.calc_tabs.addTab(self.inelastic_form, "🌟 Inelastic Scattering")

        self.transfer_form = TransferReactionForm()
        self.calc_tabs.addTab(self.transfer_form, "🔄 Transfer Reactions")

        layout.addWidget(self.calc_tabs)

        # Footer with hints
        footer = QLabel("💡 Tip: Fill in the parameters above, or use 'Load Preset Example' to get started quickly.")
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

        # Show confirmation
        QMessageBox.information(self, "Input Generated",
                              "FRESCO input file has been generated!\n\n"
                              "Switch to the 'Text Editor' tab to view and edit it.")

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
