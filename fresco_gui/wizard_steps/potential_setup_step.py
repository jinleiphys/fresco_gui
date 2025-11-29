"""
Potential Setup Step for FRESCO Studio Wizard

Step 3: Configure optical potentials.
Used for all reaction types.

For transfer reactions, 5 potential sets are needed:
- kp=1: Entrance channel (projectile + target)
- kp=2: Exit channel (ejectile + residual)
- kp=3: Binding potential for projectile core
- kp=4: Binding potential for residual core
- kp=5: Remnant potential (post/prior form)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QFrame, QGridLayout,
    QGroupBox, QCheckBox, QPushButton, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Signal, Qt

from wizard_step_widget import WizardStepWidget, ValidationMessage
from reaction_parser import ParsedReaction, ReactionType


class PotentialComponentWidget(QWidget):
    """Widget for a single potential component (Coulomb, Volume, Surface, etc.)"""

    data_changed = Signal()
    removed = Signal(object)

    # Common optical potential types
    POTENTIAL_TYPES = {
        0: ("Coulomb", ["rc"]),
        1: ("Volume Woods-Saxon", ["V", "r0", "a", "W", "rW", "aW"]),
        2: ("Surface Woods-Saxon", ["Vd", "r0d", "ad", "Wd", "rWd", "aWd"]),
        3: ("Spin-Orbit", ["Vso", "rso", "aso", "Wso", "rsoW", "asoW"]),
    }

    def __init__(self, pot_type: int = 1, kp: int = 1, show_remove: bool = True):
        super().__init__()
        self.pot_type = pot_type
        self.kp = kp
        self.show_remove = show_remove
        self.param_widgets = {}
        self._init_ui()

    def _init_ui(self):
        """Initialize the potential component UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Header with type and remove button
        header = QHBoxLayout()

        type_name = self.POTENTIAL_TYPES.get(self.pot_type, ("Unknown", []))[0]
        self.type_label = QLabel(f"{type_name} Potential")
        self.type_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #374151;")
        header.addWidget(self.type_label)

        header.addStretch()

        if self.show_remove:
            remove_btn = QPushButton("Remove")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fee2e2;
                    color: #991b1b;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #fecaca;
                }
            """)
            remove_btn.clicked.connect(lambda: self.removed.emit(self))
            header.addWidget(remove_btn)

        layout.addLayout(header)

        # Parameters grid
        self._build_params_grid(layout)

        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
            }
            QDoubleSpinBox {
                padding: 4px 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                min-width: 80px;
            }
            QDoubleSpinBox:focus {
                border-color: #2563eb;
            }
        """)

    def _build_params_grid(self, parent_layout):
        """Build parameter input grid based on potential type"""
        grid = QGridLayout()
        grid.setSpacing(8)

        _, params = self.POTENTIAL_TYPES.get(self.pot_type, ("", []))

        # Parameter tooltips and defaults
        param_info = {
            'rc': ('Coulomb radius parameter', 1.25, 'fm'),
            'V': ('Real volume depth', 50.0, 'MeV'),
            'r0': ('Real volume radius', 1.17, 'fm'),
            'a': ('Real volume diffuseness', 0.75, 'fm'),
            'W': ('Imaginary volume depth', 10.0, 'MeV'),
            'rW': ('Imaginary volume radius', 1.32, 'fm'),
            'aW': ('Imaginary volume diffuseness', 0.52, 'fm'),
            'Vd': ('Real surface depth', 0.0, 'MeV'),
            'r0d': ('Real surface radius', 1.32, 'fm'),
            'ad': ('Real surface diffuseness', 0.52, 'fm'),
            'Wd': ('Imaginary surface depth', 10.0, 'MeV'),
            'rWd': ('Imaginary surface radius', 1.32, 'fm'),
            'aWd': ('Imaginary surface diffuseness', 0.52, 'fm'),
            'Vso': ('Real spin-orbit depth', 6.0, 'MeV'),
            'rso': ('Real spin-orbit radius', 1.01, 'fm'),
            'aso': ('Real spin-orbit diffuseness', 0.75, 'fm'),
            'Wso': ('Imaginary spin-orbit depth', 0.0, 'MeV'),
            'rsoW': ('Imaginary spin-orbit radius', 1.01, 'fm'),
            'asoW': ('Imaginary spin-orbit diffuseness', 0.75, 'fm'),
        }

        row = 0
        col = 0
        for param in params:
            tooltip, default, unit = param_info.get(param, (param, 0.0, ''))

            label = QLabel(f"{param}:")
            label.setToolTip(tooltip)
            label.setStyleSheet("border: none; background: transparent;")
            grid.addWidget(label, row, col * 3)

            spinbox = QDoubleSpinBox()
            spinbox.setRange(-1000.0, 1000.0)
            spinbox.setDecimals(2)
            spinbox.setSingleStep(0.1)
            spinbox.setValue(default)
            spinbox.setToolTip(tooltip)
            spinbox.setStyleSheet("border: 1px solid #d1d5db; background: white;")
            spinbox.valueChanged.connect(lambda _: self.data_changed.emit())
            grid.addWidget(spinbox, row, col * 3 + 1)

            unit_label = QLabel(unit)
            unit_label.setStyleSheet("color: #6b7280; font-size: 11px; border: none; background: transparent;")
            grid.addWidget(unit_label, row, col * 3 + 2)

            self.param_widgets[param] = spinbox

            col += 1
            if col >= 2:  # Two params per row
                col = 0
                row += 1

        parent_layout.addLayout(grid)

    def get_data(self) -> dict:
        """Get potential component data"""
        data = {
            'type': self.pot_type,
            'kp': self.kp,
        }
        for param, widget in self.param_widgets.items():
            data[param] = widget.value()
        return data

    def set_data(self, data: dict):
        """Set potential component data"""
        for param, widget in self.param_widgets.items():
            if param in data:
                widget.setValue(data[param])


