"""
Transferred Particle Step for FRESCO Studio Wizard

Step for transfer reactions: Define the transferred particle/cluster.
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
from reaction_parser import ParsedReaction, ReactionType, get_transferred_particle, is_stripping_reaction
from mass_database import NucleusInfo


class TransferredParticleStep(WizardStepWidget):
    """
    Transfer Reaction Step: Transferred Particle Configuration.

    Define the transferred particle/cluster:
    - Automatically detected from reaction (a - b = x for stripping)
    - Quantum numbers (n, l, j) for the transferred particle
    - Binding configuration
    """

    def __init__(self):
        super().__init__(
            step_id="transferred_particle",
            title="Transferred Particle",
            description="Configure the transferred particle or cluster. For stripping reactions (d,p), "
                        "the projectile transfers nucleons to the target. For pickup, the target "
                        "loses nucleons to the projectile."
        )
        self.parsed_reaction: ParsedReaction = None
        self.transferred: NucleusInfo = None

    def init_step_ui(self):
        """Initialize the step UI"""
        # Transfer mechanism
        mechanism_group = self.create_group_box("Transfer Mechanism")
        mechanism_layout = QVBoxLayout(mechanism_group)

        self.mechanism_label = QLabel("Detecting...")
        self.mechanism_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            padding: 8px;
            background-color: #fef3c7;
            color: #92400e;
            border-radius: 4px;
        """)
        mechanism_layout.addWidget(self.mechanism_label)

        self.content_layout.addWidget(mechanism_group)

        # Transferred particle info
        particle_group = self.create_group_box("Transferred Particle")
        particle_layout = QGridLayout(particle_group)
        particle_layout.setSpacing(12)

        # Name/Symbol
        particle_layout.addWidget(QLabel("Particle:"), 0, 0)
        self.particle_label = QLabel("-")
        self.particle_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        particle_layout.addWidget(self.particle_label, 0, 1)

        # Mass number
        particle_layout.addWidget(QLabel("Mass Number (A):"), 1, 0)
        self.mass_number = QSpinBox()
        self.mass_number.setRange(1, 20)
        self.mass_number.valueChanged.connect(self.emit_data_changed)
        particle_layout.addWidget(self.mass_number, 1, 1)

        # Atomic number
        particle_layout.addWidget(QLabel("Atomic Number (Z):"), 2, 0)
        self.atomic_number = QSpinBox()
        self.atomic_number.setRange(0, 10)
        self.atomic_number.valueChanged.connect(self.emit_data_changed)
        particle_layout.addWidget(self.atomic_number, 2, 1)

        self.content_layout.addWidget(particle_group)

        # Quantum numbers for the transferred particle in projectile
        proj_group = self.create_group_box("In Projectile (Core + x)")
        proj_layout = QGridLayout(proj_group)
        proj_layout.setSpacing(12)

        # Principal quantum number
        proj_layout.addWidget(QLabel("Node number (n):"), 0, 0)
        self.proj_n = QSpinBox()
        self.proj_n.setRange(0, 10)
        self.proj_n.setValue(0)
        self.proj_n.setToolTip("Number of radial nodes (n-1 in spectroscopic notation)")
        self.proj_n.valueChanged.connect(self.emit_data_changed)
        proj_layout.addWidget(self.proj_n, 0, 1)

        # Orbital angular momentum
        proj_layout.addWidget(QLabel("Orbital (l):"), 1, 0)
        self.proj_l = QSpinBox()
        self.proj_l.setRange(0, 10)
        self.proj_l.setValue(0)
        self.proj_l.setToolTip("Orbital angular momentum quantum number")
        self.proj_l.valueChanged.connect(self.emit_data_changed)
        proj_layout.addWidget(self.proj_l, 1, 1)

        # Total angular momentum
        proj_layout.addWidget(QLabel("Total J (2j):"), 2, 0)
        self.proj_j2 = QSpinBox()
        self.proj_j2.setRange(1, 21)
        self.proj_j2.setValue(1)
        self.proj_j2.setToolTip("2 × total angular momentum (e.g., 1 for j=1/2)")
        self.proj_j2.valueChanged.connect(self.emit_data_changed)
        proj_layout.addWidget(self.proj_j2, 2, 1)

        self.content_layout.addWidget(proj_group)

        # Quantum numbers in target/residual
        target_group = self.create_group_box("In Target/Residual (Core + x)")
        target_layout = QGridLayout(target_group)
        target_layout.setSpacing(12)

        target_layout.addWidget(QLabel("Node number (n):"), 0, 0)
        self.target_n = QSpinBox()
        self.target_n.setRange(0, 10)
        self.target_n.setValue(1)
        self.target_n.valueChanged.connect(self.emit_data_changed)
        target_layout.addWidget(self.target_n, 0, 1)

        target_layout.addWidget(QLabel("Orbital (l):"), 1, 0)
        self.target_l = QSpinBox()
        self.target_l.setRange(0, 10)
        self.target_l.setValue(2)
        self.target_l.valueChanged.connect(self.emit_data_changed)
        target_layout.addWidget(self.target_l, 1, 1)

        target_layout.addWidget(QLabel("Total J (2j):"), 2, 0)
        self.target_j2 = QSpinBox()
        self.target_j2.setRange(1, 21)
        self.target_j2.setValue(5)
        self.target_j2.valueChanged.connect(self.emit_data_changed)
        target_layout.addWidget(self.target_j2, 2, 1)

        self.content_layout.addWidget(target_group)

        # Common transfers preset
        presets_group = self.create_group_box("Common Transfers")
        presets_layout = QHBoxLayout(presets_group)

        presets = [
            ("Neutron (1s₁/₂)", 1, 0, (0, 0, 1), (0, 0, 1)),
            ("Neutron (1p₃/₂)", 1, 0, (0, 1, 3), (0, 1, 3)),
            ("Neutron (1d₅/₂)", 1, 0, (0, 2, 5), (1, 2, 5)),
            ("Proton (1d₅/₂)", 1, 1, (0, 2, 5), (1, 2, 5)),
        ]

        for name, a, z, proj_qn, targ_qn in presets:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f3f4f6;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 6px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e5e7eb;
                }
            """)
            btn.clicked.connect(
                lambda _, a=a, z=z, p=proj_qn, t=targ_qn: self._apply_preset(a, z, p, t)
            )
            presets_layout.addWidget(btn)

        presets_layout.addStretch()
        self.content_layout.addWidget(presets_group)

        # Physics notes
        notes_group = self.create_group_box("Physics Notes")
        notes_layout = QVBoxLayout(notes_group)

        notes = QLabel(
            "<b>Stripping:</b> a → b + x (projectile loses nucleons)<br>"
            "Example: (d,p) transfers a neutron from deuteron to target<br><br>"
            "<b>Pickup:</b> A + x → B (target loses nucleons)<br>"
            "Example: (p,d) picks up a neutron from target<br><br>"
            "<b>Quantum numbers:</b><br>"
            "• n: Number of radial nodes (n=0 for 1s, 1p, 1d, etc.)<br>"
            "• l: Orbital angular momentum (s=0, p=1, d=2, f=3, ...)<br>"
            "• j: Total angular momentum = l ± 1/2 (stored as 2j)"
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

    def _apply_preset(self, a: int, z: int, proj_qn: tuple, targ_qn: tuple):
        """Apply a preset configuration"""
        self.mass_number.setValue(a)
        self.atomic_number.setValue(z)

        self.proj_n.setValue(proj_qn[0])
        self.proj_l.setValue(proj_qn[1])
        self.proj_j2.setValue(proj_qn[2])

        self.target_n.setValue(targ_qn[0])
        self.target_l.setValue(targ_qn[1])
        self.target_j2.setValue(targ_qn[2])

        self.emit_data_changed()

    def set_reaction(self, reaction: ParsedReaction):
        """Update from parsed reaction"""
        self.parsed_reaction = reaction

        if reaction.reaction_type != ReactionType.TRANSFER:
            return

        # Determine transfer mechanism
        is_stripping = is_stripping_reaction(reaction)
        if is_stripping:
            self.mechanism_label.setText(
                f"Stripping Reaction: {reaction.projectile.name} → "
                f"{reaction.ejectile.name} + x"
            )
            self.mechanism_label.setStyleSheet("""
                font-size: 14px;
                font-weight: 500;
                padding: 8px;
                background-color: #d1fae5;
                color: #065f46;
                border-radius: 4px;
            """)
        else:
            self.mechanism_label.setText(
                f"Pickup Reaction: {reaction.target.name} + x → "
                f"{reaction.residual.name}"
            )
            self.mechanism_label.setStyleSheet("""
                font-size: 14px;
                font-weight: 500;
                padding: 8px;
                background-color: #dbeafe;
                color: #1e40af;
                border-radius: 4px;
            """)

        # Get transferred particle
        self.transferred = get_transferred_particle(reaction)
        if self.transferred:
            self.particle_label.setText(self.transferred.name)
            self.mass_number.setValue(self.transferred.mass_number)
            self.atomic_number.setValue(self.transferred.atomic_number)

        self.run_validation()

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        return StepData(
            values={
                'transferred_a': self.mass_number.value(),
                'transferred_z': self.atomic_number.value(),
                'projectile_quantum': {
                    'n': self.proj_n.value(),
                    'l': self.proj_l.value(),
                    'j2': self.proj_j2.value(),
                },
                'target_quantum': {
                    'n': self.target_n.value(),
                    'l': self.target_l.value(),
                    'j2': self.target_j2.value(),
                },
            },
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data"""
        if 'transferred_a' in data:
            self.mass_number.setValue(data['transferred_a'])
        if 'transferred_z' in data:
            self.atomic_number.setValue(data['transferred_z'])

        if 'projectile_quantum' in data:
            pq = data['projectile_quantum']
            self.proj_n.setValue(pq.get('n', 0))
            self.proj_l.setValue(pq.get('l', 0))
            self.proj_j2.setValue(pq.get('j2', 1))

        if 'target_quantum' in data:
            tq = data['target_quantum']
            self.target_n.setValue(tq.get('n', 0))
            self.target_l.setValue(tq.get('l', 0))
            self.target_j2.setValue(tq.get('j2', 1))

    def validate(self):
        """Validate current step"""
        messages = []

        a = self.mass_number.value()
        z = self.atomic_number.value()

        if z > a:
            messages.append(ValidationMessage(
                level='error',
                message='Transferred Z cannot exceed A',
                parameter='transferred'
            ))

        # Check j = l ± 1/2 constraint
        proj_l = self.proj_l.value()
        proj_j2 = self.proj_j2.value()

        valid_j2 = [2 * proj_l - 1, 2 * proj_l + 1]
        if proj_l == 0:
            valid_j2 = [1]  # Only j = 1/2 for l = 0

        if proj_j2 not in valid_j2 and proj_j2 > 0:
            messages.append(ValidationMessage(
                level='warning',
                message=f'Projectile: j = l ± 1/2 violated (l={proj_l}, 2j={proj_j2})',
                suggestion=f'Valid 2j values for l={proj_l}: {valid_j2}'
            ))

        target_l = self.target_l.value()
        target_j2 = self.target_j2.value()

        valid_j2 = [2 * target_l - 1, 2 * target_l + 1]
        if target_l == 0:
            valid_j2 = [1]

        if target_j2 not in valid_j2 and target_j2 > 0:
            messages.append(ValidationMessage(
                level='warning',
                message=f'Target: j = l ± 1/2 violated (l={target_l}, 2j={target_j2})',
                suggestion=f'Valid 2j values for l={target_l}: {valid_j2}'
            ))

        # Success
        if not any(m.level == 'error' for m in messages):
            particle_name = f"A={a}, Z={z}"
            if a == 1 and z == 0:
                particle_name = "neutron"
            elif a == 1 and z == 1:
                particle_name = "proton"
            messages.append(ValidationMessage(
                level='success',
                message=f'Transferred particle: {particle_name}'
            ))

        return messages
