"""
Exit Channel Step for FRESCO Studio Wizard

Step for transfer reactions: Define exit channel (ejectile + residual).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QFrame, QGridLayout,
    QGroupBox, QPushButton
)
from PySide6.QtCore import Signal, Qt

from wizard_step_widget import WizardStepWidget, ValidationMessage
from reaction_parser import ParsedReaction, ReactionType
from mass_database import NucleusInfo, get_default_spin, get_default_parity


class ExitChannelParticleWidget(QWidget):
    """Widget for configuring exit channel particle"""

    data_changed = Signal()

    def __init__(self, title: str, particle_info: NucleusInfo = None):
        super().__init__()
        self.particle_info = particle_info
        self._init_ui(title)
        if particle_info:
            self._populate_from_info(particle_info)

    def _init_ui(self, title: str):
        """Initialize the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #374151;
            padding-bottom: 4px;
        """)
        layout.addWidget(title_label)

        # Properties grid
        grid = QGridLayout()
        grid.setSpacing(8)

        # Name
        grid.addWidget(QLabel("Name:"), 0, 0)
        self.name_label = QLabel("-")
        self.name_label.setStyleSheet("font-weight: 500;")
        grid.addWidget(self.name_label, 0, 1)

        # Mass number
        grid.addWidget(QLabel("A:"), 1, 0)
        self.mass_number = QSpinBox()
        self.mass_number.setRange(1, 300)
        self.mass_number.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.mass_number, 1, 1)

        # Atomic number
        grid.addWidget(QLabel("Z:"), 2, 0)
        self.atomic_number = QSpinBox()
        self.atomic_number.setRange(0, 120)
        self.atomic_number.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.atomic_number, 2, 1)

        # Mass
        grid.addWidget(QLabel("Mass (u):"), 3, 0)
        self.mass = QDoubleSpinBox()
        self.mass.setRange(0.5, 300.0)
        self.mass.setDecimals(6)
        self.mass.setSingleStep(0.001)
        self.mass.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.mass, 3, 1)

        # Spin
        grid.addWidget(QLabel("Spin:"), 4, 0)
        self.spin = QDoubleSpinBox()
        self.spin.setRange(0.0, 20.0)
        self.spin.setDecimals(1)
        self.spin.setSingleStep(0.5)
        self.spin.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.spin, 4, 1)

        # Parity
        grid.addWidget(QLabel("Parity:"), 5, 0)
        self.parity = QComboBox()
        self.parity.addItems(["+1", "-1"])
        self.parity.currentIndexChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.parity, 5, 1)

        layout.addLayout(grid)

        self.setStyleSheet("""
            QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                min-width: 100px;
            }
        """)

    def _populate_from_info(self, info: NucleusInfo):
        """Populate from NucleusInfo"""
        self.name_label.setText(info.name)
        self.mass_number.setValue(info.mass_number)
        self.atomic_number.setValue(info.atomic_number)
        self.mass.setValue(info.mass)

        spin = get_default_spin(info.symbol, info.mass_number)
        if spin is not None:
            self.spin.setValue(abs(spin))

        # Get parity from database (separate from spin)
        parity = get_default_parity(info.symbol, info.mass_number)
        # parity=1 is positive (+1), parity=-1 is negative (-1)
        # ComboBox index: 0 = "+1", 1 = "-1"
        self.parity.setCurrentIndex(0 if parity > 0 else 1)

    def set_particle(self, info: NucleusInfo):
        """Set particle info"""
        self.particle_info = info
        self._populate_from_info(info)

    def get_data(self) -> dict:
        """Get particle data"""
        return {
            'name': self.name_label.text(),
            'mass_number': self.mass_number.value(),
            'atomic_number': self.atomic_number.value(),
            'mass': self.mass.value(),
            'spin': self.spin.value(),
            'parity': 1 if self.parity.currentIndex() == 0 else -1
        }


class ExitChannelStep(WizardStepWidget):
    """
    Transfer Reaction Step: Exit Channel Configuration.

    Configure the ejectile and residual nucleus:
    - Masses, spins, parities (auto-filled from equation)
    - Exit channel potentials
    """

    def __init__(self):
        super().__init__(
            step_id="exit_channel",
            title="Exit Channel (Transfer)",
            description="Configure the exit channel particles: the ejectile (outgoing light particle) "
                        "and the residual nucleus. Values are pre-filled from the reaction equation."
        )
        self.parsed_reaction: ParsedReaction = None

    def init_step_ui(self):
        """Initialize the step UI"""
        # Reaction summary
        summary_group = self.create_group_box("Transfer Reaction")
        summary_layout = QVBoxLayout(summary_group)

        self.reaction_label = QLabel("A(a,b)B")
        self.reaction_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #2563eb;
            padding: 8px;
            background-color: #eff6ff;
            border-radius: 4px;
        """)
        self.reaction_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.reaction_label)

        self.content_layout.addWidget(summary_group)

        # Ejectile configuration
        eject_group = self.create_group_box("Ejectile (b)")
        eject_layout = QVBoxLayout(eject_group)

        self.ejectile_widget = ExitChannelParticleWidget("Outgoing Light Particle")
        self.ejectile_widget.data_changed.connect(self.emit_data_changed)
        eject_layout.addWidget(self.ejectile_widget)

        self.content_layout.addWidget(eject_group)

        # Residual configuration
        resid_group = self.create_group_box("Residual Nucleus (B)")
        resid_layout = QVBoxLayout(resid_group)

        self.residual_widget = ExitChannelParticleWidget("Final Heavy Nucleus")
        self.residual_widget.data_changed.connect(self.emit_data_changed)
        resid_layout.addWidget(self.residual_widget)

        # Excitation energy for residual
        ex_row = QHBoxLayout()
        ex_row.addWidget(QLabel("Excitation Energy:"))

        self.residual_ex = QDoubleSpinBox()
        self.residual_ex.setRange(0.0, 100.0)
        self.residual_ex.setDecimals(3)
        self.residual_ex.setSuffix(" MeV")
        self.residual_ex.setSingleStep(0.1)
        self.residual_ex.valueChanged.connect(self.emit_data_changed)
        ex_row.addWidget(self.residual_ex)

        ex_row.addStretch()
        resid_layout.addLayout(ex_row)

        self.content_layout.addWidget(resid_group)

        # Q-value display
        qvalue_group = self.create_group_box("Reaction Q-value")
        qvalue_layout = QHBoxLayout(qvalue_group)

        qvalue_layout.addWidget(QLabel("Ground state Q-value:"))
        self.qvalue_label = QLabel("-")
        self.qvalue_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        qvalue_layout.addWidget(self.qvalue_label)
        qvalue_layout.addStretch()

        self.content_layout.addWidget(qvalue_group)

        # Physics notes
        notes_group = self.create_group_box("Physics Notes")
        notes_layout = QVBoxLayout(notes_group)

        notes = QLabel(
            "<b>Exit Channel:</b> The final state of the reaction, consisting of:<br>"
            "• <b>Ejectile</b>: The light particle emitted (e.g., proton in (d,p))<br>"
            "• <b>Residual</b>: The heavy nucleus left behind<br><br>"
            "<b>Q-value:</b> Energy released (Q > 0) or absorbed (Q < 0) in the reaction.<br>"
            "Calculated from mass difference: Q = (m_a + m_A - m_b - m_B) × c²"
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

    def set_reaction(self, reaction: ParsedReaction):
        """Update from parsed reaction"""
        self.parsed_reaction = reaction

        if reaction.reaction_type != ReactionType.TRANSFER:
            return

        # Update display
        if all([reaction.target, reaction.projectile, reaction.ejectile, reaction.residual]):
            self.reaction_label.setText(
                f"{reaction.target.name}({reaction.projectile.name},"
                f"{reaction.ejectile.name}){reaction.residual.name}"
            )

        if reaction.ejectile:
            self.ejectile_widget.set_particle(reaction.ejectile)

        if reaction.residual:
            self.residual_widget.set_particle(reaction.residual)

        if reaction.q_value is not None:
            self.qvalue_label.setText(f"{reaction.q_value:.3f} MeV")

        self.run_validation()

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        return StepData(
            values={
                'ejectile': self.ejectile_widget.get_data(),
                'residual': self.residual_widget.get_data(),
                'residual_excitation': self.residual_ex.value(),
            },
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data"""
        if 'residual_excitation' in data:
            self.residual_ex.setValue(data['residual_excitation'])

    def validate(self):
        """Validate current step"""
        messages = []

        # Validate ejectile
        eject = self.ejectile_widget.get_data()
        if eject['atomic_number'] > eject['mass_number']:
            messages.append(ValidationMessage(
                level='error',
                message='Ejectile Z cannot exceed A',
                parameter='ejectile'
            ))

        # Validate residual
        resid = self.residual_widget.get_data()
        if resid['atomic_number'] > resid['mass_number']:
            messages.append(ValidationMessage(
                level='error',
                message='Residual Z cannot exceed A',
                parameter='residual'
            ))

        # Success if valid
        if not any(m.level == 'error' for m in messages):
            messages.append(ValidationMessage(
                level='success',
                message='Exit channel configuration is valid'
            ))

        return messages
