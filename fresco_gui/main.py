#!/usr/bin/env python3
"""
FRESCO Quantum Studio - Modern interface for FRESCO quantum scattering calculations
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from main_window import MainWindow


def main():
    """Main entry point for the FRESCO Quantum Studio application"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("FRESCO Quantum Studio")
    app.setOrganizationName("FRESCO Team")

    # Set application-wide font
    from PySide6.QtGui import QFont
    font = QFont("SF Pro Display", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
