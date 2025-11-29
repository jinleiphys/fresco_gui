"""
Wizard Navigator Widget for FRESCO Studio

Provides step-by-step navigation UI with progress indicator,
step status display, and navigation buttons.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QStackedWidget
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class StepInfo:
    """Information about a wizard step"""
    id: str
    title: str
    short_title: str  # For progress indicator
    is_complete: bool = False
    is_enabled: bool = True


class ProgressIndicator(QWidget):
    """
    Compact horizontal progress indicator.
    Shows step numbers with connecting lines.
    """

    step_clicked = Signal(int)

    def __init__(self):
        super().__init__()
        self.steps: List[StepInfo] = []
        self.current_step = 0
        self._step_labels: List[QLabel] = []

        self.setFixedHeight(50)
        self._init_ui()

    def _init_ui(self):
        """Initialize the progress indicator UI"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 8, 0, 8)
        self.main_layout.setSpacing(0)

    def set_steps(self, steps: List[StepInfo]):
        """Set the steps to display"""
        self.steps = steps
        self._rebuild_ui()

    def set_current_step(self, index: int):
        """Set the currently active step"""
        self.current_step = index
        self._update_styles()

    def set_step_complete(self, index: int, complete: bool):
        """Mark a step as complete or incomplete"""
        if 0 <= index < len(self.steps):
            self.steps[index].is_complete = complete
            self._update_styles()

    def _rebuild_ui(self):
        """Rebuild the progress indicator"""
        # Clear existing widgets
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._step_labels = []

        if not self.steps:
            return

        self.main_layout.addStretch(1)

        for i, step in enumerate(self.steps):
            # Create step indicator
            step_widget = self._create_step_widget(i, step)
            self._step_labels.append(step_widget)
            self.main_layout.addWidget(step_widget)

            # Add connector line (except after last step)
            if i < len(self.steps) - 1:
                connector = QFrame()
                connector.setFixedSize(30, 2)
                connector.setStyleSheet("background-color: #d1d5db;")
                self.main_layout.addWidget(connector, 0, Qt.AlignVCenter)

        self.main_layout.addStretch(1)
        self._update_styles()

    def _create_step_widget(self, index: int, step: StepInfo) -> QLabel:
        """Create a single step indicator"""
        label = QLabel(str(index + 1))
        label.setFixedSize(28, 28)
        label.setAlignment(Qt.AlignCenter)
        label.setCursor(Qt.PointingHandCursor)
        label.setToolTip(step.title)
        label.mousePressEvent = lambda e, idx=index: self._on_step_clicked(idx)
        return label

    def _on_step_clicked(self, index: int):
        """Handle step indicator click"""
        if 0 <= index < len(self.steps):
            if index <= self.current_step or self.steps[index].is_complete:
                self.step_clicked.emit(index)

    def _update_styles(self):
        """Update visual styles based on current state"""
        for i, label in enumerate(self._step_labels):
            if i == self.current_step:
                # Current step - blue filled
                label.setStyleSheet("""
                    background-color: #2563eb;
                    color: white;
                    border-radius: 14px;
                    font-weight: 600;
                    font-size: 13px;
                """)
            elif self.steps[i].is_complete:
                # Completed step - green with check
                label.setStyleSheet("""
                    background-color: #10b981;
                    color: white;
                    border-radius: 14px;
                    font-weight: 600;
                    font-size: 13px;
                """)
                label.setText("✓")
            else:
                # Future step - gray outline
                label.setStyleSheet("""
                    background-color: white;
                    color: #9ca3af;
                    border: 2px solid #d1d5db;
                    border-radius: 14px;
                    font-weight: 500;
                    font-size: 13px;
                """)
                label.setText(str(i + 1))


