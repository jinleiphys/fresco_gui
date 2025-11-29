"""
Coupling Step for FRESCO Studio Wizard

Step for inelastic scattering: Define couplings between states.
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


class CouplingStep(WizardStepWidget):
    """
    Inelastic Scattering Step: Define Couplings.

    Configure the couplings between states:
    - Deformation parameters (beta_L)
    - Coupling types (Coulomb, nuclear)
    - Multipolarity
    """

    # Coupling types
    COUPLING_KINDS = {
        1: "Deformed Coulomb",
        2: "Deformed Nuclear",
        3: "Deformed Coulomb+Nuclear",
        4: "Rotational model",
        5: "Vibrational model",
    }

    def __init__(self):
        super().__init__(
            step_id="coupling",
            title="State Couplings (Inelastic)",
            description="Define the couplings between the ground state and excited states. "
                        "The coupling strength is typically given by deformation parameters."
        )
        self.states_data = []

    def init_step_ui(self):
        """Initialize the step UI"""
        # Coupling method selection
        method_group = self.create_group_box("Coupling Method")
        method_layout = QHBoxLayout(method_group)

        method_layout.addWidget(QLabel("Coupling type:"))
        self.coupling_kind = QComboBox()
        for kind, name in self.COUPLING_KINDS.items():
            self.coupling_kind.addItem(f"{kind}: {name}", kind)
        self.coupling_kind.setCurrentIndex(2)  # Default to Coulomb+Nuclear
        self.coupling_kind.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                min-width: 200px;
            }
        """)
        self.coupling_kind.currentIndexChanged.connect(self.emit_data_changed)
        method_layout.addWidget(self.coupling_kind)
        method_layout.addStretch()

        self.content_layout.addWidget(method_group)

        # Couplings table
        couplings_group = self.create_group_box("Coupling Definitions")
        couplings_layout = QVBoxLayout(couplings_group)

        self.couplings_table = QTableWidget()
        self.couplings_table.setColumnCount(6)
        self.couplings_table.setHorizontalHeaderLabels([
            "From State", "To State", "Multipolarity (L)", "β_L", "Deform. Length", "POT #"
        ])
        self.couplings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.couplings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.couplings_table.setStyleSheet("""
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
        self.couplings_table.itemChanged.connect(self._on_table_changed)
        couplings_layout.addWidget(self.couplings_table)

        # Add/Remove buttons
        btn_row = QHBoxLayout()

        add_btn = QPushButton("+ Add Coupling")
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
        add_btn.clicked.connect(self._add_coupling)
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
        remove_btn.clicked.connect(self._remove_coupling)
        btn_row.addWidget(remove_btn)

        btn_row.addStretch()
        couplings_layout.addLayout(btn_row)

        self.content_layout.addWidget(couplings_group)

        # Deformation parameter help
        help_group = self.create_group_box("Parameter Guide")
        help_layout = QVBoxLayout(help_group)

        help_text = QLabel(
            "<b>Multipolarity (L):</b> Angular momentum transfer. Common values:<br>"
            "• L=2: Quadrupole (most common for rotational nuclei)<br>"
            "• L=3: Octupole<br>"
            "• L=1: Dipole (giant resonances)<br><br>"
            "<b>Deformation parameter (β_L):</b> Measures nuclear deformation<br>"
            "• Typical β₂ ≈ 0.2-0.3 for well-deformed nuclei<br>"
            "• Can be positive or negative depending on shape<br><br>"
            "<b>Deformation length:</b> δ = β_L × R₀ × A^(1/3) (calculated automatically if 0)"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("""
            color: #4b5563;
            font-size: 12px;
            padding: 8px;
            background-color: #f9fafb;
            border-radius: 4px;
        """)
        help_layout.addWidget(help_text)

        self.content_layout.addWidget(help_group)
        self.content_layout.addStretch()

    def _add_coupling(self):
        """Add a new coupling definition"""
        row = self.couplings_table.rowCount()
        self.couplings_table.setRowCount(row + 1)

        # Default values: 0 -> 1 transition, L=2
        self.couplings_table.setItem(row, 0, QTableWidgetItem("1"))    # From state
        self.couplings_table.setItem(row, 1, QTableWidgetItem("2"))    # To state
        self.couplings_table.setItem(row, 2, QTableWidgetItem("2"))    # Multipolarity
        self.couplings_table.setItem(row, 3, QTableWidgetItem("0.25")) # Beta
        self.couplings_table.setItem(row, 4, QTableWidgetItem("0"))    # Deform length
        self.couplings_table.setItem(row, 5, QTableWidgetItem("1"))    # POT number

        self.emit_data_changed()

    def _remove_coupling(self):
        """Remove selected coupling"""
        row = self.couplings_table.currentRow()
        if row >= 0:
            self.couplings_table.removeRow(row)
            self.emit_data_changed()

    def _on_table_changed(self, item):
        """Handle table cell changes"""
        self.emit_data_changed()

    def set_states(self, states: list):
        """Update with states from previous step"""
        self.states_data = states

        # Auto-add couplings for ground state to each excited state
        self.couplings_table.setRowCount(0)

        for i, state in enumerate(states[1:], start=2):  # Skip ground state
            row = self.couplings_table.rowCount()
            self.couplings_table.setRowCount(row + 1)

            self.couplings_table.setItem(row, 0, QTableWidgetItem("1"))   # From ground state
            self.couplings_table.setItem(row, 1, QTableWidgetItem(str(i)))  # To excited state
            self.couplings_table.setItem(row, 2, QTableWidgetItem("2"))   # Default L=2
            self.couplings_table.setItem(row, 3, QTableWidgetItem("0.25"))  # Default beta
            self.couplings_table.setItem(row, 4, QTableWidgetItem("0"))   # Deform length
            self.couplings_table.setItem(row, 5, QTableWidgetItem("1"))   # POT number

        self.run_validation()

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        couplings = []
        for row in range(self.couplings_table.rowCount()):
            try:
                coupling = {
                    'from_state': int(self.couplings_table.item(row, 0).text()),
                    'to_state': int(self.couplings_table.item(row, 1).text()),
                    'multipolarity': int(self.couplings_table.item(row, 2).text()),
                    'beta': float(self.couplings_table.item(row, 3).text()),
                    'deform_length': float(self.couplings_table.item(row, 4).text()),
                    'pot_number': int(self.couplings_table.item(row, 5).text()),
                }
                couplings.append(coupling)
            except (ValueError, AttributeError):
                pass

        return StepData(
            values={
                'coupling_kind': self.coupling_kind.currentData(),
                'couplings': couplings
            },
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data from external source"""
        if 'coupling_kind' in data:
            index = self.coupling_kind.findData(data['coupling_kind'])
            if index >= 0:
                self.coupling_kind.setCurrentIndex(index)

        if 'couplings' in data:
            couplings = data['couplings']
            self.couplings_table.setRowCount(len(couplings))

            for row, coupling in enumerate(couplings):
                self.couplings_table.setItem(row, 0, QTableWidgetItem(str(coupling.get('from_state', 1))))
                self.couplings_table.setItem(row, 1, QTableWidgetItem(str(coupling.get('to_state', 2))))
                self.couplings_table.setItem(row, 2, QTableWidgetItem(str(coupling.get('multipolarity', 2))))
                self.couplings_table.setItem(row, 3, QTableWidgetItem(str(coupling.get('beta', 0.25))))
                self.couplings_table.setItem(row, 4, QTableWidgetItem(str(coupling.get('deform_length', 0))))
                self.couplings_table.setItem(row, 5, QTableWidgetItem(str(coupling.get('pot_number', 1))))

    def validate(self):
        """Validate current step"""
        messages = []

        if self.couplings_table.rowCount() < 1:
            messages.append(ValidationMessage(
                level='warning',
                message='No couplings defined - calculation will be elastic',
                suggestion='Add at least one coupling for inelastic scattering'
            ))
            return messages

        # Check coupling validity
        n_states = len(self.states_data) if self.states_data else 10

        for row in range(self.couplings_table.rowCount()):
            try:
                from_state = int(self.couplings_table.item(row, 0).text())
                to_state = int(self.couplings_table.item(row, 1).text())
                multipolarity = int(self.couplings_table.item(row, 2).text())
                beta = float(self.couplings_table.item(row, 3).text())

                if from_state < 1 or from_state > n_states:
                    messages.append(ValidationMessage(
                        level='error',
                        message=f'Row {row+1}: Invalid from_state (must be 1-{n_states})'
                    ))

                if to_state < 1 or to_state > n_states:
                    messages.append(ValidationMessage(
                        level='error',
                        message=f'Row {row+1}: Invalid to_state (must be 1-{n_states})'
                    ))

                if from_state == to_state:
                    messages.append(ValidationMessage(
                        level='error',
                        message=f'Row {row+1}: Cannot couple a state to itself'
                    ))

                if multipolarity < 0 or multipolarity > 10:
                    messages.append(ValidationMessage(
                        level='warning',
                        message=f'Row {row+1}: Unusual multipolarity L={multipolarity}'
                    ))

                if abs(beta) > 1.0:
                    messages.append(ValidationMessage(
                        level='warning',
                        message=f'Row {row+1}: Large deformation β={beta}',
                        suggestion='Typical values are |β| < 0.5'
                    ))

            except (ValueError, AttributeError):
                messages.append(ValidationMessage(
                    level='error',
                    message=f'Row {row+1}: Invalid values'
                ))

        # Success if no errors
        if not any(m.level == 'error' for m in messages):
            n_couplings = self.couplings_table.rowCount()
            messages.append(ValidationMessage(
                level='success',
                message=f'{n_couplings} coupling(s) configured'
            ))

        return messages
