"""
Overlap Step for FRESCO Studio Wizard

Step for transfer reactions: Define overlap functions.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QFrame, QGridLayout,
    QGroupBox, QPushButton, QCheckBox
)
from PySide6.QtCore import Signal, Qt

from wizard_step_widget import WizardStepWidget, ValidationMessage
from reaction_parser import ParsedReaction, ReactionType


class OverlapConfigWidget(QWidget):
    """Widget for configuring a single overlap function"""

    data_changed = Signal()

    def __init__(self, title: str):
        super().__init__()
        self._init_ui(title)

    def _init_ui(self, title: str):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-weight: 600;
            font-size: 13px;
            color: #374151;
        """)
        layout.addWidget(title_label)

        # Parameters grid
        grid = QGridLayout()
        grid.setSpacing(8)

        # Binding energy
        grid.addWidget(QLabel("Binding Energy:"), 0, 0)
        self.binding_energy = QDoubleSpinBox()
        self.binding_energy.setRange(0.0, 100.0)
        self.binding_energy.setDecimals(3)
        self.binding_energy.setSuffix(" MeV")
        self.binding_energy.setSingleStep(0.1)
        self.binding_energy.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.binding_energy, 0, 1)

        # Potential radius
        grid.addWidget(QLabel("Radius (r₀):"), 1, 0)
        self.radius = QDoubleSpinBox()
        self.radius.setRange(0.5, 3.0)
        self.radius.setDecimals(2)
        self.radius.setSuffix(" fm")
        self.radius.setValue(1.25)
        self.radius.setSingleStep(0.05)
        self.radius.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.radius, 1, 1)

        # Diffuseness
        grid.addWidget(QLabel("Diffuseness (a):"), 2, 0)
        self.diffuseness = QDoubleSpinBox()
        self.diffuseness.setRange(0.1, 2.0)
        self.diffuseness.setDecimals(2)
        self.diffuseness.setSuffix(" fm")
        self.diffuseness.setValue(0.65)
        self.diffuseness.setSingleStep(0.05)
        self.diffuseness.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.diffuseness, 2, 1)

        # Spin-orbit (rc)
        grid.addWidget(QLabel("Coulomb radius:"), 3, 0)
        self.rc = QDoubleSpinBox()
        self.rc.setRange(0.5, 3.0)
        self.rc.setDecimals(2)
        self.rc.setSuffix(" fm")
        self.rc.setValue(1.25)
        self.rc.setSingleStep(0.05)
        self.rc.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.rc, 3, 1)

        layout.addLayout(grid)

        self.setStyleSheet("""
            QDoubleSpinBox {
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                min-width: 100px;
            }
        """)

    def get_data(self) -> dict:
        """Get overlap configuration data"""
        return {
            'binding_energy': self.binding_energy.value(),
            'radius': self.radius.value(),
            'diffuseness': self.diffuseness.value(),
            'rc': self.rc.value(),
        }

    def set_data(self, data: dict):
        """Set overlap configuration"""
        if 'binding_energy' in data:
            self.binding_energy.setValue(data['binding_energy'])
        if 'radius' in data:
            self.radius.setValue(data['radius'])
        if 'diffuseness' in data:
            self.diffuseness.setValue(data['diffuseness'])
        if 'rc' in data:
            self.rc.setValue(data['rc'])