class WizardNavigator(QWidget):
    """
    Complete wizard navigation widget.

    Layout:
    +----------------------------------------------------------+
    |  Step indicator: (1)---(2)---(3)---(4)                   |
    |  Step title label                                         |
    +----------------------------------------------------------+
    |                                                          |
    |               [Step Content Here]                        |
    |                                                          |
    +----------------------------------------------------------+
    |  [< Previous]                   [Next >] [Generate]      |
    +----------------------------------------------------------+
    """

    # Signals
    step_changed = Signal(int)
    generate_requested = Signal()
    previous_clicked = Signal()
    next_clicked = Signal()
    reset_requested = Signal()

    def __init__(self):
        super().__init__()
        self.steps: List[StepInfo] = []
        self.current_step_index = 0

        self._init_ui()

    def _init_ui(self):
        """Initialize the navigator UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top section: Progress indicator
        header = QWidget()
        header.setStyleSheet("background-color: #f9fafb;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(4)

        self.progress_indicator = ProgressIndicator()
        self.progress_indicator.step_clicked.connect(self._on_step_clicked)
        header_layout.addWidget(self.progress_indicator)

        # Step title
        self.step_info_label = QLabel("Step 1 of 1")
        self.step_info_label.setAlignment(Qt.AlignCenter)
        self.step_info_label.setStyleSheet("""
            color: #6b7280;
            font-size: 12px;
            padding: 2px;
        """)
        header_layout.addWidget(self.step_info_label)

        main_layout.addWidget(header)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #e5e7eb;")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)

        # Content area (stacked widget for steps)
        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_stack.setStyleSheet("background-color: #f3f4f6;")
        main_layout.addWidget(self.content_stack, 1)

        # Bottom section: Navigation buttons
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background-color: white; border-top: 1px solid #e5e7eb;")
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(16, 12, 16, 12)

        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setObjectName("wizardResetBtn")
        self.reset_btn.clicked.connect(self._on_reset)
        self.reset_btn.setStyleSheet("""
            QPushButton#wizardResetBtn {
                background-color: white;
                border: 1px solid #fca5a5;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                color: #dc2626;
                font-weight: 500;
            }
            QPushButton#wizardResetBtn:hover {
                background-color: #fef2f2;
                border-color: #f87171;
            }
        """)
        nav_layout.addWidget(self.reset_btn)

        nav_layout.addSpacing(8)

        # Previous button
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setObjectName("wizardPrevBtn")
        self.prev_btn.clicked.connect(self._on_previous)
        self.prev_btn.setStyleSheet("""
            QPushButton#wizardPrevBtn {
                background-color: white;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                color: #374151;
                font-weight: 500;
            }
            QPushButton#wizardPrevBtn:hover {
                background-color: #f3f4f6;
                border-color: #9ca3af;
            }
            QPushButton#wizardPrevBtn:disabled {
                background-color: #f9fafb;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
        """)
        nav_layout.addWidget(self.prev_btn)

        nav_layout.addStretch()

        # Next button
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("wizardNextBtn")
        self.next_btn.clicked.connect(self._on_next)
        self.next_btn.setStyleSheet("""
            QPushButton#wizardNextBtn {
                background-color: #2563eb;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                color: white;
                font-weight: 500;
            }
            QPushButton#wizardNextBtn:hover {
                background-color: #1d4ed8;
            }
            QPushButton#wizardNextBtn:disabled {
                background-color: #93c5fd;
            }
        """)
        nav_layout.addWidget(self.next_btn)

        # Generate button (shown on last step)
        self.generate_btn = QPushButton("Generate Input")
        self.generate_btn.setObjectName("wizardGenerateBtn")
        self.generate_btn.clicked.connect(self._on_generate)
        self.generate_btn.setStyleSheet("""
            QPushButton#wizardGenerateBtn {
                background-color: #059669;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-size: 13px;
                color: white;
                font-weight: 500;
            }
            QPushButton#wizardGenerateBtn:hover {
                background-color: #047857;
            }
            QPushButton#wizardGenerateBtn:disabled {
                background-color: #6ee7b7;
            }
        """)
        self.generate_btn.hide()
        nav_layout.addWidget(self.generate_btn)

        main_layout.addWidget(nav_widget)

    def set_steps(self, steps: List[StepInfo]):
        """Set the wizard steps"""
        self.steps = steps
        self.progress_indicator.set_steps(steps)
        self._update_ui()

    def add_step_widget(self, widget: QWidget):
        """Add a widget to the content stack"""
        self.content_stack.addWidget(widget)

    def go_to_step(self, index: int):
        """Navigate to a specific step"""
        if 0 <= index < len(self.steps):
            self.current_step_index = index
            self.content_stack.setCurrentIndex(index)
            self.progress_indicator.set_current_step(index)
            self._update_ui()
            self.step_changed.emit(index)

    def next_step(self):
        """Go to the next step"""
        if self.current_step_index < len(self.steps) - 1:
            # Mark current step as complete
            self.steps[self.current_step_index].is_complete = True
            self.progress_indicator.set_step_complete(self.current_step_index, True)
            self.go_to_step(self.current_step_index + 1)

    def previous_step(self):
        """Go to the previous step"""
        if self.current_step_index > 0:
            self.go_to_step(self.current_step_index - 1)

    def set_step_complete(self, index: int, complete: bool):
        """Mark a step as complete or incomplete"""
        if 0 <= index < len(self.steps):
            self.steps[index].is_complete = complete
            self.progress_indicator.set_step_complete(index, complete)

    def _update_ui(self):
        """Update UI state based on current step"""
        total = len(self.steps)
        current = self.current_step_index

        # Update step info label
        if total > 0 and current < total:
            step_title = self.steps[current].title
            self.step_info_label.setText(f"Step {current + 1} of {total}: {step_title}")

        # Update button states
        self.prev_btn.setEnabled(current > 0)

        is_last_step = current >= total - 1
        self.next_btn.setVisible(not is_last_step)
        self.generate_btn.setVisible(is_last_step)

    def _on_step_clicked(self, index: int):
        """Handle progress indicator step click"""
        self.go_to_step(index)

    def _on_previous(self):
        """Handle previous button click"""
        self.previous_clicked.emit()
        self.previous_step()

    def _on_next(self):
        """Handle next button click"""
        self.next_clicked.emit()
        self.next_step()

    def _on_generate(self):
        """Handle generate button click"""
        self.generate_requested.emit()

    def _on_reset(self):
        """Handle reset button click"""
        self.reset_requested.emit()

    def reset_wizard(self):
        """Reset the wizard to initial state"""
        # Reset all steps to incomplete
        for i, step in enumerate(self.steps):
            step.is_complete = False

        # Go back to first step
        self.current_step_index = 0
        self.content_stack.setCurrentIndex(0)
        self.progress_indicator.set_current_step(0)
        self._update_ui()

        # Rebuild progress indicator to show all steps as incomplete
        self.progress_indicator._update_styles()
