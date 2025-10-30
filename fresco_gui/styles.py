"""
Modern styling for the FRESCO GUI with dark and light themes
"""

LIGHT_THEME = """
/* Main Window - Clean gradient background */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f8f9fa, stop:1 #e9ecef);
}

/* Base Widget Styling */
QWidget {
    background-color: #ffffff;
    color: #212529;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Tab Widget - Modern card style */
QTabWidget::pane {
    border: none;
    background-color: #ffffff;
    border-radius: 12px;
    padding: 0px;
    margin-top: -1px;
}

QTabWidget::tab-bar {
    alignment: left;
}

/* Tab Bar - Pill style tabs */
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f8f9fa, stop:1 #e9ecef);
    color: #6c757d;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
    margin-top: 4px;
    font-weight: 500;
    min-width: 80px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #007AFF, stop:1 #0051D5);
    color: white;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #e3f2fd, stop:1 #bbdefb);
    color: #007AFF;
}

/* Buttons - Modern gradient style */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #007AFF, stop:1 #0051D5);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0084FF, stop:1 #0066DD);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0051D5, stop:1 #003D99);
    padding: 11px 19px 9px 21px;
}

QPushButton:disabled {
    background: #dee2e6;
    color: #adb5bd;
}

/* Input Fields - Clean modern style */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #f8f9fa;
    selection-background-color: #007AFF;
    selection-color: white;
    min-height: 24px;
    color: #212529;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #007AFF;
    background-color: #ffffff;
}

QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
    border: 2px solid #ced4da;
    background-color: #ffffff;
}

/* ComboBox - Modern dropdown */
QComboBox::drop-down {
    border: none;
    padding-right: 15px;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #6c757d;
    margin-right: 5px;
}

QComboBox:hover::down-arrow {
    border-top: 6px solid #007AFF;
}

QComboBox QAbstractItemView {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    background-color: #ffffff;
    selection-background-color: #007AFF;
    selection-color: white;
    padding: 4px;
}

/* Text Edit - Code-style background */
QTextEdit {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    background-color: #f8f9fa;
    padding: 10px;
    color: #212529;
}

/* Group Box - Card style */
QGroupBox {
    border: 2px solid #e9ecef;
    border-radius: 10px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 4px 12px;
    background-color: #007AFF;
    color: white;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Scroll Area - Invisible background */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* Scrollbar - Minimal modern style */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: rgba(0, 122, 255, 0.3);
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(0, 122, 255, 0.5);
}

QScrollBar::handle:vertical:pressed {
    background-color: rgba(0, 122, 255, 0.7);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: rgba(0, 122, 255, 0.3);
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: rgba(0, 122, 255, 0.5);
}

QScrollBar::handle:horizontal:pressed {
    background-color: rgba(0, 122, 255, 0.7);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}

/* Menu Bar - Clean modern style */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e9ecef;
    padding: 6px 8px;
}

QMenuBar::item {
    padding: 8px 16px;
    border-radius: 6px;
    color: #495057;
    font-weight: 500;
}

QMenuBar::item:selected {
    background-color: #e3f2fd;
    color: #007AFF;
}

QMenuBar::item:pressed {
    background-color: #bbdefb;
}

/* Menu - Modern dropdown */
QMenu {
    background-color: #ffffff;
    border: 2px solid #e9ecef;
    border-radius: 10px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 32px 8px 16px;
    border-radius: 6px;
    color: #495057;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #007AFF, stop:1 #0084FF);
    color: white;
}

QMenu::separator {
    height: 1px;
    background-color: #e9ecef;
    margin: 4px 8px;
}

/* Toolbar - Modern flat design */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffffff, stop:1 #f8f9fa);
    border-bottom: 2px solid #e9ecef;
    spacing: 6px;
    padding: 8px;
}

QToolButton {
    background-color: transparent;
    border: 2px solid transparent;
    border-radius: 8px;
    padding: 8px 16px;
    color: #495057;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #e3f2fd;
    border: 2px solid #bbdefb;
    color: #007AFF;
}

QToolButton:pressed {
    background-color: #bbdefb;
    border: 2px solid #90caf9;
}

/* Status Bar - Subtle gradient */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f8f9fa, stop:1 #ffffff);
    border-top: 2px solid #e9ecef;
    color: #6c757d;
    padding: 4px 8px;
    font-size: 12px;
}

/* Splitter - Thin modern line */
QSplitter::handle {
    background-color: #dee2e6;
    width: 2px;
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #007AFF;
}

/* Labels - Better typography */
QLabel {
    color: #495057;
    background-color: transparent;
}

QFormLayout QLabel {
    font-weight: 600;
    color: #343a40;
    padding-right: 8px;
}

/* Run Button - Green */
QToolButton#runButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #34C759, stop:1 #28A745);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    min-width: 60px;
}

QToolButton#runButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #40D66F, stop:1 #30B956);
}

QToolButton#runButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #28A745, stop:1 #1E7E34);
    padding: 9px 15px 7px 17px;
}

QToolButton#runButton:disabled {
    background: #dee2e6;
    color: #adb5bd;
}

/* Stop Button - Red */
QToolButton#stopButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #FF3B30, stop:1 #DC3545);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    min-width: 60px;
}

QToolButton#stopButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #FF5247, stop:1 #E94A5A);
}

QToolButton#stopButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #DC3545, stop:1 #BD2130);
    padding: 9px 15px 7px 17px;
}

QToolButton#stopButton:disabled {
    background: #dee2e6;
    color: #adb5bd;
}
"""

