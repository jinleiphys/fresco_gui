"""
Wizard Controller for FRESCO Studio

Main controller that orchestrates the wizard flow, manages state,
and coordinates between different wizard steps.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QFrame, QMessageBox
)
from PySide6.QtCore import Signal, Qt
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from wizard_navigator import WizardNavigator, StepInfo
from wizard_step_widget import WizardStepWidget, WizardStepContainer, StepData
from reaction_parser import ReactionType, ParsedReaction
from mass_database import NucleusInfo


def nucleus_to_dict(nucleus) -> dict:
    """Convert NucleusInfo or dict to a standard dict format"""
    if nucleus is None:
        return {}
    if isinstance(nucleus, dict):
        return nucleus
    if isinstance(nucleus, NucleusInfo):
        return {
            'name': nucleus.name,
            'symbol': nucleus.symbol,
            'mass_number': nucleus.mass_number,
            'atomic_number': nucleus.atomic_number,
            'mass': nucleus.mass,
        }
    # Try to access as attributes
    try:
        return {
            'name': getattr(nucleus, 'name', ''),
            'mass_number': getattr(nucleus, 'mass_number', 1),
            'atomic_number': getattr(nucleus, 'atomic_number', 0),
            'mass': getattr(nucleus, 'mass', 1.0),
        }
    except:
        return {}


@dataclass
class WizardState:
    """Complete state of the wizard"""
    reaction_type: ReactionType = ReactionType.ELASTIC
    reaction_data: Optional[ParsedReaction] = None
    step_data: Dict[str, StepData] = field(default_factory=dict)
    energy_mev: float = 100.0
    current_step: int = 0


class ReactionTypeSelector(QWidget):
    """Widget for selecting reaction type at the start of wizard"""

    type_changed = Signal(str)  # Emitted with reaction type string

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        label = QLabel("Reaction Type:")
        label.setStyleSheet("font-weight: 500; color: #374151;")
        layout.addWidget(label)

        self.combo = QComboBox()
        self.combo.addItem("Elastic Scattering", "elastic")
        self.combo.addItem("Inelastic Scattering", "inelastic")
        self.combo.addItem("Transfer Reaction", "transfer")
        self.combo.setMinimumWidth(200)
        self.combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #2563eb;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
        """)
        self.combo.currentIndexChanged.connect(self._on_type_changed)
        layout.addWidget(self.combo)

        layout.addStretch()

    def _on_type_changed(self, index: int):
        type_str = self.combo.currentData()
        self.type_changed.emit(type_str)

    def get_reaction_type(self) -> str:
        return self.combo.currentData()

    def set_reaction_type(self, type_str: str):
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == type_str:
                self.combo.setCurrentIndex(i)
                break


