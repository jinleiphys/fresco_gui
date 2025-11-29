"""
States Step for FRESCO Studio Wizard

Step for inelastic scattering: Define target excited states.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QFrame, QGridLayout,
    QGroupBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt

from wizard_step_widget import WizardStepWidget, ValidationMessage
from reaction_parser import ParsedReaction


class StatesStep(WizardStepWidget):
    """
    Inelastic Scattering Step: Define Target Excited States.

    Configure the states of the target nucleus that will be
    populated in inelastic scattering:
    - Ground state (always present)
    - Excited states with energy, spin, parity
    """

    def __init__(self):
        super().__init__(
            step_id="states",
            title="Target States (Inelastic)",
            description="Define the ground and excited states of the target nucleus. "
                        "Each state has an excitation energy, spin, and parity."
        )
        self.parsed_reaction: ParsedReaction = None

    def init_step_ui(self):
        """Initialize the step UI"""
        # States table
        states_group = self.create_group_box("Target Nuclear States")
        states_layout = QVBoxLayout(states_group)

        # Info label
        self.target_info = QLabel("Target: -")
        self.target_info.setStyleSheet("""
            color: #2563eb;
            font-weight: 500;
            padding: 8px;
            background-color: #eff6ff;
            border-radius: 4px;
        """)
        states_layout.addWidget(self.target_info)

        # States table
        self.states_table = QTableWidget()
        self.states_table.setColumnCount(5)
        self.states_table.setHorizontalHeaderLabels([
            "State #", "Ex (MeV)", "Spin (J)", "Parity", "Band"
        ])
        self.states_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.states_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.states_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #d1d5db;
                font-weight: 600;
            }
        """)
        self.states_table.itemChanged.connect(self._on_table_changed)
        states_layout.addWidget(self.states_table)

        # Add/Remove buttons
        btn_row = QHBoxLayout()

        add_btn = QPushButton("+ Add State")
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
        add_btn.clicked.connect(self._add_state)
        btn_row.addWidget(add_btn)

        remove_btn = QPushButton("- Remove Selected")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #fee2e2;
                color: #991b1b;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #fecaca;
            }
        """)
        remove_btn.clicked.connect(self._remove_state)
        btn_row.addWidget(remove_btn)

        btn_row.addStretch()
        states_layout.addLayout(btn_row)

        self.content_layout.addWidget(states_group)

        # Common states presets
        presets_group = self.create_group_box("Common Configurations")
        presets_layout = QHBoxLayout(presets_group)

        presets = [
            ("2+ rotational band", self._preset_rotational),
            ("3- octupole", self._preset_octupole),
            ("Giant resonance", self._preset_giant_resonance),
        ]

        for name, callback in presets:
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
            btn.clicked.connect(callback)
            presets_layout.addWidget(btn)

        presets_layout.addStretch()
        self.content_layout.addWidget(presets_group)

        # Physics notes
        notes_group = self.create_group_box("Physics Notes")
        notes_layout = QVBoxLayout(notes_group)

        notes = QLabel(
            "<b>Excitation Energy (Ex):</b> Energy above the ground state in MeV.<br><br>"
            "<b>Spin (J):</b> Total angular momentum quantum number.<br><br>"
            "<b>Parity:</b> +1 for even parity, -1 for odd parity.<br><br>"
            "<b>Band:</b> Collective band index (0 = ground state band)."
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

        # Add ground state by default
        self._add_ground_state()

    def _add_ground_state(self):
        """Add the ground state (always required)"""
        self.states_table.setRowCount(1)

        # State number (read-only)
        state_item = QTableWidgetItem("1")
        state_item.setFlags(state_item.flags() & ~Qt.ItemIsEditable)
        self.states_table.setItem(0, 0, state_item)

        # Excitation energy (0 for ground state)
        ex_item = QTableWidgetItem("0.0")
        self.states_table.setItem(0, 1, ex_item)

        # Spin
        spin_item = QTableWidgetItem("0.0")
        self.states_table.setItem(0, 2, spin_item)

        # Parity
        parity_item = QTableWidgetItem("+1")
        self.states_table.setItem(0, 3, parity_item)

        # Band
        band_item = QTableWidgetItem("0")
        self.states_table.setItem(0, 4, band_item)

    def _add_state(self):
        """Add a new excited state"""
        row = self.states_table.rowCount()
        self.states_table.setRowCount(row + 1)

        # State number
        state_item = QTableWidgetItem(str(row + 1))
        state_item.setFlags(state_item.flags() & ~Qt.ItemIsEditable)
        self.states_table.setItem(row, 0, state_item)

        # Default values
        self.states_table.setItem(row, 1, QTableWidgetItem("1.0"))  # Ex
        self.states_table.setItem(row, 2, QTableWidgetItem("2.0"))  # Spin
        self.states_table.setItem(row, 3, QTableWidgetItem("+1"))   # Parity
        self.states_table.setItem(row, 4, QTableWidgetItem("0"))    # Band

        self.emit_data_changed()

    def _remove_state(self):
        """Remove selected state (cannot remove ground state)"""
        row = self.states_table.currentRow()
        if row > 0:  # Don't remove ground state
            self.states_table.removeRow(row)
            self._renumber_states()
            self.emit_data_changed()

    def _renumber_states(self):
        """Renumber states after removal"""
        for row in range(self.states_table.rowCount()):
            item = self.states_table.item(row, 0)
            if item:
                item.setText(str(row + 1))

    def _on_table_changed(self, item):
        """Handle table cell changes"""
        self.emit_data_changed()

    def _preset_rotational(self):
        """Apply 2+ rotational band preset"""
        # Clear existing states except ground state
        self.states_table.setRowCount(1)

        # Add typical rotational band states: 0+, 2+, 4+
        states = [
            (0.0, 0.0, "+1", 0),   # Ground state
            (1.33, 2.0, "+1", 0),  # First 2+
            (4.0, 4.0, "+1", 0),   # First 4+
        ]

        self.states_table.setRowCount(len(states))
        for row, (ex, spin, parity, band) in enumerate(states):
            state_item = QTableWidgetItem(str(row + 1))
            state_item.setFlags(state_item.flags() & ~Qt.ItemIsEditable)
            self.states_table.setItem(row, 0, state_item)
            self.states_table.setItem(row, 1, QTableWidgetItem(str(ex)))
            self.states_table.setItem(row, 2, QTableWidgetItem(str(spin)))
            self.states_table.setItem(row, 3, QTableWidgetItem(parity))
            self.states_table.setItem(row, 4, QTableWidgetItem(str(band)))

        self.emit_data_changed()

    def _preset_octupole(self):
        """Apply 3- octupole state preset"""
        self.states_table.setRowCount(1)

        states = [
            (0.0, 0.0, "+1", 0),   # Ground state
            (2.5, 3.0, "-1", 0),   # 3- octupole
        ]

        self.states_table.setRowCount(len(states))
        for row, (ex, spin, parity, band) in enumerate(states):
            state_item = QTableWidgetItem(str(row + 1))
            state_item.setFlags(state_item.flags() & ~Qt.ItemIsEditable)
            self.states_table.setItem(row, 0, state_item)
            self.states_table.setItem(row, 1, QTableWidgetItem(str(ex)))
            self.states_table.setItem(row, 2, QTableWidgetItem(str(spin)))
            self.states_table.setItem(row, 3, QTableWidgetItem(parity))
            self.states_table.setItem(row, 4, QTableWidgetItem(str(band)))

        self.emit_data_changed()

    def _preset_giant_resonance(self):
        """Apply giant resonance preset"""
        self.states_table.setRowCount(1)

        states = [
            (0.0, 0.0, "+1", 0),   # Ground state
            (15.0, 1.0, "-1", 0),  # Giant dipole resonance
        ]

        self.states_table.setRowCount(len(states))
        for row, (ex, spin, parity, band) in enumerate(states):
            state_item = QTableWidgetItem(str(row + 1))
            state_item.setFlags(state_item.flags() & ~Qt.ItemIsEditable)
            self.states_table.setItem(row, 0, state_item)
            self.states_table.setItem(row, 1, QTableWidgetItem(str(ex)))
            self.states_table.setItem(row, 2, QTableWidgetItem(str(spin)))
            self.states_table.setItem(row, 3, QTableWidgetItem(parity))
            self.states_table.setItem(row, 4, QTableWidgetItem(str(band)))

        self.emit_data_changed()

    def set_reaction(self, reaction: ParsedReaction):
        """Update from parsed reaction"""
        self.parsed_reaction = reaction

        if reaction.target:
            self.target_info.setText(f"Target: {reaction.target.name}")

        self.run_validation()

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        states = []
        for row in range(self.states_table.rowCount()):
            try:
                state = {
                    'state_number': int(self.states_table.item(row, 0).text()),
                    'excitation': float(self.states_table.item(row, 1).text()),
                    'spin': float(self.states_table.item(row, 2).text()),
                    'parity': self.states_table.item(row, 3).text(),
                    'band': int(self.states_table.item(row, 4).text()),
                }
                states.append(state)
            except (ValueError, AttributeError):
                pass

        return StepData(
            values={'states': states},
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data from external source"""
        if 'states' not in data:
            return

        states = data['states']
        self.states_table.setRowCount(len(states))

        for row, state in enumerate(states):
            state_item = QTableWidgetItem(str(state.get('state_number', row + 1)))
            state_item.setFlags(state_item.flags() & ~Qt.ItemIsEditable)
            self.states_table.setItem(row, 0, state_item)
            self.states_table.setItem(row, 1, QTableWidgetItem(str(state.get('excitation', 0.0))))
            self.states_table.setItem(row, 2, QTableWidgetItem(str(state.get('spin', 0.0))))
            self.states_table.setItem(row, 3, QTableWidgetItem(state.get('parity', '+1')))
            self.states_table.setItem(row, 4, QTableWidgetItem(str(state.get('band', 0))))

    def validate(self):
        """Validate current step"""
        messages = []

        if self.states_table.rowCount() < 1:
            messages.append(ValidationMessage(
                level='error',
                message='At least one state (ground state) is required'
            ))
            return messages

        # Check ground state
        try:
            gs_ex = float(self.states_table.item(0, 1).text())
            if gs_ex != 0.0:
                messages.append(ValidationMessage(
                    level='warning',
                    message='Ground state should have Ex = 0',
                    parameter='states[0].excitation'
                ))
        except (ValueError, AttributeError):
            messages.append(ValidationMessage(
                level='error',
                message='Invalid ground state excitation energy'
            ))

        # Check for at least one excited state for inelastic
        if self.states_table.rowCount() < 2:
            messages.append(ValidationMessage(
                level='warning',
                message='No excited states defined - this is elastic scattering',
                suggestion='Add at least one excited state for inelastic scattering'
            ))

        # Success if no errors
        if not any(m.level == 'error' for m in messages):
            n_states = self.states_table.rowCount()
            messages.append(ValidationMessage(
                level='success',
                message=f'{n_states} state(s) configured'
            ))

        return messages
