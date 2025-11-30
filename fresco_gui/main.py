#!/usr/bin/env python3
"""
FRESCO Studio - Modern interface for FRESCO quantum scattering calculations
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer


def main():
    """Main entry point for the FRESCO Studio application"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("FRESCO Studio")
    app.setOrganizationName("FRESCO Team")

    # Set application-wide font
    from PySide6.QtGui import QFont
    font = QFont("SF Pro Display", 10)
    app.setFont(font)

    # Show splash screen
    from splash_screen import FrescoSplashScreen
    splash = FrescoSplashScreen()
    splash.show()
    app.processEvents()

    # Simulate loading with progress updates
    splash.setProgress(10, "Loading modules...")
    app.processEvents()

    # Import main window (this can take time)
    splash.setProgress(30, "Initializing interface...")
    app.processEvents()
    from main_window import MainWindow

    splash.setProgress(50, "Loading nuclear database...")
    app.processEvents()

    # Give a brief pause to show loading
    splash.setProgress(70, "Preparing wizard...")
    app.processEvents()

    splash.setProgress(90, "Almost ready...")
    app.processEvents()

    # Create main window
    window = MainWindow()

    splash.setProgress(100, "Ready!")
    app.processEvents()

    # Brief pause to show completion
    QTimer.singleShot(500, lambda: finish_splash(splash, window))

    sys.exit(app.exec())


def finish_splash(splash, window):
    """Finish splash screen and show main window"""
    splash.finish(window)
    window.show()


if __name__ == "__main__":
    main()
