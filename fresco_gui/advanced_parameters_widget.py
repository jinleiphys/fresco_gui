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
        self.category_group_boxes = []  # Track all category group boxes for accordion behavior
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create collapsible group box with modern design
        self.group_box = QGroupBox("Advanced Parameters")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Collapsed by default
        self.group_box.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                margin-top: 8px;
                padding: 16px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                background-color: white;
                color: #374151;
            }
        """)

        # Content widget (hidden when collapsed)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)

        # Info label
        info_label = QLabel(
            "💡 These parameters have sensible defaults. Hover over names for descriptions."
        )
        info_label.setStyleSheet("color: #6b7280; font-size: 11px; padding: 8px; background-color: #f3f4f6; border-radius: 4px;")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        # Count label showing number of advanced parameters
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #9ca3af; font-size: 10px; padding: 4px 0;")
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
        content_layout.addWidget(self.categories_scroll)

        # Reset button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
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
        """Rebuild categories in grid layout (3 per row)"""
        from PySide6.QtWidgets import QGridLayout

        # Clear existing layout if any
        if self.categories_layout:
            while self.categories_layout.count():
                item = self.categories_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(self.categories_layout)  # Delete old layout

        # Create new grid layout
        self.categories_layout = QGridLayout(self.categories_container)
        self.categories_layout.setSpacing(15)

        # Clear parameter widgets dict (will be repopulated)
        self.parameter_widgets.clear()

        # Clear category group boxes list
        self.category_group_boxes.clear()

        # Get parameters to display
        if self.parameter_manager:
            # Use dynamic categorization
            params_by_category = self.parameter_manager.get_advanced_parameters_by_category()
            advanced_param_names = set(self.parameter_manager.get_advanced_parameters())

            # Create category widgets (3 per row)
            row = 0
            col = 0

            for cat_key, cat_info in FRESCO_NAMELIST.categories.items():
                if cat_key in params_by_category and params_by_category[cat_key]:
                    # Get parameter objects for these names
                    params = [FRESCO_NAMELIST.get_parameter(name)
                             for name in params_by_category[cat_key]
                             if FRESCO_NAMELIST.get_parameter(name)]
                    if params:
                        # Create category group box
                        category_widget = self._create_category_column(cat_info, params)
                        self.categories_layout.addWidget(category_widget, row, col)

                        col += 1
                        if col >= 3:  # 3 categories per row
                            col = 0
                            row += 1

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
            row = 0
            col = 0

            for cat_key, cat_info in FRESCO_NAMELIST.categories.items():
                params = FRESCO_NAMELIST.get_parameters_by_category(cat_key)
                if params:
                    # Filter out BASIC_PARAMETERS
                    filtered_params = [p for p in params
                                     if p.name not in FRESCO_NAMELIST.BASIC_PARAMETERS]
                    if filtered_params:
                        category_widget = self._create_category_column(cat_info, filtered_params)
                        self.categories_layout.addWidget(category_widget, row, col)

                        col += 1
                        if col >= 3:  # 3 categories per row
                            col = 0
                            row += 1

            self.count_label.setText("Using static parameter categorization")

    def _on_category_toggled(self, toggled_box, checked):
        """
        Handle category toggle for accordion behavior
        When one category is expanded, collapse all others
        """
        # First, show/hide the content of the toggled box
        if hasattr(toggled_box, 'content_widget'):
            toggled_box.content_widget.setVisible(checked)

        # Then, if expanding, collapse all other categories
        if checked:
            for group_box in self.category_group_boxes:
                if group_box != toggled_box and group_box.isChecked():
                    # Temporarily block signals to avoid triggering toggle chain
                    group_box.blockSignals(True)
                    group_box.setChecked(False)
                    # Hide its content
                    if hasattr(group_box, 'content_widget'):
                        group_box.content_widget.setVisible(False)
                    group_box.blockSignals(False)

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

    def _create_category_column(self, cat_info, parameters):
        """Create a collapsible single-column category widget with modern card design"""
        # Create collapsible group box for this category
        group_box = QGroupBox(f"{cat_info['title']}")
        group_box.setCheckable(True)
        group_box.setChecked(False)  # Collapsed by default
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: 500;
                font-size: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 4px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 6px;
                background-color: white;
                color: #6b7280;
            }
            QGroupBox:hover {
                border-color: #cbd5e1;
            }
            QGroupBox::indicator {
                width: 0px;
                height: 0px;
            }
        """)

        # Container widget for parameters (will be hidden/shown)
        content_widget = QWidget()

        # Single column layout for parameters
        form_layout = QFormLayout(content_widget)
        form_layout.setSpacing(8)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Define consistent widget style
        widget_style = """
            QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox {
                padding: 4px 6px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
                font-size: 11px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus {
                border-color: #007AFF;
            }
        """

        for param in parameters:
            # All filtering is now handled by parameter_manager
            # Create label with tooltip
            label = QLabel(param.label + ":")
            label.setToolTip(param.tooltip)
            label.setStyleSheet("font-size: 11px; color: #374151;")

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
                widget_input.setStyleSheet(widget_style)
                widget_input.valueChanged.connect(self.parameters_changed.emit)

            elif param.param_type == "text":
                widget_input = QLineEdit()
                if param.default:
                    widget_input.setText(str(param.default))
                widget_input.setPlaceholderText("(optional)")
                widget_input.setToolTip(param.tooltip)
                widget_input.setStyleSheet(widget_style)
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
                widget_input.setStyleSheet(widget_style)
                widget_input.currentIndexChanged.connect(self.parameters_changed.emit)

            else:  # checkbox
                widget_input = QCheckBox()
                if param.default:
                    widget_input.setChecked(bool(param.default))
                widget_input.setToolTip(param.tooltip)
                widget_input.stateChanged.connect(self.parameters_changed.emit)

            # Store widget for later retrieval
            self.parameter_widgets[param.name] = widget_input

            # Add to form layout (single column)
            form_layout.addRow(label, widget_input)

        # Create layout for group box and add content widget
        group_layout = QVBoxLayout()
        group_layout.addWidget(content_widget)
        group_box.setLayout(group_layout)

        # Store content widget reference in group_box for later access
        group_box.content_widget = content_widget
        content_widget.setVisible(False)  # Start collapsed

        # Add to category group boxes list for accordion behavior
        self.category_group_boxes.append(group_box)

        # Connect accordion behavior: handle both visibility and mutual exclusion
        # Use a proper slot instead of lambda to avoid closure issues
        def on_toggle(checked):
            self._on_category_toggled(group_box, checked)

        group_box.toggled.connect(on_toggle)

        return group_box

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
