"""
Advanced FRESCO Parameters Widget
Collapsible widget for managing advanced FRESCO namelist parameters
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QGroupBox, QScrollArea, QDoubleSpinBox, QSpinBox,
    QLineEdit, QComboBox, QCheckBox, QToolButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from fresco_namelist import FRESCO_NAMELIST


class AdvancedParametersWidget(QWidget):
    """
    Collapsible widget for advanced FRESCO parameters
    Can be used in any calculation type form
    """

    parameters_changed = Signal()  # Emitted when any parameter changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parameter_widgets = {}  # Store widgets for each parameter
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create collapsible group box
        self.group_box = QGroupBox("⚙️ Advanced FRESCO Parameters")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Collapsed by default
        self.group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QGroupBox::indicator {
                width: 13px;
                height: 13px;
            }
            QGroupBox::indicator:unchecked {
                image: url(none);
            }
            QGroupBox::indicator:checked {
                image: url(none);
            }
        """)

        # Content widget (hidden when collapsed)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Info label
        info_label = QLabel(
            "These parameters have sensible defaults. Only modify if you need specific behavior.\n"
            "Hover over parameter names for detailed descriptions."
        )
        info_label.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        # Create tabbed sections for different parameter categories
        from PySide6.QtWidgets import QTabWidget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Create tabs for each category
        for cat_key, cat_info in FRESCO_NAMELIST.categories.items():
            params = FRESCO_NAMELIST.get_parameters_by_category(cat_key)
            if params:
                tab_widget = self._create_category_widget(params)
                self.tabs.addTab(tab_widget, f"{cat_info['icon']} {cat_info['title']}")

        content_layout.addWidget(self.tabs)

        # Reset button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()

        reset_btn = QPushButton("Reset All to Defaults")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        reset_layout.addWidget(reset_btn)

        content_layout.addLayout(reset_layout)

        # Add content to group box
        group_layout = QVBoxLayout()
        group_layout.addWidget(content_widget)
        self.group_box.setLayout(group_layout)

        # Connect collapse/expand
        self.group_box.toggled.connect(lambda checked: content_widget.setVisible(checked))
        content_widget.setVisible(False)  # Start collapsed

        layout.addWidget(self.group_box)

    def _create_category_widget(self, parameters):
        """Create widget for a parameter category"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        widget = QWidget()
        form_layout = QFormLayout(widget)
        form_layout.setSpacing(10)

        for param in parameters:
            # Skip basic parameters (they're in the main form)
            if param.name in FRESCO_NAMELIST.BASIC_PARAMETERS:
                continue

            # Create label with tooltip
            label = QLabel(param.label + ":")
            label.setToolTip(param.tooltip)
            label.setStyleSheet("font-weight: normal;")

            # Create appropriate widget based on parameter type
            if param.param_type == "number":
                if param.step and param.step < 1:  # Float
                    widget_input = QDoubleSpinBox()
                    widget_input.setDecimals(len(str(param.step).split('.')[-1]))
                else:  # Int
                    widget_input = QSpinBox()

                if param.minimum is not None:
                    widget_input.setMinimum(param.minimum)
                else:
                    widget_input.setMinimum(-999999)

                if param.maximum is not None:
                    widget_input.setMaximum(param.maximum)
                else:
                    widget_input.setMaximum(999999)

                if param.step:
                    widget_input.setSingleStep(param.step)

                if param.default is not None:
                    widget_input.setValue(param.default)
                else:
                    widget_input.setSpecialValueText("(default)")

                widget_input.setToolTip(param.tooltip)
                widget_input.valueChanged.connect(self.parameters_changed.emit)

            elif param.param_type == "text":
                widget_input = QLineEdit()
                if param.default:
                    widget_input.setText(str(param.default))
                widget_input.setPlaceholderText("(optional)")
                widget_input.setToolTip(param.tooltip)
                widget_input.textChanged.connect(self.parameters_changed.emit)

            elif param.param_type == "select":
                widget_input = QComboBox()
                for value, text in param.options:
                    widget_input.addItem(text, value)
                # Set default
                if param.default is not None:
                    for i in range(widget_input.count()):
                        if widget_input.itemData(i) == param.default:
                            widget_input.setCurrentIndex(i)
                            break
                widget_input.setToolTip(param.tooltip)
                widget_input.currentIndexChanged.connect(self.parameters_changed.emit)

            else:  # checkbox
                widget_input = QCheckBox()
                if param.default:
                    widget_input.setChecked(bool(param.default))
                widget_input.setToolTip(param.tooltip)
                widget_input.stateChanged.connect(self.parameters_changed.emit)

            # Store widget for later retrieval
            self.parameter_widgets[param.name] = widget_input

            form_layout.addRow(label, widget_input)

        scroll.setWidget(widget)
        return scroll

    def get_parameter_values(self):
        """Get all parameter values as a dictionary"""
        values = {}

        for param_name, widget in self.parameter_widgets.items():
            param = FRESCO_NAMELIST.get_parameter(param_name)
            if not param:
                continue

            # Get value based on widget type
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
                # Skip if equals default
                if param.default is not None and value == param.default:
                    continue
                values[param_name] = value

            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    values[param_name] = text

            elif isinstance(widget, QComboBox):
                value = widget.currentData()
                # Skip if equals default or None
                if value is None or (param.default is not None and value == param.default):
                    continue
                values[param_name] = value

            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
                if param.default is not None and value == param.default:
                    continue
                values[param_name] = value

        return values

    def set_parameter_value(self, name: str, value):
        """Set a parameter value"""
        if name not in self.parameter_widgets:
            return

        widget = self.parameter_widgets[name]

        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setValue(value)
        elif isinstance(widget, QLineEdit):
            widget.setText(str(value))
        elif isinstance(widget, QComboBox):
            for i in range(widget.count()):
                if widget.itemData(i) == value:
                    widget.setCurrentIndex(i)
                    break
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))

    def reset_to_defaults(self):
        """Reset all parameters to their defaults"""
        for param_name, widget in self.parameter_widgets.items():
            param = FRESCO_NAMELIST.get_parameter(param_name)
            if not param or param.default is None:
                continue

            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(param.default)
            elif isinstance(widget, QLineEdit):
                widget.setText(str(param.default))
            elif isinstance(widget, QComboBox):
                for i in range(widget.count()):
                    if widget.itemData(i) == param.default:
                        widget.setCurrentIndex(i)
                        break
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(param.default))

        self.parameters_changed.emit()

    def generate_namelist_text(self, basic_params: dict = None):
        """
        Generate &FRESCO namelist text
        Combines basic parameters with advanced parameters
        """
        # Start with basic parameters
        all_params = basic_params.copy() if basic_params else {}

        # Add advanced parameters
        advanced_params = self.get_parameter_values()
        all_params.update(advanced_params)

        # Use namelist manager to generate text
        return FRESCO_NAMELIST.generate_namelist_text(all_params)