class OverlapStep(WizardStepWidget):
    """
    Transfer Reaction Step: Overlap Functions.

    Configure the overlap functions for transfer reactions:
    - Projectile overlap: <a | b + x>
    - Target overlap: <A | B + x> or <B | A + x>
    """

    def __init__(self):
        super().__init__(
            step_id="overlap",
            title="Overlap Functions (Transfer)",
            description="Configure the overlap functions that describe how the transferred "
                        "particle is bound in the projectile and target/residual systems."
        )
        self.parsed_reaction: ParsedReaction = None

    def init_step_ui(self):
        """Initialize the step UI"""
        # Projectile overlap
        proj_group = self.create_group_box("Projectile Overlap ⟨a | b + x⟩")
        proj_layout = QVBoxLayout(proj_group)

        self.proj_info = QLabel("Projectile → Ejectile + x")
        self.proj_info.setStyleSheet("""
            color: #2563eb;
            font-weight: 500;
            padding: 8px;
            background-color: #eff6ff;
            border-radius: 4px;
        """)
        proj_layout.addWidget(self.proj_info)

        self.proj_overlap = OverlapConfigWidget("Binding Configuration")
        self.proj_overlap.data_changed.connect(self.emit_data_changed)
        proj_layout.addWidget(self.proj_overlap)

        self.content_layout.addWidget(proj_group)

        # Target overlap
        target_group = self.create_group_box("Target Overlap ⟨B | A + x⟩")
        target_layout = QVBoxLayout(target_group)

        self.target_info = QLabel("Residual → Target + x")
        self.target_info.setStyleSheet("""
            color: #059669;
            font-weight: 500;
            padding: 8px;
            background-color: #d1fae5;
            border-radius: 4px;
        """)
        target_layout.addWidget(self.target_info)

        self.target_overlap = OverlapConfigWidget("Binding Configuration")
        self.target_overlap.data_changed.connect(self.emit_data_changed)
        target_layout.addWidget(self.target_overlap)

        self.content_layout.addWidget(target_group)

        # Spectroscopic factor
        spec_group = self.create_group_box("Spectroscopic Factors")
        spec_layout = QGridLayout(spec_group)
        spec_layout.setSpacing(12)

        spec_layout.addWidget(QLabel("Projectile S_a:"), 0, 0)
        self.spec_proj = QDoubleSpinBox()
        self.spec_proj.setRange(0.0, 10.0)
        self.spec_proj.setDecimals(3)
        self.spec_proj.setValue(1.0)
        self.spec_proj.valueChanged.connect(self.emit_data_changed)
        spec_layout.addWidget(self.spec_proj, 0, 1)

        spec_layout.addWidget(QLabel("Target S_A:"), 1, 0)
        self.spec_target = QDoubleSpinBox()
        self.spec_target.setRange(0.0, 10.0)
        self.spec_target.setDecimals(3)
        self.spec_target.setValue(1.0)
        self.spec_target.valueChanged.connect(self.emit_data_changed)
        spec_layout.addWidget(self.spec_target, 1, 1)

        self.content_layout.addWidget(spec_group)

        # Preset binding energies
        presets_group = self.create_group_box("Common Binding Energies")
        presets_layout = QHBoxLayout(presets_group)

        presets = [
            ("Deuteron (d)", 2.225, "proj"),
            ("Neutron in ¹²C", 18.72, "target"),
            ("Proton in ⁴⁰Ca", 8.33, "target"),
        ]

        for name, be, which in presets:
            btn = QPushButton(f"{name}: {be} MeV")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f3f4f6;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #e5e7eb;
                }
            """)
            btn.clicked.connect(
                lambda _, be=be, w=which: self._apply_binding(be, w)
            )
            presets_layout.addWidget(btn)

        presets_layout.addStretch()
        self.content_layout.addWidget(presets_group)

        # Physics notes
        notes_group = self.create_group_box("Physics Notes")
        notes_layout = QVBoxLayout(notes_group)

        notes = QLabel(
            "<b>Overlap function:</b> The wave function of the transferred particle "
            "relative to the core nucleus.<br><br>"
            "<b>Binding energy:</b> Energy required to separate the transferred particle "
            "from the core. For (d,p): deuteron binding = 2.225 MeV.<br><br>"
            "<b>Woods-Saxon potential:</b> The bound state is calculated in a "
            "Woods-Saxon potential with given radius and diffuseness.<br><br>"
            "<b>Spectroscopic factor:</b> Probability of finding the single-particle "
            "configuration in the actual nuclear wave function."
        )
        notes.setWordWrap(True)
        notes.setStyleSheet("""
            color: #4b5563;
            font-size: 12px;
            padding: 8px;
            background-color: #f9fafb;
            border-radius: 4px;
        """)
        notes_layout.addWidget(notes)

        self.content_layout.addWidget(notes_group)
        self.content_layout.addStretch()

    def _apply_binding(self, be: float, which: str):
        """Apply a preset binding energy"""
        if which == "proj":
            self.proj_overlap.binding_energy.setValue(be)
        else:
            self.target_overlap.binding_energy.setValue(be)
        self.emit_data_changed()

    def set_reaction(self, reaction: ParsedReaction):
        """Update from parsed reaction"""
        self.parsed_reaction = reaction

        if reaction.reaction_type != ReactionType.TRANSFER:
            return

        # Update info labels
        if reaction.projectile and reaction.ejectile:
            self.proj_info.setText(
                f"{reaction.projectile.name} → {reaction.ejectile.name} + x"
            )

        if reaction.target and reaction.residual:
            self.target_info.setText(
                f"{reaction.residual.name} = {reaction.target.name} + x"
            )

        # Set projectile binding energy based on projectile type
        if reaction.projectile:
            proj_symbol = reaction.projectile.symbol.lower()
            proj_a = reaction.projectile.mass_number
            proj_name = reaction.projectile.name.lower() if reaction.projectile.name else ''

            # Common binding energies for light projectiles
            # Key by (symbol, mass_number) or by common name
            binding_energies_by_key = {
                ('h', 2): 2.225,   # Deuteron (n-p)
                ('h', 3): 8.482,   # Triton (n-d or p-2n)
                ('he', 3): 7.718,  # 3He (p-d)
                ('he', 4): 28.296, # Alpha (total binding)
            }
            binding_energies_by_name = {
                'd': 2.225,
                'deuteron': 2.225,
                '2h': 2.225,
                't': 8.482,
                'triton': 8.482,
                '3h': 8.482,
                '3he': 7.718,
                'alpha': 28.296,
                '4he': 28.296,
            }

            # Try lookup by (symbol, mass_number) first
            be_proj = binding_energies_by_key.get((proj_symbol, proj_a), 0.0)
            # If not found, try by name
            if be_proj == 0.0:
                be_proj = binding_energies_by_name.get(proj_name, 0.0)

            if be_proj > 0:
                self.proj_overlap.binding_energy.setValue(be_proj)

        # Calculate target/residual binding energy (neutron/proton separation energy)
        # For A(a,b)B: residual = target + x, so BE = mass(target) + mass(x) - mass(residual)
        if reaction.target and reaction.residual and reaction.projectile and reaction.ejectile:
            # First try to look up in known separation energies table
            resid_symbol = reaction.residual.symbol.lower()
            resid_a = reaction.residual.mass_number
            separation_energies = {
                ('c', 13): 4.946,   # 13C neutron separation
                ('c', 14): 8.176,   # 14C neutron separation
                ('o', 17): 4.143,   # 17O neutron separation
                ('o', 18): 8.045,   # 18O neutron separation
                ('ca', 41): 8.363,  # 41Ca neutron separation
                ('ca', 49): 5.146,  # 49Ca neutron separation
                ('n', 15): 10.833,  # 15N neutron separation
                ('si', 29): 8.473,  # 29Si neutron separation
            }

            be_resid = separation_energies.get((resid_symbol, resid_a), None)

            if be_resid is None:
                # Calculate from Q-value if available
                # Q = BE_proj - BE_resid  =>  BE_resid = BE_proj - Q
                if reaction.q_value is not None and be_proj > 0:
                    be_resid = be_proj - reaction.q_value
                    if be_resid <= 0:
                        be_resid = 5.0  # Default fallback
                else:
                    be_resid = 5.0  # Default fallback

            self.target_overlap.binding_energy.setValue(be_resid)

        self.run_validation()

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        return StepData(
            values={
                'projectile_overlap': self.proj_overlap.get_data(),
                'target_overlap': self.target_overlap.get_data(),
                'spectroscopic_proj': self.spec_proj.value(),
                'spectroscopic_target': self.spec_target.value(),
            },
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data"""
        if 'projectile_overlap' in data:
            self.proj_overlap.set_data(data['projectile_overlap'])
        if 'target_overlap' in data:
            self.target_overlap.set_data(data['target_overlap'])
        if 'spectroscopic_proj' in data:
            self.spec_proj.setValue(data['spectroscopic_proj'])
        if 'spectroscopic_target' in data:
            self.spec_target.setValue(data['spectroscopic_target'])

    def validate(self):
        """Validate current step"""
        messages = []

        # Check binding energies
        proj_be = self.proj_overlap.binding_energy.value()
        if proj_be <= 0:
            messages.append(ValidationMessage(
                level='error',
                message='Projectile binding energy must be positive',
                parameter='projectile_overlap.binding_energy'
            ))

        target_be = self.target_overlap.binding_energy.value()
        if target_be <= 0:
            messages.append(ValidationMessage(
                level='error',
                message='Target binding energy must be positive',
                parameter='target_overlap.binding_energy'
            ))

        # Check spectroscopic factors
        if self.spec_proj.value() <= 0 or self.spec_proj.value() > 2:
            messages.append(ValidationMessage(
                level='warning',
                message='Unusual projectile spectroscopic factor',
                suggestion='Typical values are 0.5-1.0'
            ))

        if self.spec_target.value() <= 0 or self.spec_target.value() > 2:
            messages.append(ValidationMessage(
                level='warning',
                message='Unusual target spectroscopic factor',
                suggestion='Typical values are 0.5-1.0'
            ))

        # Success
        if not any(m.level == 'error' for m in messages):
            messages.append(ValidationMessage(
                level='success',
                message=f'Overlap functions configured (BE: {proj_be:.3f}, {target_be:.3f} MeV)'
            ))

        return messages
