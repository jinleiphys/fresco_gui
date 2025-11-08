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
from pot_widget import PotentialManagerWidget
from parameter_manager import ParameterManager
from dynamic_general_params_widget import DynamicGeneralParametersWidget
from energy_array_widget import EnergyArrayWidget


class ElasticScatteringForm(QWidget):
    """Form for elastic scattering calculations"""

    def __init__(self):
        super().__init__()
        print("[ElasticForm] __init__ called", flush=True)
        # Create parameter manager for elastic scattering
        self.param_manager = ParameterManager(calculation_type="elastic")
        print(f"[ElasticForm] ParameterManager created, general params: {self.param_manager.get_general_parameters()}", flush=True)
        self.init_ui()
        print("[ElasticForm] init_ui() completed", flush=True)

        # Load default preset on initialization
        self.load_preset()
        print("[ElasticForm] Default preset loaded", flush=True)

    def update_from_input_file(self, input_text: str):
        """
        Update form and parameter categorization based on loaded input file

        Args:
            input_text: Content of the loaded FRESCO input file
        """
        from parameter_manager import (
            parse_fresco_input_parameters,
            parse_fresco_parameter_values,
            parse_partition_namelist
        )

        print("\n" + "="*60)
        print("[ElasticForm] Starting update_from_input_file")
        print("="*60)

        # Parse parameters from the input file
        file_params = parse_fresco_input_parameters(input_text)
        param_values = parse_fresco_parameter_values(input_text)
        partition_info = parse_partition_namelist(input_text)

        print(f"\n[ElasticForm] Parsed {len(file_params)} parameter names from file:")
        print(f"  {sorted(file_params)}")
        print(f"\n[ElasticForm] Parsed {len(param_values)} parameter values from file:")
        for k, v in sorted(param_values.items()):
            print(f"  {k} = {v}")
        print(f"\n[ElasticForm] Parsed partition info:")
        for k, v in partition_info.items():
            print(f"  {k} = {v}")

        # Update parameter manager
        print(f"\n[ElasticForm] Updating parameter manager...")
        self.param_manager.update_from_input_file(file_params)

        # IMPORTANT: Refresh UI first (this rebuilds widgets for both general and advanced)
        print(f"\n[ElasticForm] Refreshing general parameters widget...", flush=True)
        try:
            print(f"[ElasticForm] Calling general_params.refresh()...", flush=True)
            self.general_params.refresh()
            print(f"[ElasticForm] Returned from general_params.refresh()", flush=True)
            print(f"[ElasticForm] General params refresh complete", flush=True)
        except Exception as e:
            print(f"[ElasticForm] ERROR in general_params.refresh(): {e}", flush=True)
            import traceback
            traceback.print_exc()

        print(f"\n[ElasticForm] Refreshing advanced parameters widget...", flush=True)
        try:
            self.advanced_params.refresh()
            print(f"[ElasticForm] Advanced params refresh complete", flush=True)
        except Exception as e:
            print(f"[ElasticForm] ERROR in advanced_params.refresh(): {e}", flush=True)
            import traceback
            traceback.print_exc()

        # THEN populate all FRESCO parameters with values
        print(f"\n[ElasticForm] Populating all FRESCO parameters...", flush=True)
        try:
            for param_name, param_value in param_values.items():
                print(f"  Processing {param_name} = {param_value}...", flush=True)
                # Try to set in general params first, then advanced
                if param_name in self.general_params.parameter_widgets:
                    self.general_params.set_parameter_value(param_name, param_value)
                else:
                    self.advanced_params.set_parameter_value(param_name, param_value)
            print(f"[ElasticForm] All FRESCO parameters populated", flush=True)
        except Exception as e:
            print(f"[ElasticForm] ERROR populating parameters: {e}", flush=True)
            import traceback
            traceback.print_exc()

        # Populate partition information (projectile and target)
        print(f"\n[ElasticForm] Populating partition information...", flush=True)
        try:
            if 'namep' in partition_info:
                self.proj_name.setText(partition_info['namep'])
                print(f"  Set proj_name = {partition_info['namep']}", flush=True)
            if 'massp' in partition_info:
                self.proj_mass.setValue(partition_info['massp'])
                print(f"  Set proj_mass = {partition_info['massp']}", flush=True)
            if 'zp' in partition_info:
                self.proj_charge.setValue(partition_info['zp'])
                print(f"  Set proj_charge = {partition_info['zp']}", flush=True)
            if 'jp' in partition_info:
                self.proj_spin.setValue(partition_info['jp'])
                print(f"  Set proj_spin = {partition_info['jp']}", flush=True)

            if 'namet' in partition_info:
                self.targ_name.setText(partition_info['namet'])
                print(f"  Set targ_name = {partition_info['namet']}", flush=True)
            if 'masst' in partition_info:
                self.targ_mass.setValue(partition_info['masst'])
                print(f"  Set targ_mass = {partition_info['masst']}", flush=True)
            if 'zt' in partition_info:
                self.targ_charge.setValue(partition_info['zt'])
                print(f"  Set targ_charge = {partition_info['zt']}", flush=True)
            if 'jt' in partition_info:
                self.targ_spin.setValue(partition_info['jt'])
                print(f"  Set targ_spin = {partition_info['jt']}", flush=True)
        except Exception as e:
            print(f"[ElasticForm] ERROR populating partition: {e}", flush=True)
            import traceback
            traceback.print_exc()

        # Update header from first line of input file
        try:
            first_line = input_text.strip().split('\n')[0].strip()
            # Remove leading '!' if present
            if first_line.startswith('!'):
                first_line = first_line[1:].strip()
            self.header.setText(first_line)
            print(f"  Set header from file = {first_line}", flush=True)
        except Exception as e:
            print(f"  Could not extract header from file, using default: {e}", flush=True)
            # Fallback: generate from partition info
            if 'namep' in partition_info and 'namet' in partition_info:
                header = f"{partition_info['namep']} + {partition_info['namet']} elastic scattering"
                self.header.setText(header)
                print(f"  Set header from partition = {header}", flush=True)

        # Parse and load energy array (elab/nlab)
        print(f"\n[ElasticForm] Parsing energy array...", flush=True)
        try:
            self.energy_widget.parse_fresco_format(input_text)
            boundaries, intervals = self.energy_widget.get_boundaries_and_intervals()
            print(f"  Loaded {len(boundaries)} energy boundaries: {boundaries}", flush=True)
            print(f"  With {len(intervals)} intervals: {intervals}", flush=True)
        except Exception as e:
            print(f"[ElasticForm] ERROR parsing energies: {e}", flush=True)
            import traceback
            traceback.print_exc()

        # Load POT information into potential manager
        print(f"\n[ElasticForm] Loading POT information...", flush=True)
        self.pot_manager.load_from_input_text(input_text)

        print(f"\n[ElasticForm] Update complete. Promoted parameters: {self.param_manager.get_categorization_summary()['promoted_params']}", flush=True)
        print("="*60 + "\n", flush=True)


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
        header_label.setObjectName("sectionHeader")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        preset_btn = QPushButton("Load Preset Example")
        preset_btn.setObjectName("presetButton")
        preset_btn.clicked.connect(self.load_preset)
        header_layout.addWidget(preset_btn)

        main_layout.addWidget(header_widget)

        # Header field (not a FRESCO parameter)
        header_group = QGroupBox("Calculation Description")
        header_layout = QFormLayout()
        header_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        header_layout.setLabelAlignment(Qt.AlignLeft)

        self.header = QLineEdit("Alpha + 12C elastic scattering at 30 MeV")
        self.header.setAlignment(Qt.AlignLeft)
        header_layout.addRow("Header:", self.header)

        header_group.setLayout(header_layout)
        main_layout.addWidget(header_group)

        # Dynamic General FRESCO Parameters
        self.general_params = DynamicGeneralParametersWidget(parameter_manager=self.param_manager)
        main_layout.addWidget(self.general_params)

        # Energy Array Widget (for elab/nlab) - integrated into General Parameters
        self.energy_widget = EnergyArrayWidget()
        # Insert energy widget into the General Parameters group box
        self.general_params.group_box.layout().addWidget(self.energy_widget)

        # Projectile Parameters
        proj_group = QGroupBox("Projectile (Incoming Particle)")
        proj_layout = QFormLayout()
        proj_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        proj_layout.setLabelAlignment(Qt.AlignLeft)

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
        targ_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        targ_layout.setLabelAlignment(Qt.AlignLeft)

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

        # Optical Potentials Manager
        self.pot_manager = PotentialManagerWidget()
        main_layout.addWidget(self.pot_manager)

        # Advanced FRESCO Parameters (with parameter manager)
        self.advanced_params = AdvancedParametersWidget(parameter_manager=self.param_manager)
        main_layout.addWidget(self.advanced_params)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def load_preset(self):
        """Load preset example from p+Ni78 elastic scattering"""
        # Use the actual example file content (single-line header as required by FRESCO)
        preset_input = """p+Ni78 Coulomb and Nuclear elastic scattering
NAMELIST
 &FRESCO hcm=0.1 rmatch=60
	 jtmin=0.0 jtmax=50 absend= 0.0010
	 thmin=0.00 thmax=180.00 thinc=1.00
 	 chans=1 smats=2  xstabl=1
	 elab(1:3)=6.9 11.00 49.350  nlab(1:3)=1 1 /

 &PARTITION namep='p' massp=1.00 zp=1
 	    namet='Ni78' masst=78.0000 zt=28 qval=-0.000 nex=1  /
 &STATES jp=0.5 bandp=1 ep=0.0000 cpot=1 jt=0.0 bandt=1 et=0.0000  /
 &partition /

 &POT kp=1 ap=1.000 at=78.000 rc=1.2  /
 &POT kp=1 type=1 p1=40.00 p2=1.2 p3=0.65 p4=10.0 p5=1.2 p6=0.500  /
 &pot /
 &overlap /
 &coupling /
"""
        # Load using the same method as file loading
        self.update_from_input_file(preset_input)

        # Expand/activate the POT group box and individual POT components
        self.pot_manager.group_box.setChecked(True)
        for pot_widget in self.pot_manager.potential_widgets:
            pot_widget.group_box.setChecked(True)

    def generate_input(self):
        """Generate FRESCO input text from form values"""
        # Collect parameters from general parameters widget
        general_params = self.general_params.get_parameter_values()

        # DEBUG: Print what we got
        print(f"\n[ElasticForm.generate_input] DEBUG:")
        print(f"  General params from widget: {general_params}")
        print(f"  Parameter manager general params: {self.param_manager.get_general_parameters()}")
        print(f"  Widget dict keys: {list(self.general_params.parameter_widgets.keys())}")

        # Remove elab and nlab from general_params (handled by energy widget)
        general_params_filtered = {k: v for k, v in general_params.items() if k not in ['elab', 'nlab']}

        # Generate &FRESCO namelist with general and advanced parameters
        fresco_namelist = self.advanced_params.generate_namelist_text(general_params_filtered)

        # Insert energy array into the namelist (before the closing /)
        energy_string = self.energy_widget.get_fresco_format()
        print(f"  Energy string generated: '{energy_string}'", flush=True)

        # Insert energy line before the closing '/'
        fresco_namelist = fresco_namelist.rsplit('/', 1)[0] + f"     {energy_string} /"
        print(f"  Namelist after energy insertion (first 500 chars):", flush=True)
        print(f"  {fresco_namelist[:500]}", flush=True)

        # Generate &POT namelists from potential manager
        pot_namelists = self.pot_manager.generate_pot_namelists()

        # Build complete input file (single-line header as required by FRESCO)
        input_text = f"""{self.header.text()}
NAMELIST
{fresco_namelist}

 &PARTITION namep='{self.proj_name.text()}' massp={self.proj_mass.value()} zp={self.proj_charge.value()} namet='{self.targ_name.text()}' masst={self.targ_mass.value()} zt={self.targ_charge.value()} qval=0.0 nex=1  /
 &STATES jp={self.proj_spin.value()} bandp=1 ep=0.0 cpot=1 jt={self.targ_spin.value()} bandt=1 et=0.0  /
 &partition /

{pot_namelists}
 &pot /
 &overlap /
 &coupling /

! Generated by FRESCO Quantum Studio (Form Builder)
! Questions or issues? Contact: jinlei@fewbody.com
"""
        return input_text


