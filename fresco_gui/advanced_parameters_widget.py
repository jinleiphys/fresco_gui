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
    Supports dynamic parameter categorization via ParameterManager
    """

    parameters_changed = Signal()  # Emitted when any parameter changes

    def __init__(self, parameter_manager=None, parent=None):
        """
        Initialize the widget

        Args:
            parameter_manager: ParameterManager instance for dynamic categorization (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        self.parameter_manager = parameter_manager
        self.parameter_widgets = {}  # Store widgets for each parameter
        self.content_widget = None  # Store reference to content widget for refreshing
        self.category_buttons = []  # Track category buttons and content widgets
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create collapsible group box with modern design
        self.group_box = QGroupBox("Advanced Parameters")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Collapsed by default

        # Content widget (hidden when collapsed)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)

        # Info label
        info_label = QLabel(
            "💡 These parameters have sensible defaults. Hover over names for descriptions."
        )
        info_label.setObjectName("infoBox")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        # Count label showing number of advanced parameters
        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        content_layout.addWidget(self.count_label)

        # Create scroll area for all categories (no tabs)
        self.categories_scroll = QScrollArea()
        self.categories_scroll.setWidgetResizable(True)
        self.categories_scroll.setFrameShape(QScrollArea.NoFrame)

        # Container for all categories
        self.categories_container = QWidget()
        self.categories_layout = None  # Will be set in _rebuild_categories

        # Build categories based on parameter manager
        self._rebuild_categories()

        self.categories_scroll.setWidget(self.categories_container)

        # Create a horizontal layout: category list on left, content on right
        categories_and_content = QHBoxLayout()
        categories_and_content.addWidget(self.categories_scroll, 1)  # Category buttons

        # Content display area (shared by all categories)
        self.content_display = QWidget()
        self.content_display_layout = QVBoxLayout(self.content_display)
        self.content_display_layout.setContentsMargins(8, 8, 8, 8)

        categories_and_content.addWidget(self.content_display, 2)  # Content area (larger)

        content_layout.addLayout(categories_and_content)

        # Reset button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("resetButton")
        reset_btn.setProperty("styleClass", "secondary")
        reset_btn.clicked.connect(self.reset_to_defaults)
        reset_layout.addWidget(reset_btn)

        content_layout.addLayout(reset_layout)

        # Add content to group box
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.content_widget)
        self.group_box.setLayout(group_layout)

        # Connect collapse/expand
        self.group_box.toggled.connect(lambda checked: self.content_widget.setVisible(checked))
        self.content_widget.setVisible(False)  # Start collapsed

        layout.addWidget(self.group_box)

    def _rebuild_categories(self):
        """Rebuild categories as vertical list of buttons with shared content area"""
        # Clear existing layout if any
        if self.categories_layout:
            while self.categories_layout.count():
                item = self.categories_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.categories_layout)  # Delete old layout

        # Create new vertical layout for category buttons
        self.categories_layout = QVBoxLayout(self.categories_container)
        self.categories_layout.setSpacing(4)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)

        # Clear parameter widgets dict (will be repopulated)
        self.parameter_widgets.clear()

        # Clear category storage
        self.category_buttons = []  # List of (button, content_widget) tuples
        self.current_category = None

        # Get parameters to display
        if self.parameter_manager:
            # Use dynamic categorization
            params_by_category = self.parameter_manager.get_advanced_parameters_by_category()
            advanced_param_names = set(self.parameter_manager.get_advanced_parameters())

            # Create category button and content for each category
            for cat_key, cat_info in FRESCO_NAMELIST.categories.items():
                if cat_key in params_by_category and params_by_category[cat_key]:
                    # Get parameter objects for these names
                    params = [FRESCO_NAMELIST.get_parameter(name)
                             for name in params_by_category[cat_key]
                             if FRESCO_NAMELIST.get_parameter(name)]
                    if params:
                        # Create category button and content
                        button, content_widget = self._create_category_button_and_content(cat_info, params)
                        self.categories_layout.addWidget(button)
                        self.category_buttons.append((button, content_widget))

            # Add stretch at bottom
            self.categories_layout.addStretch()

            # Update count label
            advanced_count = len(advanced_param_names)
            general_count = len(self.parameter_manager.get_general_parameters())
            total_count = advanced_count + general_count
            self.count_label.setText(
                f"Advanced parameters: {advanced_count} | "
                f"General parameters: {general_count} | "
                f"Total: {total_count}"
            )
        else:
            # Fallback: show all non-basic parameters (old behavior)
            for cat_key, cat_info in FRESCO_NAMELIST.categories.items():
                params = FRESCO_NAMELIST.get_parameters_by_category(cat_key)
                if params:
                    # Filter out BASIC_PARAMETERS
                    filtered_params = [p for p in params
                                     if p.name not in FRESCO_NAMELIST.BASIC_PARAMETERS]
                    if filtered_params:
                        button, content_widget = self._create_category_button_and_content(cat_info, filtered_params)
                        self.categories_layout.addWidget(button)
                        self.category_buttons.append((button, content_widget))

            self.categories_layout.addStretch()
            self.count_label.setText("Using static parameter categorization")

    def refresh(self):
        """Refresh the widget to reflect current parameter categorization"""
        print(f"  [AdvancedParams] refresh() called, rebuilding categories...")
        self._rebuild_categories()
        print(f"  [AdvancedParams] After refresh, have {len(self.parameter_widgets)} widgets:")
        print(f"    {sorted(self.parameter_widgets.keys())}")

    def set_parameter_manager(self, parameter_manager):
        """
        Set or update the parameter manager

        Args:
            parameter_manager: ParameterManager instance
        """
        self.parameter_manager = parameter_manager
        self.refresh()

    def _create_category_button_and_content(self, cat_info, parameters):
        """Create a category button and its content widget"""
        # Create button for category
        button = QPushButton(cat_info['title'])
        button.setCheckable(True)
        button.setObjectName("categoryButton")

        # Create content widget (will be displayed in shared area when button is clicked)
        content_widget = self._create_category_content(cat_info, parameters)

        # Connect button click to show this category's content
        button.clicked.connect(lambda: self._show_category_content(button, content_widget))

        return button, content_widget

    def _create_category_content(self, cat_info, parameters):
        """Create content widget for a category"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        # Create container for parameters
        container = QWidget()
        form_layout = QFormLayout(container)
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Create widgets for each parameter
        for param in parameters:
            label = QLabel(param.label + ":")
            label.setToolTip(param.tooltip)
            label.setObjectName("paramLabel")

            if param.param_type == "number":
                if param.step and param.step < 1:
                    widget_input = QDoubleSpinBox()
                    widget_input.setDecimals(len(str(param.step).split('.')[-1]))
                else:
                    widget_input = QSpinBox()

                widget_input.setMinimum(param.minimum if param.minimum is not None else -999999)
                widget_input.setMaximum(param.maximum if param.maximum is not None else 999999)
                if param.step:
                    widget_input.setSingleStep(param.step)
                if param.default is not None:
                    widget_input.setValue(param.default)
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

            self.parameter_widgets[param.name] = widget_input
            form_layout.addRow(label, widget_input)

        # Set container as scroll widget content
        scroll.setWidget(container)
        return scroll

    def _show_category_content(self, button, content_widget):
        """Show selected category's content in shared display area"""
        # Clear current content from display area
        while self.content_display_layout.count():
            item = self.content_display_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Add new content to display area
        self.content_display_layout.addWidget(content_widget)

        # Update button states (uncheck all others)
        for btn, _ in self.category_buttons:
            if btn != button:
                btn.blockSignals(True)
                btn.setChecked(False)
                btn.blockSignals(False)

        # Ensure this button is checked
        button.blockSignals(True)
        button.setChecked(True)
        button.blockSignals(False)

    def get_parameter_values(self):
        """Get all parameter values as a dictionary (only non-default values for advanced params)"""
        values = {}

        for param_name, widget in self.parameter_widgets.items():
            param = FRESCO_NAMELIST.get_parameter(param_name)
            if not param:
                continue

            # Get value based on widget type
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
                # For advanced params, skip if:
                # 1. Default is None and value is 0 (unmodified numeric widget)
                # 2. Value equals a non-None default
                if param.default is None and value == 0:
                    continue  # Skip unmodified widgets with None default
                if param.default is not None and value == param.default:
                    continue  # Skip values equal to explicit defaults
                values[param_name] = value

            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:  # Only include non-empty text
                    values[param_name] = text

            elif isinstance(widget, QComboBox):
                value = widget.currentData()
                # Skip if None or equals default
                if value is None:
                    continue
                if param.default is not None and value == param.default:
                    continue
                values[param_name] = value

            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
                # Skip if equals default (or False if default is None)
                if param.default is None and not value:
                    continue
                if param.default is not None and value == param.default:
                    continue
                values[param_name] = value

        return values

    def set_parameter_value(self, name: str, value):
        """Set a parameter value"""
        if name not in self.parameter_widgets:
            print(f"    [AdvancedParams] Parameter '{name}' not in widget dict (might be in general params)")
            return

        widget = self.parameter_widgets[name]
        print(f"    [AdvancedParams] Setting {name} = {value} (widget type: {widget.__class__.__name__})")

        try:
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                old_val = widget.value()
                widget.setValue(value)
                widget.update()
                widget.repaint()
                new_val = widget.value()
                print(f"      {name}: {old_val} -> {new_val} (target: {value})")
            elif isinstance(widget, QLineEdit):
                old_val = widget.text()
                widget.setText(str(value))
                widget.update()
                widget.repaint()
                new_val = widget.text()
                print(f"      {name}: '{old_val}' -> '{new_val}' (target: '{value}')")
            elif isinstance(widget, QComboBox):
                old_idx = widget.currentIndex()
                for i in range(widget.count()):
                    if widget.itemData(i) == value:
                        widget.setCurrentIndex(i)
                        widget.update()
                        widget.repaint()
                        break
                new_idx = widget.currentIndex()
                print(f"      {name}: index {old_idx} -> {new_idx}")
            elif isinstance(widget, QCheckBox):
                old_val = widget.isChecked()
                widget.setChecked(bool(value))
                widget.update()
                widget.repaint()
                new_val = widget.isChecked()
                print(f"      {name}: {old_val} -> {new_val} (target: {value})")
        except Exception as e:
            print(f"      ERROR setting {name}: {e}")

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
