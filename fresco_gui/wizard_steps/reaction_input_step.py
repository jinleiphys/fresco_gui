"""
Reaction Input Step for FRESCO Studio Wizard

First step: Enter reaction equation and beam energy.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QFrame, QGridLayout, QPushButton, QGroupBox
)
from PySide6.QtCore import Signal, Qt

from wizard_step_widget import WizardStepWidget, ValidationMessage
from reaction_parser import ReactionParser, ReactionType, ParsedReaction


class ReactionInputStep(WizardStepWidget):
    """
    Step 1: Reaction equation and energy input.
    """

    reaction_parsed = Signal(object)  # Emits ParsedReaction

    def __init__(self):
        super().__init__(
            step_id="reaction_input",
            title="Reaction Setup",
            description=""
        )
        self.parser = ReactionParser()
        self.parsed_reaction: ParsedReaction = None

    def init_step_ui(self):
        """Initialize the step UI"""
        # Main input card
        input_card = QWidget()
        input_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setSpacing(16)

        # Title
        title = QLabel("Enter Reaction")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2937;")
        input_layout.addWidget(title)

        # Equation input
        equation_row = QHBoxLayout()
        equation_row.setSpacing(12)

        eq_label = QLabel("Equation:")
        eq_label.setStyleSheet("font-weight: 500; color: #374151; min-width: 70px;")
        equation_row.addWidget(eq_label)

        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("e.g., p+ni78, alpha+c12*, c12(d,p)c13")
        self.equation_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                font-size: 15px;
                font-family: 'Monaco', 'Consolas', monospace;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        self.equation_input.textChanged.connect(self._on_equation_changed)
        equation_row.addWidget(self.equation_input, 1)

        input_layout.addLayout(equation_row)

        # Energy input
        energy_row = QHBoxLayout()
        energy_row.setSpacing(12)

        energy_label = QLabel("Energy:")
        energy_label.setStyleSheet("font-weight: 500; color: #374151; min-width: 70px;")
        energy_row.addWidget(energy_label)

        self.energy_input = QDoubleSpinBox()
        self.energy_input.setRange(0.01, 10000.0)
        self.energy_input.setValue(10.0)
        self.energy_input.setSuffix(" MeV")
        self.energy_input.setDecimals(2)
        self.energy_input.setSingleStep(1.0)
        self.energy_input.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 14px;
                font-size: 15px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                min-width: 140px;
            }
            QDoubleSpinBox:focus {
                border-color: #2563eb;
            }
        """)
        self.energy_input.valueChanged.connect(self.emit_data_changed)
        energy_row.addWidget(self.energy_input)

        energy_row.addStretch()
        input_layout.addLayout(energy_row)

        # Status message
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("padding: 8px 0;")
        input_layout.addWidget(self.status_label)

        self.content_layout.addWidget(input_card)

        # Reaction info card (hidden until parsed)
        self.info_card = QWidget()
        self.info_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        info_layout = QVBoxLayout(self.info_card)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(8)

        info_title = QLabel("Detected Reaction")
        info_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #374151;")
        info_layout.addWidget(info_title)

        self.info_grid = QGridLayout()
        self.info_grid.setSpacing(8)
        self.info_grid.setColumnMinimumWidth(0, 80)

        self._add_info_row(0, "Type:", "-")
        self._add_info_row(1, "Projectile:", "-")
        self._add_info_row(2, "Target:", "-")
        self._add_info_row(3, "Ejectile:", "-")
        self._add_info_row(4, "Residual:", "-")
        self._add_info_row(5, "Q-value:", "-")

        info_layout.addLayout(self.info_grid)

        self.info_card.hide()
        self.content_layout.addWidget(self.info_card)

        # Quick examples
        examples_card = QWidget()
        examples_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        examples_layout = QVBoxLayout(examples_card)
        examples_layout.setContentsMargins(20, 16, 20, 16)
        examples_layout.setSpacing(12)

        examples_title = QLabel("Quick Examples")
        examples_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #374151;")
        examples_layout.addWidget(examples_title)

        examples = [
            ("p + 58Ni (elastic)", "p+ni58", 10.0),
            ("alpha + 12C* (inelastic)", "alpha+c12*", 30.0),
            ("12C(d,p)13C (transfer)", "c12(d,p)c13", 30.0),
            ("40Ca(d,p)41Ca", "ca40(d,p)ca41", 56.0),
        ]

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for label, equation, energy in examples:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f3f4f6;
                    border: 1px solid #e5e7eb;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 12px;
                    color: #374151;
                }
                QPushButton:hover {
                    background-color: #e5e7eb;
                }
            """)
            btn.clicked.connect(lambda _, eq=equation, en=energy: self._use_example(eq, en))
            btn_row.addWidget(btn)
        btn_row.addStretch()

        examples_layout.addLayout(btn_row)

        # Format help
        help_text = QLabel(
            "Formats: <b>proj+target</b> for elastic/inelastic (use * for excited state), "
            "<b>target(proj,eject)resid</b> for transfer"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #6b7280; font-size: 12px;")
        examples_layout.addWidget(help_text)

        self.content_layout.addWidget(examples_card)

        self.content_layout.addStretch()

    def _add_info_row(self, row: int, label: str, value: str):
        """Add a row to the info grid"""
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #6b7280; font-size: 13px;")
        self.info_grid.addWidget(lbl, row, 0)

        val = QLabel(value)
        val.setStyleSheet("color: #1f2937; font-size: 13px;")
        val.setObjectName(f"info_val_{row}")
        self.info_grid.addWidget(val, row, 1)

    def _update_info_row(self, row: int, value: str):
        """Update a row in the info grid"""
        val = self.info_card.findChild(QLabel, f"info_val_{row}")
        if val:
            val.setText(value)

    def _on_equation_changed(self, text: str):
        """Handle equation text change"""
        if not text.strip():
            self.status_label.setText("")
            self.info_card.hide()
            self.parsed_reaction = None
            self.emit_data_changed()
            return

        result = self.parser.parse(text)
        self.parsed_reaction = result

        if result.parse_success:
            self._show_success(result)
        else:
            self._show_error(result)

        self.emit_data_changed()

    def _show_success(self, result: ParsedReaction):
        """Display successful parse result"""
        type_name = {
            ReactionType.ELASTIC: "Elastic Scattering",
            ReactionType.INELASTIC: "Inelastic Scattering",
            ReactionType.TRANSFER: "Transfer Reaction"
        }.get(result.reaction_type, "Unknown")

        self.status_label.setText(f"✓ {type_name}")
        self.status_label.setStyleSheet("""
            padding: 8px 12px;
            background-color: #d1fae5;
            color: #065f46;
            border-radius: 4px;
            font-weight: 500;
        """)

        # Update info card
        self.info_card.show()
        self._update_info_row(0, type_name)

        if result.projectile:
            self._update_info_row(1, f"{result.projectile.name} (Z={result.projectile.atomic_number}, A={result.projectile.mass_number})")
        if result.target:
            suffix = " *" if result.is_target_excited else ""
            self._update_info_row(2, f"{result.target.name}{suffix} (Z={result.target.atomic_number}, A={result.target.mass_number})")

        # Show/hide transfer-specific rows
        is_transfer = result.reaction_type == ReactionType.TRANSFER
        for row in [3, 4]:
            label = self.info_grid.itemAtPosition(row, 0).widget()
            value = self.info_grid.itemAtPosition(row, 1).widget()
            if label and value:
                label.setVisible(is_transfer)
                value.setVisible(is_transfer)

        if is_transfer:
            if result.ejectile:
                self._update_info_row(3, f"{result.ejectile.name} (Z={result.ejectile.atomic_number}, A={result.ejectile.mass_number})")
            if result.residual:
                self._update_info_row(4, f"{result.residual.name} (Z={result.residual.atomic_number}, A={result.residual.mass_number})")

        if result.q_value is not None:
            self._update_info_row(5, f"{result.q_value:.3f} MeV")
        else:
            self._update_info_row(5, "-")

        self.reaction_parsed.emit(result)

    def _show_error(self, result: ParsedReaction):
        """Display parse error"""
        error_msg = "; ".join(result.parse_errors) if result.parse_errors else "Invalid format"
        self.status_label.setText(f"✗ {error_msg}")
        self.status_label.setStyleSheet("""
            padding: 8px 12px;
            background-color: #fee2e2;
            color: #991b1b;
            border-radius: 4px;
        """)
        self.info_card.hide()

    def _use_example(self, equation: str, energy: float):
        """Load an example reaction"""
        self.equation_input.setText(equation)
        self.energy_input.setValue(energy)

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        data = {
            'equation': self.equation_input.text().strip(),
            'energy': self.energy_input.value(),
            'parsed_reaction': self.parsed_reaction,
        }

        if self.parsed_reaction and self.parsed_reaction.parse_success:
            data['reaction_type'] = self.parsed_reaction.reaction_type
            data['projectile'] = self.parsed_reaction.projectile
            data['target'] = self.parsed_reaction.target
            data['ejectile'] = self.parsed_reaction.ejectile
            data['residual'] = self.parsed_reaction.residual
            data['q_value'] = self.parsed_reaction.q_value
            data['is_target_excited'] = self.parsed_reaction.is_target_excited

        return StepData(
            values=data,
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data from external source"""
        if 'equation' in data:
            self.equation_input.setText(data['equation'])
        if 'energy' in data:
            self.energy_input.setValue(data['energy'])

    def reset(self):
        """Reset the step to initial state"""
        self.equation_input.clear()
        self.energy_input.setValue(10.0)
        self.parsed_reaction = None
        self.status_label.setText("")
        self.status_label.setStyleSheet("padding: 8px 0;")
        self.info_card.hide()
        self._is_completed = False
        self._validation_messages = []

    def validate(self):
        """Validate current step"""
        messages = []

        equation = self.equation_input.text().strip()
        if not equation:
            messages.append(ValidationMessage(
                level='error',
                message='Please enter a reaction equation'
            ))
            return messages

        if not self.parsed_reaction or not self.parsed_reaction.parse_success:
            for error in (self.parsed_reaction.parse_errors if self.parsed_reaction else ['Invalid format']):
                messages.append(ValidationMessage(level='error', message=error))
            return messages

        if self.parsed_reaction.parse_warnings:
            for warning in self.parsed_reaction.parse_warnings:
                messages.append(ValidationMessage(level='warning', message=warning))

        energy = self.energy_input.value()
        if energy <= 0:
            messages.append(ValidationMessage(level='error', message='Energy must be positive'))

        return messages