class PotentialSetWidget(QWidget):
    """Widget for a complete potential set (kp group) containing multiple components"""

    data_changed = Signal()

    def __init__(self, kp: int, title: str, description: str, show_add_remove: bool = True):
        super().__init__()
        self.kp = kp
        self.title = title
        self.description = description
        self.show_add_remove = show_add_remove
        self.potential_widgets = []
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Group box for this potential set
        group = QGroupBox(f"{self.title} (kp={self.kp})")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 8px;
                padding: 12px;
                padding-top: 24px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                background-color: white;
                color: #374151;
            }
        """)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)

        # Description
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("""
            color: #2563eb;
            font-weight: 500;
            padding: 8px;
            background-color: #eff6ff;
            border-radius: 4px;
        """)
        group_layout.addWidget(desc_label)

        # Container for potential components
        self.potentials_container = QVBoxLayout()
        self.potentials_container.setSpacing(8)
        group_layout.addLayout(self.potentials_container)

        # Add potential button (only if allowed)
        if self.show_add_remove:
            add_row = QHBoxLayout()
            add_row.addStretch()

            self.add_pot_combo = QComboBox()
            self.add_pot_combo.addItem("Add Coulomb", 0)
            self.add_pot_combo.addItem("Add Volume W-S", 1)
            self.add_pot_combo.addItem("Add Surface W-S", 2)
            self.add_pot_combo.addItem("Add Spin-Orbit", 3)
            self.add_pot_combo.setStyleSheet("""
                QComboBox {
                    padding: 6px 12px;
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                }
            """)
            add_row.addWidget(self.add_pot_combo)

            add_btn = QPushButton("+ Add")
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
            """)
            add_btn.clicked.connect(self._add_potential)
            add_row.addWidget(add_btn)

            group_layout.addLayout(add_row)

        layout.addWidget(group)

    def _add_potential(self):
        """Add a new potential component"""
        pot_type = self.add_pot_combo.currentData()
        self.add_potential_widget(pot_type)
        self.data_changed.emit()

    def add_potential_widget(self, pot_type: int, data: dict = None):
        """Add a potential widget to the container"""
        widget = PotentialComponentWidget(pot_type, self.kp, show_remove=self.show_add_remove)
        if data:
            widget.set_data(data)
        widget.data_changed.connect(self.data_changed.emit)
        widget.removed.connect(self._remove_potential)
        self.potential_widgets.append(widget)
        self.potentials_container.addWidget(widget)

    def _remove_potential(self, widget):
        """Remove a potential widget"""
        if widget in self.potential_widgets:
            self.potential_widgets.remove(widget)
            self.potentials_container.removeWidget(widget)
            widget.deleteLater()
            self.data_changed.emit()

    def clear_potentials(self):
        """Clear all potential widgets"""
        for widget in self.potential_widgets[:]:
            self.potentials_container.removeWidget(widget)
            widget.deleteLater()
        self.potential_widgets.clear()

    def get_data(self) -> list:
        """Get all potential data for this set"""
        return [w.get_data() for w in self.potential_widgets]


