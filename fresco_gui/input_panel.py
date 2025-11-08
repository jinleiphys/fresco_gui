"""
Input panel with text editor and form-based input for FRESCO input files
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QPushButton, QTabWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

from form_input_panel import FormInputPanel


class InputPanel(QWidget):
    """Panel containing input file editor with tabs for text and form input"""

    def __init__(self):
        super().__init__()
        self.auto_save_callback = None  # Will be set by MainWindow
        self._loading_file = False  # Flag to prevent auto-save during file loading

        # Auto-save timer (2 seconds delay after last edit)
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self._trigger_auto_save)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI with tabs for text editor and form builder"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Tab 1: Text Editor (original functionality)
        text_editor_widget = QWidget()
        text_layout = QVBoxLayout(text_editor_widget)
        text_layout.setContentsMargins(10, 10, 10, 10)

        # Header for text editor
        header_layout = QHBoxLayout()
        header_label = QLabel("FRESCO Input File Editor")
        header_label.setObjectName("pageHeader")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Help button
        help_btn = QPushButton("Show Example")
        help_btn.clicked.connect(self.show_example)
        header_layout.addWidget(help_btn)

        text_layout.addLayout(header_layout)

        # Text editor for input file
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter FRESCO input file content here or load from file...")

        # Use monospace font
        font = QFont("Menlo", 11)
        if not font.exactMatch():
            font = QFont("Monaco", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.text_edit.setFont(font)

        # Connect text changed signal for auto-save
        self.text_edit.textChanged.connect(self._on_text_changed)

        text_layout.addWidget(self.text_edit)

        # Footer with hints for text editor
        footer = QLabel("💡 Tip: Edit FRESCO input directly here, or click 'Show Example' to load p+Ni78 example. Auto-save enabled (2s after edit).")
        footer.setObjectName("footerHint")
        footer.setWordWrap(True)
        text_layout.addWidget(footer)

        # Tab 2: Form Builder (new graphical interface)
        self.form_panel = FormInputPanel()
        # Connect form generation signal to update text editor
        self.form_panel.input_generated.connect(self.set_input_text)

        # Add tabs
        self.tabs.addTab(text_editor_widget, "Text Editor")
        self.tabs.addTab(self.form_panel, "Form Builder")

        layout.addWidget(self.tabs)

    def get_input_text(self):
        """Get the current input text"""
        return self.text_edit.toPlainText()

    def set_input_text(self, text):
        """Set the input text and switch to Text Editor tab"""
        # Temporarily disable auto-save during programmatic text setting
        self._loading_file = True
        self.text_edit.setPlainText(text)
        self._loading_file = False
        # Automatically switch to Text Editor tab after input is generated
        self.tabs.setCurrentIndex(0)  # 0 = Text Editor tab

    def load_from_file(self, file_path):
        """Load input from file and switch to Form Builder"""
        from PySide6.QtWidgets import QMessageBox
        import re

        with open(file_path, 'r') as f:
            content = f.read()

        # Validate if this is a FRESCO input file
        # Check for &FRESCO namelist or other FRESCO-specific markers
        fresco_markers = [r'&FRESCO', r'&PARTITION', r'&STATES', r'&POT', r'&COUPLING', r'&OVERLAP']
        is_fresco_file = any(re.search(marker, content, re.IGNORECASE) for marker in fresco_markers)

        if not is_fresco_file:
            # Show error message
            QMessageBox.critical(
                self,
                "Invalid FRESCO Input File",
                f"The file '{file_path}' does not appear to be a valid FRESCO input file.\n\n"
                "A valid FRESCO input file should contain at least one of the following namelists:\n"
                "  • &FRESCO\n"
                "  • &PARTITION\n"
                "  • &STATES\n"
                "  • &POT\n"
                "  • &COUPLING\n"
                "  • &OVERLAP"
            )
            return

        # Load content into text editor
        self.set_input_text(content)

        # Notify form builder to update parameter categorization
        self.form_panel.update_from_loaded_file(content)

        # Automatically switch to Form Builder tab
        self.tabs.setCurrentIndex(1)  # Index 1 is Form Builder tab

    def save_to_file(self, file_path):
        """Save input to file"""
        content = self.get_input_text()
        with open(file_path, 'w') as f:
            f.write(content)

    def clear_input(self):
        """Clear the input text"""
        self.text_edit.clear()

    def show_example(self):
        """Show an example FRESCO input - p+Ni78 elastic scattering"""
        example = """p+Ni78 Coulomb and Nuclear elastic scattering
NAMELIST
 &FRESCO hcm=0.1 rmatch=60
	 jtmin=0.0 jtmax=50 absend= 0.0010
	 thmin=0.00 thmax=180.00 thinc=1.00
 	 chans=1 smats=2  xstabl=1
	 elab(1:3)=6.9 11.00 49.350  nlab(1:3)=1 1 /

 &PARTITION namep='p' massp=1.00 zp=1
 	    namet='Ni78' masst=78.0000 zt=28 qval=-0.000 nex=1  /
 &STATES jp=0.5 bandp=1 ep=0.0000 cpot=1 jt=0.0 bandt=1 et=0.0000  /
 &partition /

 &POT kp=1 ap=1.000 at=78.000 rc=1.2  /
 &POT kp=1 type=1 p1=40.00 p2=1.2 p3=0.65 p4=10.0 p5=1.2 p6=0.500  /
 &pot /
 &overlap /
 &coupling /
"""
        self.set_input_text(example)

    def set_auto_save_callback(self, callback):
        """Set the auto-save callback function (called by MainWindow)"""
        self.auto_save_callback = callback

    def _on_text_changed(self):
        """Handle text changes - restart auto-save timer"""
        # Don't auto-save during file loading or form generation
        if self._loading_file:
            return

        # Only trigger auto-save if callback is set (i.e., file is open)
        if self.auto_save_callback:
            # Restart timer (2 seconds delay)
            self.auto_save_timer.start(2000)

    def _trigger_auto_save(self):
        """Trigger the auto-save callback"""
        if self.auto_save_callback:
            self.auto_save_callback()
