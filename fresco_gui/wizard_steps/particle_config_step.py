"""
Particle Configuration Step for FRESCO Studio Wizard

Step 2: Configure particle properties (masses, spins, parities).
Used for elastic and inelastic scattering.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QFrame, QGridLayout,
    QGroupBox, QCheckBox
)
from PySide6.QtCore import Signal, Qt

from wizard_step_widget import WizardStepWidget, ValidationMessage
from reaction_parser import ParsedReaction, ReactionType
from mass_database import NucleusInfo, get_default_spin, get_default_parity


class ParticleWidget(QWidget):
    """Widget for configuring a single particle"""

    data_changed = Signal()

    def __init__(self, title: str, particle_info: NucleusInfo = None):
        super().__init__()
        self.particle_info = particle_info
        self._init_ui(title)
        if particle_info:
            self._populate_from_info(particle_info)

    def _init_ui(self, title: str):
        """Initialize the particle widget UI"""
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

        # Name (read-only display)
        grid.addWidget(QLabel("Name:"), 0, 0)
        self.name_label = QLabel("-")
        self.name_label.setStyleSheet("font-weight: 500;")
        grid.addWidget(self.name_label, 0, 1)

        # Mass number (A)
        grid.addWidget(QLabel("Mass Number (A):"), 1, 0)
        self.mass_number = QSpinBox()
        self.mass_number.setRange(1, 300)
        self.mass_number.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.mass_number, 1, 1)

        # Atomic number (Z)
        grid.addWidget(QLabel("Atomic Number (Z):"), 2, 0)
        self.atomic_number = QSpinBox()
        self.atomic_number.setRange(0, 120)
        self.atomic_number.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.atomic_number, 2, 1)

        # Mass (in atomic mass units)
        grid.addWidget(QLabel("Mass (u):"), 3, 0)
        self.mass = QDoubleSpinBox()
        self.mass.setRange(0.5, 300.0)
        self.mass.setDecimals(6)
        self.mass.setSingleStep(0.001)
        self.mass.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.mass, 3, 1)

        # Spin
        grid.addWidget(QLabel("Spin (ℏ):"), 4, 0)
        self.spin = QDoubleSpinBox()
        self.spin.setRange(0.0, 20.0)
        self.spin.setDecimals(1)
        self.spin.setSingleStep(0.5)
        self.spin.valueChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.spin, 4, 1)

        # Parity
        grid.addWidget(QLabel("Parity:"), 5, 0)
        self.parity = QComboBox()
        self.parity.addItems(["+1 (even)", "-1 (odd)"])
        self.parity.currentIndexChanged.connect(lambda _: self.data_changed.emit())
        grid.addWidget(self.parity, 5, 1)

        layout.addLayout(grid)

        # Style the widget
        self.setStyleSheet("""
            QSpinBox, QDoubleSpinBox, QComboBox {
                padding: 6px 10px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                min-width: 100px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #2563eb;
            }
        """)

    def _populate_from_info(self, info: NucleusInfo):
        """Populate widgets from NucleusInfo"""
        self.name_label.setText(info.name)
        self.mass_number.setValue(info.mass_number)
        self.atomic_number.setValue(info.atomic_number)
        self.mass.setValue(info.mass)

        # Get default spin
        spin = get_default_spin(info.symbol, info.mass_number)
        if spin is not None:
            self.spin.setValue(abs(spin))
        else:
            self.spin.setValue(0.0)

        # Get parity from database (separate from spin)
        parity = get_default_parity(info.symbol, info.mass_number)
        # parity=1 is positive (+1), parity=-1 is negative (-1)
        # ComboBox index: 0 = "+1 (even)", 1 = "-1 (odd)"
        self.parity.setCurrentIndex(0 if parity > 0 else 1)

    def set_particle(self, info: NucleusInfo):
        """Set particle information"""
        self.particle_info = info
        self._populate_from_info(info)

    def get_data(self) -> dict:
        """Get particle data as dictionary"""
        return {
            'name': self.name_label.text(),
            'mass_number': self.mass_number.value(),
            'atomic_number': self.atomic_number.value(),
            'mass': self.mass.value(),
            'spin': self.spin.value(),
            'parity': 1 if self.parity.currentIndex() == 0 else -1
        }


class ParticleConfigStep(WizardStepWidget):
    """
    Step 2: Particle configuration.

    Configure projectile and target properties including:
    - Mass numbers and atomic numbers
    - Masses (can be auto-filled from database)
    - Ground state spins and parities
    """

    def __init__(self):
        super().__init__(
            step_id="particle_config",
            title="Particle Configuration",
            description="Configure the properties of the projectile and target nuclei. "
                        "Values are pre-filled from the mass database but can be adjusted."
        )
        self.parsed_reaction: ParsedReaction = None

    def init_step_ui(self):
        """Initialize the step UI"""
        # Projectile configuration
        proj_group = self.create_group_box("Projectile")
        proj_layout = QVBoxLayout(proj_group)

        self.projectile_widget = ParticleWidget("Projectile Nucleus")
        self.projectile_widget.data_changed.connect(self.emit_data_changed)
        proj_layout.addWidget(self.projectile_widget)

        self.content_layout.addWidget(proj_group)

        # Target configuration
        target_group = self.create_group_box("Target")
        target_layout = QVBoxLayout(target_group)

        self.target_widget = ParticleWidget("Target Nucleus")
        self.target_widget.data_changed.connect(self.emit_data_changed)
        target_layout.addWidget(self.target_widget)

        # Excitation energy for inelastic
        self.excitation_frame = QFrame()
        excitation_layout = QHBoxLayout(self.excitation_frame)
        excitation_layout.setContentsMargins(0, 12, 0, 0)

        excitation_label = QLabel("Excitation Energy:")
        excitation_label.setStyleSheet("font-weight: 500; color: #374151;")
        excitation_layout.addWidget(excitation_label)

        self.excitation_energy = QDoubleSpinBox()
        self.excitation_energy.setRange(0.0, 100.0)
        self.excitation_energy.setDecimals(3)
        self.excitation_energy.setSuffix(" MeV")
        self.excitation_energy.setSingleStep(0.1)
        self.excitation_energy.valueChanged.connect(self.emit_data_changed)
        excitation_layout.addWidget(self.excitation_energy)

        excitation_help = QLabel("(For inelastic scattering)")
        excitation_help.setStyleSheet("color: #6b7280; font-size: 12px;")
        excitation_layout.addWidget(excitation_help)
        excitation_layout.addStretch()

        self.excitation_frame.hide()  # Show only for inelastic
        target_layout.addWidget(self.excitation_frame)

        self.content_layout.addWidget(target_group)

        # Physics info box
        info_group = self.create_group_box("Physics Notes")
        info_layout = QVBoxLayout(info_group)

        info_text = QLabel(
            "<b>Mass:</b> Nuclear mass in atomic mass units (u). "
            "1 u = 931.494 MeV/c².<br><br>"
            "<b>Spin:</b> Total angular momentum quantum number J of the ground state. "
            "Common values: 0 for even-even nuclei, half-integer for odd-A nuclei.<br><br>"
            "<b>Parity:</b> Spatial reflection symmetry of the nuclear wave function. "
            "+1 (even) or -1 (odd)."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            color: #4b5563;
            font-size: 12px;
            padding: 8px;
            background-color: #f9fafb;
            border-radius: 4px;
        """)
        info_layout.addWidget(info_text)

        self.content_layout.addWidget(info_group)

        self.content_layout.addStretch()

    def set_reaction(self, reaction: ParsedReaction):
        """Update particle configuration from parsed reaction"""
        self.parsed_reaction = reaction

        if reaction.projectile:
            self.projectile_widget.set_particle(reaction.projectile)

        if reaction.target:
            self.target_widget.set_particle(reaction.target)

        # Show/hide excitation energy based on reaction type
        is_inelastic = reaction.reaction_type == ReactionType.INELASTIC
        self.excitation_frame.setVisible(is_inelastic)

        self.run_validation()

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        data = {
            'projectile': self.projectile_widget.get_data(),
            'target': self.target_widget.get_data(),
        }

        if self.excitation_frame.isVisible():
            data['excitation_energy'] = self.excitation_energy.value()

        return StepData(
            values=data,
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data from external source"""
        # Data setting would be implemented for loading saved wizard states
        pass

    def validate(self):
        """Validate current step"""
        messages = []

        # Validate projectile
        proj_data = self.projectile_widget.get_data()
        if proj_data['mass_number'] < 1:
            messages.append(ValidationMessage(
                level='error',
                message='Projectile mass number must be at least 1',
                parameter='projectile.mass_number'
            ))

        if proj_data['atomic_number'] > proj_data['mass_number']:
            messages.append(ValidationMessage(
                level='error',
                message='Projectile Z cannot exceed A',
                parameter='projectile.atomic_number'
            ))

        # Validate target
        target_data = self.target_widget.get_data()
        if target_data['mass_number'] < 1:
            messages.append(ValidationMessage(
                level='error',
                message='Target mass number must be at least 1',
                parameter='target.mass_number'
            ))

        if target_data['atomic_number'] > target_data['mass_number']:
            messages.append(ValidationMessage(
                level='error',
                message='Target Z cannot exceed A',
                parameter='target.atomic_number'
            ))

        # Validate excitation energy for inelastic
        if self.excitation_frame.isVisible():
            ex = self.excitation_energy.value()
            if ex <= 0:
                messages.append(ValidationMessage(
                    level='warning',
                    message='Excitation energy is 0 - this is elastic scattering',
                    parameter='excitation_energy',
                    suggestion='Set excitation energy > 0 for inelastic scattering'
                ))

        # Success if no errors
        if not any(m.level == 'error' for m in messages):
            messages.append(ValidationMessage(
                level='success',
                message='Particle configuration is valid'
            ))

        return messages