class InelasticScatteringForm(QWidget):
    """Form for inelastic scattering calculations"""

    def __init__(self):
        super().__init__()
        # Create parameter manager for inelastic scattering
        self.param_manager = ParameterManager(calculation_type="inelastic")
        self.init_ui()

    def update_from_input_file(self, input_text: str):
        """
        Update form and parameter categorization based on loaded input file

        Args:
            input_text: Content of the loaded FRESCO input file
        """
        from parameter_manager import (
            parse_fresco_input_parameters,
            parse_fresco_parameter_values,
            parse_partition_namelist
        )

        print("\n" + "="*60)
        print("[InelasticForm] Starting update_from_input_file")
        print("="*60)

        # Parse parameters from the input file
        file_params = parse_fresco_input_parameters(input_text)
        param_values = parse_fresco_parameter_values(input_text)
        partition_info = parse_partition_namelist(input_text)

        print(f"\n[InelasticForm] Parsed {len(file_params)} parameter names from file")
        print(f"\n[InelasticForm] Parsed {len(param_values)} parameter values from file")
        print(f"\n[InelasticForm] Parsed partition info")

        # Update parameter manager
        print(f"\n[InelasticForm] Updating parameter manager...")
        self.param_manager.update_from_input_file(file_params)

        # IMPORTANT: Refresh UI first (this rebuilds widgets for both general and advanced)
        print(f"\n[InelasticForm] Refreshing general parameters widget...")
        self.general_params.refresh()
        print(f"[InelasticForm] General params refresh complete")

        print(f"\n[InelasticForm] Refreshing advanced parameters widget...")
        self.advanced_params.refresh()
        print(f"[InelasticForm] Advanced params refresh complete")

        # THEN populate all FRESCO parameters with values
        print(f"\n[InelasticForm] Populating all FRESCO parameters...")
        for param_name, param_value in param_values.items():
            # Try to set in general params first, then advanced
            if param_name in self.general_params.parameter_widgets:
                self.general_params.set_parameter_value(param_name, param_value)
            else:
                self.advanced_params.set_parameter_value(param_name, param_value)
        print(f"[InelasticForm] All FRESCO parameters populated")

        # Populate partition information
        print(f"\n[InelasticForm] Populating partition information...")
        if 'namep' in partition_info:
            self.proj_name.setText(partition_info['namep'])
        if 'massp' in partition_info:
            self.proj_mass.setValue(partition_info['massp'])
        if 'zp' in partition_info:
            self.proj_charge.setValue(partition_info['zp'])

        if 'namet' in partition_info:
            self.targ_name.setText(partition_info['namet'])
        if 'masst' in partition_info:
            self.targ_mass.setValue(partition_info['masst'])
        if 'zt' in partition_info:
            self.targ_charge.setValue(partition_info['zt'])

        # Update header from first line of input file
        try:
            first_line = input_text.strip().split('\n')[0].strip()
            if first_line.startswith('!'):
                first_line = first_line[1:].strip()
            self.header.setText(first_line)
        except Exception as e:
            if 'namep' in partition_info and 'namet' in partition_info:
                header = f"{partition_info['namep']} + {partition_info['namet']} inelastic scattering"
                self.header.setText(header)

        # Parse and load energy array
        print(f"\n[InelasticForm] Parsing energy array...")
        self.energy_widget.parse_fresco_format(input_text)

        # Load POT information
        print(f"\n[InelasticForm] Loading POT information...")
        self.pot_manager.load_from_input_text(input_text)

        print(f"\n[InelasticForm] Update complete. Promoted parameters: {self.param_manager.get_categorization_summary()['promoted_params']}")
        print("="*60 + "\n")

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
        header_label.setObjectName("sectionHeader")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        preset_btn = QPushButton("Load Preset Example")
        preset_btn.setObjectName("presetButton")
        preset_btn.clicked.connect(self.load_preset)
        header_layout.addWidget(preset_btn)

        main_layout.addWidget(header_widget)

        # Header field (not a FRESCO parameter)
        header_group = QGroupBox("Calculation Description")
        header_layout_inner = QFormLayout()
        header_layout_inner.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        header_layout_inner.setLabelAlignment(Qt.AlignLeft)

        self.header = QLineEdit("Alpha + 12C inelastic to 2+ state at 4.439 MeV")
        self.header.setAlignment(Qt.AlignLeft)
        header_layout_inner.addRow("Header:", self.header)

        header_group.setLayout(header_layout_inner)
        main_layout.addWidget(header_group)

        # Dynamic General FRESCO Parameters
        self.general_params = DynamicGeneralParametersWidget(parameter_manager=self.param_manager)
        main_layout.addWidget(self.general_params)

        # Energy Array Widget (for elab/nlab) - integrated into General Parameters
        self.energy_widget = EnergyArrayWidget()
        # Insert energy widget into the General Parameters group box
        self.general_params.group_box.layout().addWidget(self.energy_widget)

        # Projectile Parameters
        proj_group = QGroupBox("Projectile (Incoming Particle)")
        proj_layout = QFormLayout()
        proj_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        proj_layout.setLabelAlignment(Qt.AlignLeft)

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
        targ_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        targ_layout.setLabelAlignment(Qt.AlignLeft)

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

        # Excited State Parameters
        excited_group = QGroupBox("Excited State Configuration")
        excited_layout = QFormLayout()
        excited_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        excited_layout.setLabelAlignment(Qt.AlignLeft)

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
        deform_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        deform_layout.setLabelAlignment(Qt.AlignLeft)

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

        # Optical Potentials Manager
        self.pot_manager = PotentialManagerWidget()
        main_layout.addWidget(self.pot_manager)

        # Advanced FRESCO Parameters (with parameter manager)
        self.advanced_params = AdvancedParametersWidget(parameter_manager=self.param_manager)
        main_layout.addWidget(self.advanced_params)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def load_preset(self):
        """Load preset example for 12C(α,α')12C* 2+ state"""
        # Use the same approach as ElasticScatteringForm
        preset_input = """Alpha + 12C inelastic to 2+ state at 4.439 MeV
NAMELIST
 &FRESCO hcm=0.05 rmatch=30.0
	 jtmin=0.0 jtmax=60 absend= 0.0010
	 thmin=0.00 thmax=180.00 thinc=2.00
 	 chans=1 smats=2 xstabl=1
	 elab(1:1)=30.0 nlab(1:1)=1 /

 &PARTITION namep='alpha' massp=4.0 zp=2
 	    namet='12C' masst=12.0 zt=6 qval=0.0 nex=1  /
 &STATES jp=0.0 bandp=1 ep=0.0 cpot=1 jt=0.0 bandt=1 et=0.0  /
 &partition /

 &POT kp=1 type=0 ap=4.0 at=12.0 rc=1.25 /
 &POT kp=1 type=1 p1=100.0 p2=1.17 p3=0.75 p4=25.0 p5=1.32 p6=0.51 /
 &pot /
 &overlap /
 &coupling /
"""
        # Load using the same method as file loading
        self.update_from_input_file(preset_input)

        # Set inelastic-specific parameters
        self.exc_spin.setValue(2.0)
        self.exc_energy.setValue(4.439)
        self.lambda_multipolarity.setValue(2)
        self.beta.setValue(0.5)
        self.deform_radius.setValue(1.2)

        # Expand POT group box
        self.pot_manager.group_box.setChecked(True)
        for pot_widget in self.pot_manager.potential_widgets:
            pot_widget.group_box.setChecked(True)

    def generate_input(self):
        """Generate FRESCO input text for inelastic scattering"""
        # Collect parameters from general parameters widget
        general_params = self.general_params.get_parameter_values()

        # Remove elab and nlab from general_params (handled by energy widget)
        general_params_filtered = {k: v for k, v in general_params.items() if k not in ['elab', 'nlab']}

        # Generate &FRESCO namelist with general and advanced parameters
        fresco_namelist = self.advanced_params.generate_namelist_text(general_params_filtered)

        # Insert energy array into the namelist (before the closing /)
        energy_string = self.energy_widget.get_fresco_format()
        fresco_namelist = fresco_namelist.rsplit('/', 1)[0] + f"     {energy_string} /"

        # Generate &POT namelists from potential manager
        pot_namelists = self.pot_manager.generate_pot_namelists()

        # Build complete input file (single-line header as required by FRESCO)
        input_text = f"""{self.header.text()}
NAMELIST
{fresco_namelist}

 &PARTITION namep='{self.proj_name.text()}' massp={self.proj_mass.value()} zp={self.proj_charge.value()} namet='{self.targ_name.text()}' masst={self.targ_mass.value()} zt={self.targ_charge.value()} qval=0.0 nex=1  /
 &STATES jp={self.proj_spin.value()} bandp=1 ep=0.0 cpot=1 jt={self.targ_spin.value()} bandt=1 et=0.0  /
 &partition /

{pot_namelists}

&POT kp=3 type=8 p1={self.beta.value()} p2={self.deform_radius.value()} p3=0.65 /

 &pot /

&COUPLING icto=1 icfrom=1 kind=3 ip1=0 ip2=3 p1={self.lambda_multipolarity.value()} jt={self.exc_spin.value()} et={self.exc_energy.value()} /

 &coupling /
 &overlap /

! Generated by FRESCO Quantum Studio (Form Builder)
! Questions or issues? Contact: jinlei@fewbody.com
"""
        return input_text


