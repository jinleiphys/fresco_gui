"""
Dynamic General Parameters Widget
Displays FRESCO namelist parameters that are categorized as "General"
Adapts based on calculation type and loaded input files
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox,
    QDoubleSpinBox, QSpinBox, QLineEdit, QComboBox, QCheckBox, QLabel
)
from PySide6.QtCore import Qt, Signal

from fresco_namelist import FRESCO_NAMELIST


class DynamicGeneralParametersWidget(QWidget):
    """
    Widget that dynamically displays FRESCO general parameters
    based on parameter manager categorization
    """

    parameters_changed = Signal()  # Emitted when any parameter changes

    def __init__(self, parameter_manager=None, parent=None):
        """
        Initialize the widget

        Args:
            parameter_manager: ParameterManager instance for dynamic categorization
            parent: Parent widget
        """
        super().__init__(parent)
        self.parameter_manager = parameter_manager
        self.parameter_widgets = {}  # Store widgets for each parameter
        self.form_layout = None
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        print(f"[DynamicGeneralParams] Initializing UI...", flush=True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create group box with modern card design
        self.group_box = QGroupBox("General Parameters")
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
                color: #007AFF;
            }
        """)

        # Container for form layout
        self.content_widget = QWidget()
        self.form_layout = QFormLayout(self.content_widget)
        self.form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.form_layout.setLabelAlignment(Qt.AlignLeft)
        self.form_layout.setSpacing(8)

        # Build initial parameters
        self._rebuild_parameters()

        # Add content to group box
        group_layout = QVBoxLayout()
        group_layout.addWidget(self.content_widget)
        self.group_box.setLayout(group_layout)

        layout.addWidget(self.group_box)

    def _rebuild_parameters(self):
        """Rebuild all parameter widgets based on current categorization"""
        print(f"  [DynamicGeneralParams] Rebuilding parameters...", flush=True)

        try:
            # Clear existing widgets - collect first, then delete
            print(f"    Clearing existing widgets (count={self.form_layout.count()})...", flush=True)
            widgets_to_delete = []
            items_to_delete = []

            while self.form_layout.count():
                item = self.form_layout.takeAt(0)
                items_to_delete.append(item)
                if item.widget():
                    widgets_to_delete.append(item.widget())

            # Now delete all collected widgets
            for widget in widgets_to_delete:
                widget.hide()  # Hide first
                widget.setParent(None)  # Unparent
                widget.deleteLater()  # Schedule for deletion

            # Clear parameter widgets dict
            self.parameter_widgets.clear()
            print(f"    Widgets cleared ({len(widgets_to_delete)} widgets deleted)", flush=True)

        except Exception as e:
            print(f"    ERROR during widget clearing: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return

        # Get general parameters from parameter manager
        if not self.parameter_manager:
            print(f"    WARNING: No parameter manager set!")
            # Add a warning label
            warning_label = QLabel("⚠️ No parameter manager configured")
            warning_label.setStyleSheet("color: orange; font-style: italic;")
            self.form_layout.addRow(warning_label)
            return

        general_param_names = self.parameter_manager.get_general_parameters()
        print(f"    Building widgets for {len(general_param_names)} general parameters:")
        print(f"      {general_param_names}")

        if not general_param_names:
            print(f"    WARNING: No general parameters in parameter manager!")
            # Add info label
            info_label = QLabel("No general parameters to display")
            info_label.setStyleSheet("color: gray; font-style: italic;")
            self.form_layout.addRow(info_label)
            return

        # Create widgets for each general parameter
        try:
            for param_name in general_param_names:
                print(f"      Creating widget for {param_name}...", flush=True)
                param = FRESCO_NAMELIST.get_parameter(param_name)
                if not param:
                    print(f"      Warning: parameter '{param_name}' not found in FRESCO_NAMELIST")
                    continue

                # Create label with tooltip
                label = QLabel(param.label + ":")
                label.setToolTip(param.tooltip)
                label.setStyleSheet("font-weight: normal;")

                # Create appropriate widget based on parameter type
                widget_input = self._create_widget_for_parameter(param)

                # Store widget for later retrieval
                self.parameter_widgets[param_name] = widget_input

                # Add to form layout
                self.form_layout.addRow(label, widget_input)
                print(f"      ✓ Created widget for {param_name}", flush=True)

            print(f"  [DynamicGeneralParams] Rebuild complete: {len(self.parameter_widgets)} widgets created", flush=True)
        except Exception as e:
            print(f"  ERROR during widget creation: {e}", flush=True)
            import traceback
            traceback.print_exc()

        print(f"  [DynamicGeneralParams] About to return from _rebuild_parameters()", flush=True)

    def _create_widget_for_parameter(self, param):
        """Create appropriate widget for a parameter based on its type"""
        widget_style = """
            QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox {
                padding: 5px 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus {
                border-color: #007AFF;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """

        if param.param_type == "number":
            if param.step and param.step < 1:  # Float
                widget = QDoubleSpinBox()
                widget.setDecimals(len(str(param.step).split('.')[-1]))
            else:  # Int
                widget = QSpinBox()

            if param.minimum is not None:
                widget.setMinimum(param.minimum)
            else:
                widget.setMinimum(-999999)

            if param.maximum is not None:
                widget.setMaximum(param.maximum)
            else:
                widget.setMaximum(999999)

            if param.step:
                widget.setSingleStep(param.step)

            if param.default is not None:
                widget.setValue(param.default)
            else:
                widget.setSpecialValueText("(default)")

            widget.setToolTip(param.tooltip)
            widget.setStyleSheet(widget_style)
            widget.valueChanged.connect(lambda: self.parameters_changed.emit())

        elif param.param_type == "text":
            widget = QLineEdit()
            if param.default:
                widget.setText(str(param.default))
            widget.setPlaceholderText("(optional)")
            widget.setToolTip(param.tooltip)
            widget.setStyleSheet(widget_style)
            widget.textChanged.connect(lambda: self.parameters_changed.emit())

        elif param.param_type == "select":
            widget = QComboBox()
            for value, text in param.options:
                widget.addItem(text, value)
            # Set default
            if param.default is not None:
                for i in range(widget.count()):
                    if widget.itemData(i) == param.default:
                        widget.setCurrentIndex(i)
                        break
            widget.setToolTip(param.tooltip)
            widget.setStyleSheet(widget_style)
            widget.currentIndexChanged.connect(lambda: self.parameters_changed.emit())

        else:  # checkbox
            widget = QCheckBox()
            if param.default:
                widget.setChecked(bool(param.default))
            widget.setToolTip(param.tooltip)
            widget.stateChanged.connect(lambda: self.parameters_changed.emit())

        return widget

    def refresh(self):
        """Refresh the widget to reflect current parameter categorization"""
        print(f"  [DynamicGeneralParams] refresh() called", flush=True)
        self._rebuild_parameters()
        print(f"  [DynamicGeneralParams] About to return from refresh()", flush=True)

    def set_parameter_manager(self, parameter_manager):
        """
        Set or update the parameter manager

        Args:
            parameter_manager: ParameterManager instance
        """
        self.parameter_manager = parameter_manager
        self.refresh()

    def get_parameter_values(self):
        """Get all parameter values as a dictionary (including default values)"""
        values = {}

        for param_name, widget in self.parameter_widgets.items():
            param = FRESCO_NAMELIST.get_parameter(param_name)
            if not param:
                continue

            # Get value based on widget type
            # Always include the value, even if it equals default
            # This ensures all general parameters are in the output
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
                values[param_name] = value

            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:  # Only include non-empty text
                    values[param_name] = text

            elif isinstance(widget, QComboBox):
                value = widget.currentData()
                if value is not None:  # Include if not None
                    values[param_name] = value

            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
                values[param_name] = value

        return values

    def set_parameter_value(self, name: str, value):
        """Set a parameter value"""
        if name not in self.parameter_widgets:
            print(f"      [DynamicGeneralParams] Parameter '{name}' not in widget dict")
            return

        widget = self.parameter_widgets[name]
        print(f"      [DynamicGeneralParams] Setting {name} = {value} (widget type: {widget.__class__.__name__})")

        try:
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                old_val = widget.value()
                widget.setValue(value)
                widget.update()
                widget.repaint()
                new_val = widget.value()
                print(f"        {name}: {old_val} -> {new_val} (target: {value})")
            elif isinstance(widget, QLineEdit):
                old_val = widget.text()
                widget.setText(str(value))
                widget.update()
                widget.repaint()
                new_val = widget.text()
                print(f"        {name}: '{old_val}' -> '{new_val}' (target: '{value}')")
            elif isinstance(widget, QComboBox):
                old_idx = widget.currentIndex()
                for i in range(widget.count()):
                    if widget.itemData(i) == value:
                        widget.setCurrentIndex(i)
                        widget.update()
                        widget.repaint()
                        break
                new_idx = widget.currentIndex()
                print(f"        {name}: index {old_idx} -> {new_idx}")
            elif isinstance(widget, QCheckBox):
                old_val = widget.isChecked()
                widget.setChecked(bool(value))
                widget.update()
                widget.repaint()
                new_val = widget.isChecked()
                print(f"        {name}: {old_val} -> {new_val} (target: {value})")
        except Exception as e:
            print(f"        ERROR setting {name}: {e}")

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
