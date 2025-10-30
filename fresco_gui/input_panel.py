"""
Input panel with text editor for FRESCO input files
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLabel, QHBoxLayout, QPushButton
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


class InputPanel(QWidget):
    """Panel containing input file editor"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with text editor"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("FRESCO Input File Editor")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Help button
        help_btn = QPushButton("Show Example")
        help_btn.clicked.connect(self.show_example)
        header_layout.addWidget(help_btn)

        layout.addLayout(header_layout)

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

        layout.addWidget(self.text_edit)

        # Footer with hints
        footer = QLabel("Tip: Use File → Open to load existing input files, or File → Save to save your changes.")
        footer.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
        footer.setWordWrap(True)
        layout.addWidget(footer)

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