DARK_THEME = """
/* Main Window - Dark gradient */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1a1d23, stop:1 #0d0f12);
}

/* Base Widget - Dark mode */
QWidget {
    background-color: #1e2127;
    color: #e4e7eb;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Tab Widget - Dark card */
QTabWidget::pane {
    border: none;
    background-color: #1e2127;
    border-radius: 12px;
    padding: 0px;
    margin-top: -1px;
}

QTabWidget::tab-bar {
    alignment: left;
}

/* Tab Bar - Dark pills */
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2a2e35, stop:1 #1f2228);
    color: #9ca3af;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
    margin-top: 4px;
    font-weight: 500;
    min-width: 80px;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0A84FF, stop:1 #0066DD);
    color: white;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1e3a5f, stop:1 #1a2d4a);
    color: #60a5fa;
}

/* Buttons - Dark gradient */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0A84FF, stop:1 #0066DD);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3b9eff, stop:1 #1e88ff);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #0066DD, stop:1 #004fa8);
    padding: 11px 19px 9px 21px;
}

QPushButton:disabled {
    background: #374151;
    color: #6b7280;
}

/* Input Fields - Dark style */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    border: 2px solid #374151;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #1f2937;
    selection-background-color: #0A84FF;
    selection-color: white;
    min-height: 24px;
    color: #e4e7eb;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #0A84FF;
    background-color: #111827;
}

QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
    border: 2px solid #4b5563;
    background-color: #111827;
}

/* ComboBox - Dark dropdown */
QComboBox::drop-down {
    border: none;
    padding-right: 15px;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #9ca3af;
    margin-right: 5px;
}

QComboBox:hover::down-arrow {
    border-top: 6px solid #60a5fa;
}

QComboBox QAbstractItemView {
    border: 2px solid #374151;
    border-radius: 8px;
    background-color: #1f2937;
    selection-background-color: #0A84FF;
    selection-color: white;
    padding: 4px;
}

/* Text Edit - Dark terminal style */
QTextEdit {
    border: 2px solid #374151;
    border-radius: 8px;
    background-color: #111827;
    padding: 10px;
    color: #e4e7eb;
}

/* Group Box - Dark card */
QGroupBox {
    border: 2px solid #374151;
    border-radius: 10px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
    background-color: #1e2127;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 4px 12px;
    background-color: #0A84FF;
    color: white;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Scroll Area - Dark transparent */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* Scrollbar - Dark minimal style */
QScrollBar:vertical {
    border: none;
    background-color: transparent;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: rgba(10, 132, 255, 0.4);
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(10, 132, 255, 0.6);
}

QScrollBar::handle:vertical:pressed {
    background-color: rgba(10, 132, 255, 0.8);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

QScrollBar:horizontal {
    border: none;
    background-color: transparent;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: rgba(10, 132, 255, 0.4);
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: rgba(10, 132, 255, 0.6);
}

QScrollBar::handle:horizontal:pressed {
    background-color: rgba(10, 132, 255, 0.8);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}

/* Menu Bar - Dark modern */
QMenuBar {
    background-color: #1e2127;
    border-bottom: 1px solid #374151;
    padding: 6px 8px;
}

QMenuBar::item {
    padding: 8px 16px;
    border-radius: 6px;
    color: #9ca3af;
    font-weight: 500;
}

QMenuBar::item:selected {
    background-color: #1e3a5f;
    color: #60a5fa;
}

QMenuBar::item:pressed {
    background-color: #1a2d4a;
}

/* Menu - Dark dropdown */
QMenu {
    background-color: #1e2127;
    border: 2px solid #374151;
    border-radius: 10px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 32px 8px 16px;
    border-radius: 6px;
    color: #e4e7eb;
}

QMenu::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #0A84FF, stop:1 #3b9eff);
    color: white;
}

QMenu::separator {
    height: 1px;
    background-color: #374151;
    margin: 4px 8px;
}

/* Toolbar - Dark flat */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1e2127, stop:1 #1a1d23);
    border-bottom: 2px solid #374151;
    spacing: 6px;
    padding: 8px;
}

QToolButton {
    background-color: transparent;
    border: 2px solid transparent;
    border-radius: 8px;
    padding: 8px 16px;
    color: #9ca3af;
    font-weight: 500;
}

QToolButton:hover {
    background-color: #1e3a5f;
    border: 2px solid #2a5080;
    color: #60a5fa;
}

QToolButton:pressed {
    background-color: #1a2d4a;
    border: 2px solid #1e3a5f;
}

/* Status Bar - Dark gradient */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1a1d23, stop:1 #1e2127);
    border-top: 2px solid #374151;
    color: #9ca3af;
    padding: 4px 8px;
    font-size: 12px;
}

/* Splitter - Dark thin line */
QSplitter::handle {
    background-color: #374151;
    width: 2px;
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #60a5fa;
}

/* Labels - Dark typography */
QLabel {
    color: #e4e7eb;
    background-color: transparent;
}

QFormLayout QLabel {
    font-weight: 600;
    color: #f3f4f6;
    padding-right: 8px;
}

/* Run Button - Green (Dark Theme) */
QToolButton#runButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #32D74B, stop:1 #28A745);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    min-width: 60px;
}

QToolButton#runButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3FE65B, stop:1 #32D74B);
}

QToolButton#runButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #28A745, stop:1 #1E7E34);
    padding: 9px 15px 7px 17px;
}

QToolButton#runButton:disabled {
    background: #374151;
    color: #6b7280;
}

/* Stop Button - Red (Dark Theme) */
QToolButton#stopButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #FF453A, stop:1 #DC3545);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
    min-width: 60px;
}

QToolButton#stopButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #FF6159, stop:1 #E94A5A);
}

QToolButton#stopButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #DC3545, stop:1 #BD2130);
    padding: 9px 15px 7px 17px;
}

QToolButton#stopButton:disabled {
    background: #374151;
    color: #6b7280;
}
"""


def apply_modern_style(widget, theme="light"):
    """Apply modern styling to a widget"""
    if theme == "dark":
        widget.setStyleSheet(DARK_THEME)
    else:
        widget.setStyleSheet(LIGHT_THEME)
