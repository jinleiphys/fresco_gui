"""
Wizard Step Base Widget for FRESCO Studio

Base class for all wizard step widgets, providing common functionality
for navigation, validation, and state management.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGroupBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationMessage:
    """Validation message with severity level"""
    level: str  # 'error', 'warning', 'info', 'success'
    message: str
    parameter: str = ""  # Optional parameter name
    suggestion: str = ""  # Optional suggestion


@dataclass
class StepData:
    """Data container for a wizard step"""
    values: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = False
    validation_messages: List[ValidationMessage] = field(default_factory=list)


class WizardStepWidget(QWidget):
    """
    Base class for wizard step widgets.

    Provides:
    - Standard layout with title, description, and content area
    - Validation framework
    - State management (get/set data)
    - Signal for data changes
    """

    # Signals
    data_changed = Signal()  # Emitted when step data changes
    validation_changed = Signal(list)  # Emitted with list of ValidationMessage
    step_completed = Signal(bool)  # Emitted when step completion status changes

    def __init__(self, step_id: str, title: str, description: str = ""):
        super().__init__()
        self.step_id = step_id
        self.title = title
        self.description = description
        self._is_completed = False
        self._validation_messages: List[ValidationMessage] = []

        self._init_base_ui()

    def _init_base_ui(self):
        """Initialize the base UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # Content area (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll, 1)

        # Initialize step-specific content
        self.init_step_ui()

    def init_step_ui(self):
        """
        Initialize step-specific UI elements.
        Override in subclasses to add custom widgets.
        """
        pass

    def get_data(self) -> StepData:
        """
        Get current step data.
        Override in subclasses to return actual data.

        Returns:
            StepData object with current values and validation state
        """
        return StepData(
            values={},
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: Dict[str, Any]):
        """
        Set step data from external source.
        Override in subclasses to populate widgets.

        Args:
            data: Dictionary of values to set
        """
        pass

    def validate(self) -> List[ValidationMessage]:
        """
        Validate current step data.
        Override in subclasses to implement validation logic.

        Returns:
            List of ValidationMessage objects
        """
        return []

    def run_validation(self):
        """Run validation and emit signals"""
        self._validation_messages = self.validate()
        self.validation_changed.emit(self._validation_messages)

        # Update completion status
        has_errors = any(m.level == 'error' for m in self._validation_messages)
        new_completed = not has_errors

        if new_completed != self._is_completed:
            self._is_completed = new_completed
            self.step_completed.emit(self._is_completed)

    def is_complete(self) -> bool:
        """Check if step is complete (no errors)"""
        return self._is_completed

    def get_validation_messages(self) -> List[ValidationMessage]:
        """Get current validation messages"""
        return self._validation_messages

    def on_entering_step(self):
        """
        Called when user enters this step.
        Override to perform actions when step becomes active.
        """
        self.run_validation()

    def on_leaving_step(self) -> bool:
        """
        Called when user tries to leave this step.
        Override to perform validation or cleanup.

        Returns:
            True if OK to leave, False to prevent navigation
        """
        self.run_validation()
        return True  # Allow leaving even with warnings

    def create_group_box(self, title: str, collapsible: bool = False) -> QGroupBox:
        """
        Create a styled group box for organizing content.

        Args:
            title: Group box title
            collapsible: Whether the group can be collapsed

        Returns:
            Configured QGroupBox
        """
        group = QGroupBox(title)
        group.setCheckable(collapsible)
        if collapsible:
            group.setChecked(True)

        group.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 8px;
                padding: 12px;
                padding-top: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 6px;
                background-color: white;
                color: #374151;
            }
        """)

        return group

    def create_info_label(self, text: str) -> QLabel:
        """Create an informational label with standard styling"""
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("""
            color: #6b7280;
            font-size: 12px;
            padding: 4px 0;
        """)
        return label

    def create_help_button(self, tooltip: str) -> QPushButton:
        """Create a help button with tooltip"""
        btn = QPushButton("?")
        btn.setFixedSize(20, 20)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #e5e7eb;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                color: #6b7280;
            }
            QPushButton:hover {
                background-color: #d1d5db;
                color: #374151;
            }
        """)
        return btn

    def emit_data_changed(self):
        """Emit data changed signal and re-validate"""
        self.data_changed.emit()
        self.run_validation()


class WizardStepContainer(QWidget):
    """
    Simple container that just wraps a wizard step.
    Validation is shown inline within the step.
    """

    def __init__(self, step: WizardStepWidget):
        super().__init__()
        self.step = step

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.step)
