"""
Log widget for displaying FRESCO output with syntax highlighting
"""

from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor
from PySide6.QtCore import Qt, Signal
from styles import LIGHT_COLORS


class LogWidget(QWidget):
    """Widget for displaying colored log output"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the log widget"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)

        # Use monospace font from design system
        font = QFont("SF Mono", 11)
        if not font.exactMatch():
            font = QFont("Monaco", 11)
        if not font.exactMatch():
            font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.text_edit.setFont(font)

        layout.addWidget(self.text_edit)

        # Define text formats using design system colors
        self.format_normal = QTextCharFormat()
        self.format_normal.setForeground(QColor(LIGHT_COLORS['text_primary']))

        self.format_info = QTextCharFormat()
        self.format_info.setForeground(QColor(LIGHT_COLORS['info']))
        self.format_info.setFontWeight(QFont.Weight.DemiBold)

        self.format_warning = QTextCharFormat()
        self.format_warning.setForeground(QColor(LIGHT_COLORS['warning']))
        self.format_warning.setFontWeight(QFont.Weight.DemiBold)

        self.format_error = QTextCharFormat()
        self.format_error.setForeground(QColor(LIGHT_COLORS['error']))
        self.format_error.setFontWeight(QFont.Weight.DemiBold)

        self.format_success = QTextCharFormat()
        self.format_success.setForeground(QColor(LIGHT_COLORS['success']))
        self.format_success.setFontWeight(QFont.Weight.DemiBold)

    def append_output(self, text):
        """Append normal output text"""
        self._append_text(text, self.format_normal)

    def append_info(self, text):
        """Append info message"""
        self._append_text(f"[INFO] {text}", self.format_info)

    def append_warning(self, text):
        """Append warning message"""
        self._append_text(f"[WARNING] {text}", self.format_warning)

    def append_error(self, text):
        """Append error message"""
        self._append_text(f"[ERROR] {text}", self.format_error)

    def append_success(self, text):
        """Append success message"""
        self._append_text(f"[SUCCESS] {text}", self.format_success)

    def _append_text(self, text, text_format):
        """Append text with specific format"""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text + '\n', text_format)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def clear(self):
        """Clear the log"""
        self.text_edit.clear()

    def get_text(self):
        """Get all log text"""
        return self.text_edit.toPlainText()
