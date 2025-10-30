"""
Input panel with text editor and form-based input for FRESCO input files
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QPushButton, QTabWidget
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from form_input_panel import FormInputPanel


class InputPanel(QWidget):
    """Panel containing input file editor with tabs for text and form input"""

    def __init__(self):
        super().__init__()
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
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
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

        text_layout.addWidget(self.text_edit)

        # Footer with hints for text editor
        footer = QLabel("Tip: Use File → Open to load existing input files, or File → Save to save your changes.")
        footer.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
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
        """Set the input text"""
        self.text_edit.setPlainText(text)

    def load_from_file(self, file_path):
        """Load input from file"""
        with open(file_path, 'r') as f:
            content = f.read()
        self.set_input_text(content)

    def save_to_file(self, file_path):
        """Save input to file"""
        content = self.get_input_text()
        with open(file_path, 'w') as f:
            f.write(content)

    def clear_input(self):
        """Clear the input text"""
        self.text_edit.clear()

    def show_example(self):
        """Show an example FRESCO input"""
        example = """! Example FRESCO input file
! Alpha + 12C elastic scattering at 30 MeV

&FRESCO
hcm=0.05
rmatch=30.0
absend=0.01
thmax=180.0
jtmax=40
thinc=5.0
elab=30.0
iter=1
accrcy=0.005
rasym=25.0
switch=500.0
ajswtch=10.0
iblock=1
nnu=30
chans=1
smats=2
xstabl=1
koords=1
kqmax=2
/

&PARTITION
namep='alpha'
massp=4.0
zp=2.0
jp=0.0
namet='12C'
masst=12.0
zt=6.0
jt=0.0
/

&STATES
jp=0.0
bandp=1
ep=0.0
cpot=1
jt=0.0
bandt=1
et=0.0
/

&POT
kp=1
type=0
p1=0.0
p2=0.0
p3=0.0
ap=1.0
at=1.0
rc=1.3
/

&POT
kp=1
type=1
p1=50.0
p2=1.2
p3=0.65
ap=1.0
at=1.0
rc=1.3
/
"""
        self.set_input_text(example)