class PotentialSetupStep(WizardStepWidget):
    """
    Step 3: Optical Potential Setup.

    Configure optical potentials for the reaction:
    - For elastic/inelastic: entrance channel potentials only
    - For transfer: 5 potential sets (entrance, exit, binding×2, remnant)
    """

    def __init__(self):
        # Initialize attributes before calling super().__init__()
        self.potential_sets = {}  # kp -> PotentialSetWidget
        self.parsed_reaction: ParsedReaction = None
        self.reaction_type = ReactionType.ELASTIC

        super().__init__(
            step_id="potential_setup",
            title="Optical Potential Setup",
            description="Configure the optical potentials for the reaction."
        )

    def init_step_ui(self):
        """Initialize the step UI"""
        # Main container for potential sets
        self.sets_container = QVBoxLayout()
        self.sets_container.setSpacing(16)
        self.content_layout.addLayout(self.sets_container)

        # Physics notes
        notes_group = self.create_group_box("Potential Notes")
        notes_layout = QVBoxLayout(notes_group)

        notes_text = QLabel(
            "<b>Woods-Saxon Form:</b> V(r) = -V / (1 + exp((r - R)/a)) where R = r₀ × A^(1/3)<br><br>"
            "<b>Coulomb:</b> Point-charge Coulomb for r > Rc, uniform sphere for r < Rc<br>"
            "<b>Volume:</b> Absorbs flux throughout the nuclear interior<br>"
            "<b>Surface:</b> Absorbs flux at the nuclear surface (derivative form)<br>"
            "<b>Spin-Orbit:</b> Thomas form, couples to spin of projectile"
        )
        notes_text.setWordWrap(True)
        notes_text.setStyleSheet("""
            color: #4b5563;
            font-size: 12px;
            padding: 8px;
            background-color: #f9fafb;
            border-radius: 4px;
        """)
        notes_layout.addWidget(notes_text)

        self.content_layout.addWidget(notes_group)
        self.content_layout.addStretch()

        # Setup default (elastic) potentials
        self._setup_elastic_potentials()

    def _clear_all_sets(self):
        """Clear all potential sets"""
        for kp, widget in self.potential_sets.items():
            self.sets_container.removeWidget(widget)
            widget.deleteLater()
        self.potential_sets.clear()

    def _setup_elastic_potentials(self):
        """Setup potentials for elastic scattering (1 set)"""
        self._clear_all_sets()

        # kp=1: Entrance channel
        entrance_set = PotentialSetWidget(
            kp=1,
            title="Entrance Channel",
            description="Projectile + Target interaction"
        )
        entrance_set.data_changed.connect(self.emit_data_changed)
        # Add default potentials
        entrance_set.add_potential_widget(0, {'rc': 1.25})  # Coulomb
        entrance_set.add_potential_widget(1, {  # Volume
            'V': 50.0, 'r0': 1.17, 'a': 0.75,
            'W': 10.0, 'rW': 1.32, 'aW': 0.52
        })

        self.potential_sets[1] = entrance_set
        self.sets_container.addWidget(entrance_set)

    def _setup_transfer_potentials(self):
        """Setup potentials for transfer reactions (5 sets)"""
        self._clear_all_sets()

        proj_name = "Projectile"
        targ_name = "Target"
        eject_name = "Ejectile"
        resid_name = "Residual"

        if self.parsed_reaction:
            if self.parsed_reaction.projectile:
                proj_name = self.parsed_reaction.projectile.name
            if self.parsed_reaction.target:
                targ_name = self.parsed_reaction.target.name
            if self.parsed_reaction.ejectile:
                eject_name = self.parsed_reaction.ejectile.name
            if self.parsed_reaction.residual:
                resid_name = self.parsed_reaction.residual.name

        # kp=1: Entrance channel (projectile + target)
        entrance_set = PotentialSetWidget(
            kp=1,
            title="Entrance Channel",
            description=f"{proj_name} + {targ_name} interaction"
        )
        entrance_set.data_changed.connect(self.emit_data_changed)
        entrance_set.add_potential_widget(0, {'rc': 1.30})
        entrance_set.add_potential_widget(1, {
            'V': 37.2, 'r0': 1.2, 'a': 0.6,
            'W': 21.6, 'rW': 1.2, 'aW': 0.69
        })
        self.potential_sets[1] = entrance_set
        self.sets_container.addWidget(entrance_set)

        # kp=2: Exit channel (ejectile + residual)
        exit_set = PotentialSetWidget(
            kp=2,
            title="Exit Channel",
            description=f"{eject_name} + {resid_name} interaction"
        )
        exit_set.data_changed.connect(self.emit_data_changed)
        exit_set.add_potential_widget(0, {'rc': 1.30})
        exit_set.add_potential_widget(1, {
            'V': 37.2, 'r0': 1.2, 'a': 0.6,
            'W': 21.6, 'rW': 1.2, 'aW': 0.69
        })
        self.potential_sets[2] = exit_set
        self.sets_container.addWidget(exit_set)

        # kp=3: Binding potential for projectile core (transferred particle bound to core)
        proj_bind_set = PotentialSetWidget(
            kp=3,
            title="Projectile Binding",
            description=f"Transferred particle bound in {proj_name}"
        )
        proj_bind_set.data_changed.connect(self.emit_data_changed)
        proj_bind_set.add_potential_widget(0, {'rc': 1.2})
        proj_bind_set.add_potential_widget(1, {
            'V': 50.0, 'r0': 1.2, 'a': 0.65,
            'W': 0.0, 'rW': 1.2, 'aW': 0.65
        })
        proj_bind_set.add_potential_widget(3, {  # Spin-orbit
            'Vso': 6.0, 'rso': 1.2, 'aso': 0.65,
            'Wso': 0.0, 'rsoW': 1.2, 'asoW': 0.65
        })
        self.potential_sets[3] = proj_bind_set
        self.sets_container.addWidget(proj_bind_set)

        # kp=4: Binding potential for residual core
        resid_bind_set = PotentialSetWidget(
            kp=4,
            title="Residual Binding",
            description=f"Transferred particle bound in {resid_name}"
        )
        resid_bind_set.data_changed.connect(self.emit_data_changed)
        resid_bind_set.add_potential_widget(0, {'rc': 1.2})
        resid_bind_set.add_potential_widget(1, {
            'V': 50.0, 'r0': 1.2, 'a': 0.65,
            'W': 0.0, 'rW': 1.2, 'aW': 0.65
        })
        resid_bind_set.add_potential_widget(3, {  # Spin-orbit
            'Vso': 6.0, 'rso': 1.2, 'aso': 0.65,
            'Wso': 0.0, 'rsoW': 1.2, 'asoW': 0.65
        })
        self.potential_sets[4] = resid_bind_set
        self.sets_container.addWidget(resid_bind_set)

        # kp=5: Remnant potential (for post/prior form)
        remnant_set = PotentialSetWidget(
            kp=5,
            title="Remnant Potential",
            description=f"Core-core interaction (post/prior)"
        )
        remnant_set.data_changed.connect(self.emit_data_changed)
        remnant_set.add_potential_widget(0, {'rc': 1.30})
        remnant_set.add_potential_widget(1, {
            'V': 37.2, 'r0': 1.2, 'a': 0.6,
            'W': 21.6, 'rW': 1.2, 'aW': 0.69
        })
        self.potential_sets[5] = remnant_set
        self.sets_container.addWidget(remnant_set)

    def set_reaction(self, reaction: ParsedReaction):
        """Update from parsed reaction"""
        self.parsed_reaction = reaction

        # Check if reaction type changed
        if reaction.reaction_type != self.reaction_type:
            self.reaction_type = reaction.reaction_type

            if self.reaction_type == ReactionType.TRANSFER:
                self._setup_transfer_potentials()
            else:
                self._setup_elastic_potentials()
        else:
            # Just update labels
            self._update_labels()

        self.run_validation()

    def _update_labels(self):
        """Update description labels with particle names"""
        if not self.parsed_reaction:
            return

        proj_name = self.parsed_reaction.projectile.name if self.parsed_reaction.projectile else "Projectile"
        targ_name = self.parsed_reaction.target.name if self.parsed_reaction.target else "Target"

        if 1 in self.potential_sets:
            # Find and update the description label
            pass  # For simplicity, rely on rebuild

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        all_potentials = []
        for kp, pot_set in self.potential_sets.items():
            all_potentials.extend(pot_set.get_data())

        return StepData(
            values={
                'potentials': all_potentials,
                'potential_sets': {kp: pot_set.get_data() for kp, pot_set in self.potential_sets.items()}
            },
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data from external source"""
        # For now, just handle the simple case
        pass

    def validate(self):
        """Validate current step"""
        messages = []

        total_pots = sum(len(pot_set.potential_widgets) for pot_set in self.potential_sets.values())

        if total_pots == 0:
            messages.append(ValidationMessage(
                level='error',
                message='At least one potential is required'
            ))
            return messages

        # Check each set has at least Coulomb for charged particles
        for kp, pot_set in self.potential_sets.items():
            has_coulomb = any(w.pot_type == 0 for w in pot_set.potential_widgets)
            if not has_coulomb:
                messages.append(ValidationMessage(
                    level='warning',
                    message=f'No Coulomb potential in set kp={kp}'
                ))

        # For transfer, check all 5 sets are present
        if self.reaction_type == ReactionType.TRANSFER:
            required_sets = {1, 2, 3, 4, 5}
            present_sets = set(self.potential_sets.keys())
            missing = required_sets - present_sets
            if missing:
                messages.append(ValidationMessage(
                    level='error',
                    message=f'Missing potential sets: kp={missing}'
                ))

        # Success
        if not any(m.level == 'error' for m in messages):
            n_sets = len(self.potential_sets)
            messages.append(ValidationMessage(
                level='success',
                message=f'{n_sets} potential set(s), {total_pots} components configured'
            ))

        return messages

    def reset(self):
        """Reset to initial state"""
        self.reaction_type = ReactionType.ELASTIC
        self._setup_elastic_potentials()
        self._is_completed = False
        self._validation_messages = []