class TransferReactionForm(QWidget):
    """Form for transfer reaction calculations"""

    def __init__(self):
        super().__init__()
        print("[TransferForm] __init__ called", flush=True)
        # Create parameter manager for transfer reactions
        self.param_manager = ParameterManager(calculation_type="transfer")
        print(f"[TransferForm] ParameterManager created, general params: {self.param_manager.get_general_parameters()}", flush=True)
        self.init_ui()
        print("[TransferForm] init_ui() completed", flush=True)

        # Load default preset on initialization
        self.load_preset()
        print("[TransferForm] Default preset loaded", flush=True)

    def update_from_input_file(self, input_text: str):
        """
        Update form and parameter categorization based on loaded input file

        Args:
            input_text: Content of the loaded FRESCO input file
        """
        from parameter_manager import (
            parse_fresco_input_parameters,
            parse_fresco_parameter_values,
            parse_partition_namelist
        )

        print("\n" + "="*60)
        print("[TransferForm] Starting update_from_input_file")
        print("="*60)

        # Parse parameters from the input file
        file_params = parse_fresco_input_parameters(input_text)
        param_values = parse_fresco_parameter_values(input_text)
        partition_info = parse_partition_namelist(input_text)

        print(f"\n[TransferForm] Parsed {len(file_params)} parameter names from file:")
        print(f"  {sorted(file_params)}")
        print(f"\n[TransferForm] Parsed {len(param_values)} parameter values from file:")
        for k, v in sorted(param_values.items()):
            print(f"  {k} = {v}")
        print(f"\n[TransferForm] Parsed partition info:")
        for k, v in partition_info.items():
            print(f"  {k} = {v}")

        # Update parameter manager
        print(f"\n[TransferForm] Updating parameter manager...")
        self.param_manager.update_from_input_file(file_params)

        # IMPORTANT: Refresh UI first (this rebuilds widgets for both general and advanced)
        print(f"\n[TransferForm] Refreshing general parameters widget...", flush=True)
        try:
            self.general_params.refresh()
            print(f"[TransferForm] General params refresh complete", flush=True)
        except Exception as e:
            print(f"[TransferForm] ERROR in general_params.refresh(): {e}", flush=True)
            import traceback
            traceback.print_exc()

        print(f"\n[TransferForm] Refreshing advanced parameters widget...", flush=True)
        try:
            self.advanced_params.refresh()
            print(f"[TransferForm] Advanced params refresh complete", flush=True)
        except Exception as e:
            print(f"[TransferForm] ERROR in advanced_params.refresh(): {e}", flush=True)
            import traceback
            traceback.print_exc()

        # THEN populate all FRESCO parameters with values
        print(f"\n[TransferForm] Populating all FRESCO parameters...", flush=True)
        try:
            for param_name, param_value in param_values.items():
                print(f"  Processing {param_name} = {param_value}...", flush=True)
                # Try to set in general params first, then advanced
                if param_name in self.general_params.parameter_widgets:
                    self.general_params.set_parameter_value(param_name, param_value)
                else:
                    self.advanced_params.set_parameter_value(param_name, param_value)
            print(f"[TransferForm] All FRESCO parameters populated", flush=True)
        except Exception as e:
            print(f"[TransferForm] ERROR populating parameters: {e}", flush=True)
            import traceback
            traceback.print_exc()

        # Populate partition information
        print(f"\n[TransferForm] Populating partition information...", flush=True)
        try:
            # Entrance channel
            if 'namep' in partition_info:
                self.proj_name.setText(partition_info['namep'])
            if 'massp' in partition_info:
                self.proj_mass.setValue(partition_info['massp'])
            if 'zp' in partition_info:
                self.proj_charge.setValue(partition_info['zp'])

            if 'namet' in partition_info:
                self.targ_name.setText(partition_info['namet'])
            if 'masst' in partition_info:
                self.targ_mass.setValue(partition_info['masst'])
            if 'zt' in partition_info:
                self.targ_charge.setValue(partition_info['zt'])
        except Exception as e:
            print(f"[TransferForm] ERROR populating partition: {e}", flush=True)
            import traceback
            traceback.print_exc()

        # Update header from first line of input file
        try:
            first_line = input_text.strip().split('\n')[0].strip()
            if first_line.startswith('!'):
                first_line = first_line[1:].strip()
            self.header.setText(first_line)
            print(f"  Set header from file = {first_line}", flush=True)
        except Exception as e:
            print(f"  Could not extract header from file: {e}", flush=True)

        # Parse and load energy array (elab/nlab)
        print(f"\n[TransferForm] Parsing energy array...", flush=True)
        try:
            self.energy_widget.parse_fresco_format(input_text)
            boundaries, intervals = self.energy_widget.get_boundaries_and_intervals()
            print(f"  Loaded {len(boundaries)} energy boundaries: {boundaries}", flush=True)
            print(f"  With {len(intervals)} intervals: {intervals}", flush=True)
        except Exception as e:
            print(f"[TransferForm] ERROR parsing energies: {e}", flush=True)
            import traceback
            traceback.print_exc()

        # Load POT information into potential manager
        print(f"\n[TransferForm] Loading POT information...", flush=True)
        self.pot_manager.load_from_input_text(input_text)

        print(f"\n[TransferForm] Update complete. Promoted parameters: {self.param_manager.get_categorization_summary()['promoted_params']}", flush=True)
        print("="*60 + "\n", flush=True)

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
        header_label.setObjectName("sectionHeader")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        preset_btn = QPushButton("Load Preset Example")
        preset_btn.setObjectName("presetButton")
        preset_btn.clicked.connect(self.load_preset)
        header_layout.addWidget(preset_btn)

        main_layout.addWidget(header_widget)

        info_label = QLabel("Configure one-nucleon or cluster transfer reactions (DWBA)")
        info_label.setObjectName("infoLabel")
        main_layout.addWidget(info_label)

        # Header field (not a FRESCO parameter)
        header_group = QGroupBox("Calculation Description")
        header_layout = QFormLayout()
        header_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        header_layout.setLabelAlignment(Qt.AlignLeft)

        self.header = QLineEdit("Deuteron + 40Ca -> proton + 41Ca (d,p) reaction")
        self.header.setAlignment(Qt.AlignLeft)
        header_layout.addRow("Header:", self.header)

        header_group.setLayout(header_layout)
        main_layout.addWidget(header_group)

        # Dynamic General FRESCO Parameters
        self.general_params = DynamicGeneralParametersWidget(parameter_manager=self.param_manager)
        main_layout.addWidget(self.general_params)

        # Energy Array Widget (for elab/nlab) - integrated into General Parameters
        self.energy_widget = EnergyArrayWidget()
        # Insert energy widget into the General Parameters group box
        self.general_params.group_box.layout().addWidget(self.energy_widget)

        # Entrance Channel (a + A)
        entrance_group = QGroupBox("Entrance Channel (a + A)")
        entrance_layout = QFormLayout()
        entrance_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        entrance_layout.setLabelAlignment(Qt.AlignLeft)

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
        exit_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        exit_layout.setLabelAlignment(Qt.AlignLeft)

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
        transfer_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        transfer_layout.setLabelAlignment(Qt.AlignLeft)

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

        # Optical Potentials Manager
        self.pot_manager = PotentialManagerWidget()
        main_layout.addWidget(self.pot_manager)

        # Advanced FRESCO Parameters (with parameter manager)
        self.advanced_params = AdvancedParametersWidget(parameter_manager=self.param_manager)
        main_layout.addWidget(self.advanced_params)

        main_layout.addStretch()

        scroll.setWidget(main_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def load_preset(self):
        """Load preset example for d(40Ca,p)41Ca stripping reaction"""
        # Use the actual example file content (single-line header as required by FRESCO)
        preset_input = """40Ca(d,p)41Ca neutron transfer reaction
NAMELIST
 &FRESCO hcm=0.1 rmatch=20
	 jtmin=0.0 jtmax=50 absend= 0.0010
	 thmin=0.00 thmax=180.00 thinc=5.00
 	 chans=1 smats=2  xstabl=1
	 elab(1:1)=15.0 nlab(1:1)=1 /

 &PARTITION namep='d' massp=2.00 zp=1
 	    namet='40Ca' masst=40.0000 zt=20 qval=0.000 nex=1  /
 &STATES jp=0.5 bandp=1 ep=0.0000 cpot=1 jt=0.0 bandt=1 et=0.0000  /
 &partition /

 &POT kp=1 ap=2.000 at=40.000 rc=1.2  /
 &POT kp=1 type=1 p1=40.00 p2=1.2 p3=0.65 p4=10.0 p5=1.2 p6=0.500  /
 &pot /
 &overlap /
 &coupling /
"""
        # Load using the same method as file loading
        self.update_from_input_file(preset_input)

        # Expand/activate the POT group box and individual POT components
        self.pot_manager.group_box.setChecked(True)
        for pot_widget in self.pot_manager.potential_widgets:
            pot_widget.group_box.setChecked(True)

        # Set transfer-specific parameters (not in FRESCO namelist)
        self.eject_name.setText("p")
        self.eject_mass.setValue(1.0078)
        self.eject_charge.setValue(1.0)
        self.resid_name.setText("41Ca")
        self.resid_mass.setValue(41.0)
        self.resid_charge.setValue(20.0)
        self.qvalue.setValue(5.08)

        self.trans_name.setText("n")
        self.trans_mass.setValue(1.0087)
        self.trans_charge.setValue(0.0)
        self.trans_l.setValue(1)
        self.trans_j.setValue(0.5)
        self.trans_nodes.setValue(0)
        self.binding_energy.setValue(2.224)

    def generate_input(self):
        """Generate FRESCO input text for transfer reaction"""
        # Get parameters from dynamic general parameters widget
        general_params = self.general_params.get_parameter_values()

        # Get energy array from energy widget
        boundaries, intervals = self.energy_widget.get_boundaries_and_intervals()
        if boundaries:
            general_params['elab'] = boundaries
            general_params['nlab'] = intervals

        # Generate &FRESCO namelist with advanced parameters
        fresco_namelist = self.advanced_params.generate_namelist_text(general_params)

        # Generate &POT namelists from potential manager
        pot_namelists = self.pot_manager.generate_pot_namelists()

        # Build complete input file (single-line header as required by FRESCO)
        input_text = f"""{self.header.text()}
NAMELIST
{fresco_namelist}

&PARTITION namep='{self.proj_name.text()}' massp={self.proj_mass.value()} zp={self.proj_charge.value()} namet='{self.targ_name.text()}' masst={self.targ_mass.value()} zt={self.targ_charge.value()} qval=0.0 /

&STATES jp=0.5 bandp=1 ep=0.0 cpot=1 jt=0.0 bandt=1 et=0.0 /

&PARTITION namep='{self.eject_name.text()}' massp={self.eject_mass.value()} zp={self.eject_charge.value()} namet='{self.resid_name.text()}' masst={self.resid_mass.value()} zt={self.resid_charge.value()} qval={self.qvalue.value()} nex=1 /

&STATES jp=0.5 bandp=2 ep=0.0 cpot=2 jt={self.trans_j.value()} bandt=2 et=0.0 /

 &partition /

{pot_namelists}

&POT kp=3 type=1 shape=0 p1=50.0 p2=1.25 p3=0.65 /

 &pot /

&OVERLAP kn1=1 ic1=1 ic2=1 kind=0 /

&OVERLAP kn1=2 ic1=1 ic2=2 kind=7 ch1=1 ch2=2 nn={self.trans_nodes.value() + 1} l={self.trans_l.value()} j={self.trans_j.value()} kbpot=3 be={self.binding_energy.value()} isc=1 ipc=1 /

 &overlap /

&COUPLING icto=2 icfrom=1 kind=7 ip1=0 ip2=0 /

 &coupling /

! Generated by FRESCO Quantum Studio (Form Builder)
! Questions or issues? Contact: jinlei@fewbody.com
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
        header_label.setObjectName("pageHeader")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Generate button
        self.generate_btn = QPushButton("Generate Input File")
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
        footer = QLabel("💡 Tip: The form is pre-loaded with p+Ni78 example. Modify parameters as needed, then click 'Generate Input File' to update the Text Editor.")
        footer.setObjectName("footerHint")
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
                              "You will be automatically switched to the 'Text Editor' tab.")

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

    def update_from_loaded_file(self, input_text: str):
        """
        Update the current form's parameter categorization when a file is loaded

        This is called when the user loads a file in the Text Editor tab,
        ensuring the Form Builder tab reflects the parameters in the loaded file.
        Also automatically detects and switches to the appropriate calculation type.

        Args:
            input_text: Content of the loaded FRESCO input file
        """
        from parameter_manager import detect_calculation_type

        # Auto-detect calculation type from input file
        calc_type = detect_calculation_type(input_text)
        print(f"[FormInputPanel] Detected calculation type: {calc_type}")

        # Map calculation type to tab index
        type_to_index = {
            "elastic": 0,
            "inelastic": 1,
            "transfer": 2,
            "default": 0  # Default to elastic
        }

        # Switch to the appropriate tab
        target_index = type_to_index.get(calc_type, 0)
        self.calc_tabs.setCurrentIndex(target_index)

        # Update the corresponding form
        if target_index == 0:  # Elastic
            self.elastic_form.update_from_input_file(input_text)
        elif target_index == 1:  # Inelastic
            self.inelastic_form.update_from_input_file(input_text)
        elif target_index == 2:  # Transfer
            self.transfer_form.update_from_input_file(input_text)

        print(f"[FormInputPanel] Switched to {calc_type} tab and updated parameters")