class WizardController(QWidget):
    """
    Main wizard controller that manages the complete wizard flow.

    Responsibilities:
    - Create and manage wizard steps based on reaction type
    - Handle navigation between steps
    - Collect and validate data from all steps
    - Generate FRESCO input from wizard data
    """

    # Signals
    input_generated = Signal(str)  # Emitted with generated FRESCO input

    def __init__(self):
        super().__init__()
        self.state = WizardState()
        self.step_widgets: List[WizardStepWidget] = []

        self._init_ui()
        self._setup_elastic_steps()  # Default to elastic

    def _init_ui(self):
        """Initialize the controller UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navigator (contains progress indicator and step content)
        self.navigator = WizardNavigator()
        self.navigator.generate_requested.connect(self._on_generate)
        self.navigator.step_changed.connect(self._on_step_changed)
        self.navigator.reset_requested.connect(self._on_reset)
        main_layout.addWidget(self.navigator, 1)

        # Type selector (hidden - type is auto-detected from equation)
        self.type_selector = ReactionTypeSelector()
        self.type_selector.type_changed.connect(self._on_reaction_type_changed)
        self.type_selector.hide()

    def _on_reaction_type_changed(self, type_str: str):
        """Handle reaction type change"""
        type_map = {
            "elastic": ReactionType.ELASTIC,
            "inelastic": ReactionType.INELASTIC,
            "transfer": ReactionType.TRANSFER,
        }
        self.state.reaction_type = type_map.get(type_str, ReactionType.ELASTIC)

        # Rebuild steps for new reaction type
        self._clear_steps()

        if self.state.reaction_type == ReactionType.ELASTIC:
            self._setup_elastic_steps()
        elif self.state.reaction_type == ReactionType.INELASTIC:
            self._setup_inelastic_steps()
        elif self.state.reaction_type == ReactionType.TRANSFER:
            self._setup_transfer_steps()

        # Reset to first step
        self.navigator.go_to_step(0)

    def _clear_steps(self):
        """Clear all existing steps"""
        # Remove widgets from navigator
        while self.navigator.content_stack.count() > 0:
            widget = self.navigator.content_stack.widget(0)
            self.navigator.content_stack.removeWidget(widget)
            widget.deleteLater()

        self.step_widgets = []

    def _setup_elastic_steps(self):
        """Setup steps for elastic scattering"""
        from wizard_steps.reaction_input_step import ReactionInputStep
        from wizard_steps.particle_config_step import ParticleConfigStep
        from wizard_steps.potential_setup_step import PotentialSetupStep
        from wizard_steps.review_step import ReviewStep

        steps = [
            StepInfo("reaction", "Reaction Input", "Reaction", is_enabled=True),
            StepInfo("particles", "Particle Configuration", "Particles", is_enabled=True),
            StepInfo("potentials", "Optical Potentials", "Potentials", is_enabled=True),
            StepInfo("review", "Review & Generate", "Review", is_enabled=True),
        ]

        self.navigator.set_steps(steps)

        # Create step widgets
        step1 = ReactionInputStep()
        step1.reaction_parsed.connect(self._on_reaction_parsed)
        step1.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step1)

        step2 = ParticleConfigStep()
        step2.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step2)

        step3 = PotentialSetupStep()
        step3.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step3)

        step4 = ReviewStep()
        step4.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step4)

        # Add to navigator with containers
        for step in self.step_widgets:
            container = WizardStepContainer(step)
            self.navigator.add_step_widget(container)

    def _setup_inelastic_steps(self):
        """Setup steps for inelastic scattering"""
        from wizard_steps.reaction_input_step import ReactionInputStep
        from wizard_steps.particle_config_step import ParticleConfigStep
        from wizard_steps.states_step import StatesStep
        from wizard_steps.coupling_step import CouplingStep
        from wizard_steps.potential_setup_step import PotentialSetupStep
        from wizard_steps.review_step import ReviewStep

        steps = [
            StepInfo("reaction", "Reaction Input", "Reaction", is_enabled=True),
            StepInfo("particles", "Particle Configuration", "Particles", is_enabled=True),
            StepInfo("states", "States Definition", "States", is_enabled=True),
            StepInfo("coupling", "State Couplings", "Coupling", is_enabled=True),
            StepInfo("potentials", "Optical Potentials", "Potentials", is_enabled=True),
            StepInfo("review", "Review & Generate", "Review", is_enabled=True),
        ]

        self.navigator.set_steps(steps)

        # Create step widgets
        step1 = ReactionInputStep()
        step1.reaction_parsed.connect(self._on_reaction_parsed)
        step1.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step1)

        step2 = ParticleConfigStep()
        step2.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step2)

        step3 = StatesStep()
        step3.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step3)

        step4 = CouplingStep()
        step4.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step4)

        step5 = PotentialSetupStep()
        step5.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step5)

        step6 = ReviewStep()
        step6.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step6)

        for step in self.step_widgets:
            container = WizardStepContainer(step)
            self.navigator.add_step_widget(container)

    def _setup_transfer_steps(self):
        """Setup steps for transfer reaction"""
        from wizard_steps.reaction_input_step import ReactionInputStep
        from wizard_steps.particle_config_step import ParticleConfigStep
        from wizard_steps.exit_channel_step import ExitChannelStep
        from wizard_steps.transferred_particle_step import TransferredParticleStep
        from wizard_steps.overlap_step import OverlapStep
        from wizard_steps.potential_setup_step import PotentialSetupStep
        from wizard_steps.review_step import ReviewStep

        steps = [
            StepInfo("reaction", "Reaction Input", "Reaction", is_enabled=True),
            StepInfo("entrance", "Entrance Channel", "Entrance", is_enabled=True),
            StepInfo("exit", "Exit Channel", "Exit", is_enabled=True),
            StepInfo("transferred", "Transferred Particle", "Transfer", is_enabled=True),
            StepInfo("overlap", "Overlap Functions", "Overlap", is_enabled=True),
            StepInfo("potentials", "Optical Potentials", "Potentials", is_enabled=True),
            StepInfo("review", "Review & Generate", "Review", is_enabled=True),
        ]

        self.navigator.set_steps(steps)

        # Create step widgets
        step1 = ReactionInputStep()
        step1.reaction_parsed.connect(self._on_reaction_parsed)
        step1.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step1)

        step2 = ParticleConfigStep()
        step2.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step2)

        step3 = ExitChannelStep()
        step3.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step3)

        step4 = TransferredParticleStep()
        step4.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step4)

        step5 = OverlapStep()
        step5.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step5)

        step6 = PotentialSetupStep()
        step6.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step6)

        step7 = ReviewStep()
        step7.data_changed.connect(self._on_step_data_changed)
        self.step_widgets.append(step7)

        for step in self.step_widgets:
            container = WizardStepContainer(step)
            self.navigator.add_step_widget(container)

    def _on_step_data_changed(self):
        """Handle step data change"""
        # Update step completion status
        for i, step in enumerate(self.step_widgets):
            is_complete = step.is_complete()
            self.navigator.set_step_complete(i, is_complete)

    def _on_reaction_parsed(self, parsed_reaction: ParsedReaction):
        """Handle reaction parsed from first step"""
        old_reaction_type = self.state.reaction_type
        self.state.reaction_data = parsed_reaction
        self.state.reaction_type = parsed_reaction.reaction_type

        # If reaction type changed, rebuild the wizard steps
        if self.state.reaction_type != old_reaction_type:
            self._rebuild_steps_for_reaction_type(parsed_reaction)
        else:
            # Update subsequent steps with reaction info
            for step in self.step_widgets[1:]:
                if hasattr(step, 'set_reaction'):
                    step.set_reaction(parsed_reaction)

    def _rebuild_steps_for_reaction_type(self, parsed_reaction: ParsedReaction):
        """Rebuild wizard steps when reaction type changes"""
        # Save the reaction input step data (first step)
        first_step_data = None
        if self.step_widgets:
            first_step_data = self.step_widgets[0].get_data()

        # Clear existing steps
        self._clear_steps()

        # Setup new steps based on reaction type
        if self.state.reaction_type == ReactionType.ELASTIC:
            self._setup_elastic_steps()
        elif self.state.reaction_type == ReactionType.INELASTIC:
            self._setup_inelastic_steps()
        elif self.state.reaction_type == ReactionType.TRANSFER:
            self._setup_transfer_steps()

        # Restore the first step data and propagate reaction to subsequent steps
        if first_step_data and self.step_widgets:
            self.step_widgets[0].set_data(first_step_data.values)
            # Update reaction data in subsequent steps
            for step in self.step_widgets[1:]:
                if hasattr(step, 'set_reaction'):
                    step.set_reaction(parsed_reaction)

        # Stay on first step
        self.navigator.go_to_step(0)

    def _on_step_changed(self, index: int):
        """Handle step change"""
        self.state.current_step = index

        # Collect data from all previous steps and pass to review step
        if index == len(self.step_widgets) - 1:  # Review step
            all_data = self._collect_all_step_data()
            review_step = self.step_widgets[-1]
            if hasattr(review_step, 'set_wizard_data'):
                review_step.set_wizard_data(all_data)

        # Notify the step it's being entered
        if 0 <= index < len(self.step_widgets):
            self.step_widgets[index].on_entering_step()

    def _collect_all_step_data(self) -> dict:
        """Collect data from all wizard steps"""
        all_data = {}

        step_keys = ['reaction_input', 'particle_config', 'states', 'coupling',
                     'exit_channel', 'transferred_particle', 'overlap', 'potential_setup']

        for i, step in enumerate(self.step_widgets[:-1]):  # Exclude review step
            step_data = step.get_data()
            # Use step_id if available, otherwise use index
            key = step.step_id if hasattr(step, 'step_id') else f'step_{i}'
            all_data[key] = step_data.values

        return all_data

    def _on_generate(self):
        """Handle generate button click"""
        try:
            input_text = self.generate_fresco_input()
            self.input_generated.emit(input_text)

            QMessageBox.information(
                self,
                "Input Generated",
                "FRESCO input file has been generated successfully!\n\n"
                "You can view it in the Text Editor tab."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Generation Error",
                f"Failed to generate FRESCO input:\n\n{str(e)}"
            )

    def _on_reset(self):
        """Handle reset button click - reset wizard to initial state"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Reset Wizard",
            "Are you sure you want to reset the wizard?\n\n"
            "All entered data will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._reset_wizard()

    def _reset_wizard(self):
        """Reset the wizard to initial state"""
        # Reset state
        self.state = WizardState()

        # Reset all step widgets
        for step in self.step_widgets:
            if hasattr(step, 'reset'):
                step.reset()
            elif hasattr(step, 'set_data'):
                step.set_data({})  # Clear data

        # Reset navigator
        self.navigator.reset_wizard()

        # Notify first step it's being entered
        if self.step_widgets:
            self.step_widgets[0].on_entering_step()

    def generate_fresco_input(self) -> str:
        """
        Generate FRESCO input text from wizard state.

        Returns:
            Complete FRESCO input file content
        """
        # Collect data from all steps
        all_data = {}
        for step in self.step_widgets:
            step_data = step.get_data()
            all_data.update(step_data.values)

        # Build input based on reaction type
        if self.state.reaction_type == ReactionType.ELASTIC:
            return self._generate_elastic_input(all_data)
        elif self.state.reaction_type == ReactionType.INELASTIC:
            return self._generate_inelastic_input(all_data)
        elif self.state.reaction_type == ReactionType.TRANSFER:
            return self._generate_transfer_input(all_data)
        else:
            return "! Unknown reaction type\n"

    def _generate_elastic_input(self, data: Dict[str, Any]) -> str:
        """Generate elastic scattering input"""
        # Extract values with defaults - convert NucleusInfo to dict
        proj = nucleus_to_dict(data.get('projectile', {}))
        targ = nucleus_to_dict(data.get('target', {}))
        energy = data.get('energy', 100.0)
        params = data.get('fresco_params', {})
        pots = data.get('potentials', [])

        # Build header
        proj_name = proj.get('name', 'p')
        targ_name = targ.get('name', '12C')
        header = f"{proj_name}+{targ_name} @ {energy} MeV; Elastic"

        # Build FRESCO namelist
        fresco_params = {
            'hcm': params.get('hcm', 0.1) if isinstance(params, dict) else 0.1,
            'rmatch': params.get('rmatch', 60.0) if isinstance(params, dict) else 60.0,
            'jtmax': params.get('jtmax', 50.0) if isinstance(params, dict) else 50.0,
            'absend': params.get('absend', 0.001) if isinstance(params, dict) else 0.001,
            'thmin': params.get('thmin', 0.0) if isinstance(params, dict) else 0.0,
            'thmax': params.get('thmax', 180.0) if isinstance(params, dict) else 180.0,
            'thinc': params.get('thinc', 1.0) if isinstance(params, dict) else 1.0,
            'iter': params.get('iter', 1) if isinstance(params, dict) else 1,
            'chans': params.get('chans', 1) if isinstance(params, dict) else 1,
            'smats': params.get('smats', 2) if isinstance(params, dict) else 2,
            'xstabl': params.get('xstabl', 1) if isinstance(params, dict) else 1,
        }

        fresco_line = " &FRESCO\n"
        for key, val in fresco_params.items():
            fresco_line += f"     {key}={val}"
        fresco_line += f"\n      elab={energy:.3f} /\n"

        # Build PARTITION
        proj_mass = proj.get('mass', 1.0)
        proj_z = proj.get('atomic_number', 1)
        targ_mass = targ.get('mass', 12.0)
        targ_z = targ.get('atomic_number', 6)
        proj_spin = proj.get('spin', 0.5)
        targ_spin = targ.get('spin', 0.0)

        partition = f" &PARTITION namep='{proj_name}' massp={proj_mass} zp={proj_z} "
        partition += f"namet='{targ_name}' masst={targ_mass} zt={targ_z} qval=0.0 nex=1 /\n"

        # Build STATES
        states = f" &STATES jp={proj_spin} bandp=1 ep=0.0 cpot=1 "
        states += f"jt={targ_spin} bandt=1 et=0.0 /\n"

        # Build POT namelists
        pot_text = self._generate_pot_namelists(pots, proj, targ)

        # Assemble
        input_text = f"""{header}
NAMELIST
{fresco_line}
{partition}{states} &partition /

{pot_text} &pot /
 &overlap /
 &coupling /

! Generated by FRESCO Studio (Wizard)
! Questions or issues? Contact: jinl@tongji.edu.cn
"""
        return input_text

    def _generate_inelastic_input(self, data: Dict[str, Any]) -> str:
        """Generate inelastic scattering input"""
        # Similar to elastic but with states and coupling
        # Simplified implementation for now
        return self._generate_elastic_input(data)  # TODO: Implement properly

    def _generate_transfer_input(self, data: Dict[str, Any]) -> str:
        """Generate transfer reaction input"""
        # Extract values - convert NucleusInfo to dict
        proj = nucleus_to_dict(data.get('projectile', {}))
        targ = nucleus_to_dict(data.get('target', {}))
        eject = nucleus_to_dict(data.get('ejectile', {}))
        resid = nucleus_to_dict(data.get('residual', {}))
        energy = data.get('energy', 100.0)
        params = data.get('fresco_params', {})
        pots = data.get('potentials', [])
        qval = data.get('q_value', 0.0) or 0.0

        # Get particle properties
        proj_name = proj.get('name', 'd')
        proj_mass = proj.get('mass', 2.0)
        proj_z = proj.get('atomic_number', 1)
        proj_a = proj.get('mass_number', 2)
        proj_spin = proj.get('spin', 1.0)

        targ_name = targ.get('name', '12C')
        targ_mass = targ.get('mass', 12.0)
        targ_z = targ.get('atomic_number', 6)
        targ_a = targ.get('mass_number', 12)
        targ_spin = targ.get('spin', 0.0)

        eject_name = eject.get('name', 'p')
        eject_mass = eject.get('mass', 1.0)
        eject_z = eject.get('atomic_number', 1)
        eject_a = eject.get('mass_number', 1)
        eject_spin = eject.get('spin', 0.5)

        resid_name = resid.get('name', '13C')
        resid_mass = resid.get('mass', 13.0)
        resid_z = resid.get('atomic_number', 6)
        resid_a = resid.get('mass_number', 13)
        resid_spin = resid.get('spin', 0.5)
        resid_parity = resid.get('parity', 1)  # 1 for +, -1 for -

        # Build header
        header = f"{targ_name}({proj_name},{eject_name}){resid_name} @ {energy} MeV"

        # Build FRESCO namelist
        fresco_params = {
            'hcm': 0.03,
            'rmatch': 40.0,
            'jtmax': 120.0,
            'absend': -1.0,
            'thmin': 0.0,
            'thmax': 60.0,
            'thinc': 0.5,
            'iter': 1,
            'nnu': 36,
            'rintp': 0.20,
            'hnl': 0.1,
            'rnl': 10.0,
            'chans': 1,
            'xstabl': 1,
        }

        fresco_line = " &FRESCO "
        param_strs = [f"{k}={v}" for k, v in fresco_params.items()]
        fresco_line += " ".join(param_strs[:6]) + "\n\t " + " ".join(param_strs[6:])
        fresco_line += f"\n\t elab={energy:.1f}  /\n"

        # Build PARTITIONs
        partition1 = f" &PARTITION namep='{proj_name}' massp={proj_mass:.1f} zp={proj_z} "
        partition1 += f"namet='{targ_name}' masst={targ_mass:.1f} zt={targ_z} nex=1  /\n"
        states1 = f" &STATES jp={proj_spin} bandp=1 ep=0.0 cpot=1 jt={targ_spin} bandt=1 et=0.0  /\n"

        partition2 = f"\n &PARTITION namep='{eject_name}' massp={eject_mass:.1f} zp={eject_z} "
        partition2 += f"namet='{resid_name}' masst={resid_mass:.1f} zt={resid_z} qval={qval:.4f} nex=1  /\n"
        # Use residual parity for bandt: positive=1, negative=-1
        resid_bandt = 1 if resid_parity > 0 else -1
        states2 = f" &STATES jp={eject_spin} bandp=1 ep=0.0 cpot=2 jt={resid_spin} bandt={resid_bandt} et=0.0  /\n"

        # Build POT namelists for all 5 sets
        pot_lines = []

        # kp=1: Entrance channel
        pot_lines.append(f" &POT kp=1 ap={proj_a:.3f} at={targ_a:.3f} rc=1.3  /")
        pot_lines.append(f" &POT kp=1 type=1 p1=37.2 p2=1.2 p3=0.6  p4=21.6 p5=1.2 p6=0.69  /")

        # kp=2: Exit channel
        pot_lines.append(f"\n &POT kp=2 ap={eject_a:.3f} at={resid_a:.3f} rc=1.3  /")
        pot_lines.append(f" &POT kp=2 type=1 p1=37.2 p2=1.2 p3=0.6  p4=21.6 p5=1.2 p6=0.69  /")

        # kp=3: Projectile binding (transferred particle in projectile)
        pot_lines.append(f"\n &POT kp=3 at={proj_a} rc=1.2  /")
        pot_lines.append(f" &POT kp=3 type=1 p1=50.00 p2=1.2 p3=0.65   /")
        pot_lines.append(f" &POT kp=3 type=3 p1=6.00  p2=1.2 p3=0.65   /")

        # kp=4: Residual binding (transferred particle in residual)
        pot_lines.append(f"\n &POT kp=4 at={resid_a} rc=1.2  /")
        pot_lines.append(f" &POT kp=4 type=1 p1=50.00 p2=1.2 p3=0.65   /")
        pot_lines.append(f" &POT kp=4 type=3 p1=6.00  p2=1.2 p3=0.65   /")

        # kp=5: Remnant potential (core-core)
        pot_lines.append(f"\n &POT kp=5 ap={proj_a:.3f} at={targ_a:.3f} rc=1.3  /")
        pot_lines.append(f" &POT kp=5 type=1 p1=37.2 p2=1.2 p3=0.6  p4=21.6 p5=1.2 p6=0.69  /")

        pot_text = "\n".join(pot_lines)

        # Build OVERLAP section
        # Determine transferred particle (difference between proj and eject)
        transferred_a = abs(proj_a - eject_a)
        transferred_z = abs(proj_z - eject_z)

        # Overlap 1: projectile -> core + transferred (e.g., d -> p + n)
        # Overlap 2: residual -> target + transferred (e.g., 13C -> 12C + n)
        overlap_lines = []

        # Get binding energies from wizard overlap step data
        proj_overlap_data = data.get('projectile_overlap', {})
        targ_overlap_data = data.get('target_overlap', {})

        be_proj = proj_overlap_data.get('binding_energy', 2.225) if isinstance(proj_overlap_data, dict) else 2.225
        be_resid = targ_overlap_data.get('binding_energy', 4.946) if isinstance(targ_overlap_data, dict) else 4.946

        # Get quantum numbers from transferred particle step or use defaults
        transferred_data = data.get('transferred_particle', {})

        # For projectile overlap (light ion like deuteron)
        # Deuteron: 1s state (nn=1, l=0, j=0.5 for the neutron)
        # Note: nn = number of nodes + 1 (FRESCO convention), so 1s = nn=1
        proj_n = transferred_data.get('n_proj', 1) if isinstance(transferred_data, dict) else 1
        proj_l = transferred_data.get('l_proj', 0) if isinstance(transferred_data, dict) else 0
        proj_j = transferred_data.get('j_proj', 0.5) if isinstance(transferred_data, dict) else 0.5

        # For residual overlap (heavy nucleus)
        # Determine l based on shell model: p-shell (l=1) for A=5-16, sd-shell for A=17-40
        # nn = 1 for lowest state in that shell (no radial nodes within the shell)
        resid_n = transferred_data.get('n_resid', 1) if isinstance(transferred_data, dict) else 1
        # Default l based on residual mass number
        default_l = 0
        if 5 <= resid_a <= 16:
            default_l = 1  # p-shell
        elif 17 <= resid_a <= 40:
            default_l = 2  # d-shell (sd-shell)
        resid_l = transferred_data.get('l_resid', default_l) if isinstance(transferred_data, dict) else default_l
        # For j, use the residual nucleus spin (which equals the transferred particle j for 0+ target)
        # For 12C(0+) + n -> 13C(1/2-), j = 1/2 (p1/2 state)
        # Default to residual spin if available, otherwise l - 0.5 for p-shell (gives 1/2-)
        default_j = resid_spin if resid_spin > 0 else (abs(resid_l - 0.5) if resid_l > 0 else 0.5)
        resid_j = transferred_data.get('j_resid', default_j) if isinstance(transferred_data, dict) else default_j

        overlap_lines.append(f" &Overlap kn1=1 ic1=1 ic2=2 in=1 kind=0 nn={proj_n} l={proj_l} sn=0.5 j={proj_j} kbpot=3 be={be_proj:.3f} isc=1 ipc=0 /")
        overlap_lines.append(f" &Overlap kn1=2 ic1=2 ic2=1 in=2 kind=0 nn={resid_n} l={resid_l} sn=0.5 j={resid_j} kbpot=4 be={be_resid:.3f} isc=1 ipc=0 /")

        overlap_text = "\n".join(overlap_lines)

        # Build COUPLING section
        coupling_lines = []
        coupling_lines.append(f" &Coupling icto=-2 icfrom=1 kind=7 ip1=0 ip2=-1 ip3=5 /")
        coupling_lines.append(f" &CFP in=1 ib=1 ia=1 kn=1 a=1.00  /")
        coupling_lines.append(f" &CFP in=2 ib=1 ia=1 kn=2 a=1.00  /")
        coupling_lines.append(f" &CFP /")

        coupling_text = "\n".join(coupling_lines)

        # Assemble
        input_text = f"""{header}
NAMELIST
{fresco_line}
{partition1}{states1}
{partition2}{states2} &partition /

{pot_text}
 &pot /

{overlap_text}
 &overlap /

{coupling_text}
 &coupling /

! Generated by FRESCO Studio (Wizard)
! Questions or issues? Contact: jinl@tongji.edu.cn
"""
        return input_text

    def _generate_pot_namelists(self, pots: List[Dict], proj: Dict, targ: Dict) -> str:
        """Generate POT namelists from potential data"""
        if not pots:
            # Default potentials
            at = targ.get('mass', 12.0)
            ap = proj.get('mass', 1.0)
            return f"""&POT kp=1 type=0 at={at} ap={ap} rc=1.2 /
&POT kp=1 type=1 p1=50.0 p2=1.2 p3=0.65 p4=10.0 p5=1.2 p6=0.5 /
"""

        lines = []
        for pot in pots:
            kp = pot.get('kp', 1)
            pot_type = pot.get('type', 0)

            if pot_type == 0:  # Coulomb
                # Coulomb uses rc parameter, and needs ap/at from masses
                rc = pot.get('rc', 1.25)
                at = targ.get('mass_number', targ.get('mass', 12))
                ap = proj.get('mass_number', proj.get('mass', 1))
                lines.append(f"&POT kp={kp} type=0 at={at} ap={ap} rc={rc} /")
            elif pot_type == 1:  # Volume Woods-Saxon
                # Map named parameters to p1-p6
                V = pot.get('V', 50.0)
                r0 = pot.get('r0', 1.17)
                a = pot.get('a', 0.75)
                W = pot.get('W', 10.0)
                rW = pot.get('rW', 1.32)
                aW = pot.get('aW', 0.52)
                lines.append(f"&POT kp={kp} type=1 p1={V} p2={r0} p3={a} p4={W} p5={rW} p6={aW} /")
            elif pot_type == 2:  # Surface Woods-Saxon
                Vd = pot.get('Vd', 0.0)
                r0d = pot.get('r0d', 1.32)
                ad = pot.get('ad', 0.52)
                Wd = pot.get('Wd', 10.0)
                rWd = pot.get('rWd', 1.32)
                aWd = pot.get('aWd', 0.52)
                lines.append(f"&POT kp={kp} type=2 p1={Vd} p2={r0d} p3={ad} p4={Wd} p5={rWd} p6={aWd} /")
            elif pot_type == 3:  # Spin-orbit
                Vso = pot.get('Vso', 6.0)
                rso = pot.get('rso', 1.01)
                aso = pot.get('aso', 0.75)
                lines.append(f"&POT kp={kp} type=3 p1={Vso} p2={rso} p3={aso} /")

        return '\n'.join(lines) + '\n'

    def set_reaction_from_equation(self, equation: str):
        """
        Set up the wizard from a reaction equation.

        Args:
            equation: Reaction equation string (e.g., "n14(f17,ne18)c13")
        """
        from reaction_parser import parse_reaction

        result = parse_reaction(equation)

        if result.parse_success:
            self.state.reaction_data = result

            # Set reaction type selector
            type_map = {
                ReactionType.ELASTIC: "elastic",
                ReactionType.INELASTIC: "inelastic",
                ReactionType.TRANSFER: "transfer",
            }
            self.type_selector.set_reaction_type(type_map.get(result.reaction_type, "elastic"))

            # Populate first step with parsed data
            if self.step_widgets:
                self.step_widgets[0].set_data({
                    'equation': equation,
                    'reaction': result
                })
