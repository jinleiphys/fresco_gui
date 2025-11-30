"""
Splash Screen for FRESCO Studio

Displays a modern splash screen with logo on application startup.
"""

import os
from PySide6.QtWidgets import QSplashScreen, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QRectF


class FrescoSplashScreen(QSplashScreen):
    """Modern splash screen with animated logo"""

    def __init__(self):
        # Create a pixmap for the splash screen
        pixmap = QPixmap(480, 320)
        pixmap.fill(Qt.transparent)

        super().__init__(pixmap)

        # Set window flags for frameless splash
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)

        # Enable transparency
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Load SVG logo
        self.svg_renderer = None
        logo_path = os.path.join(os.path.dirname(__file__), 'resources', 'logo.svg')
        if os.path.exists(logo_path):
            self.svg_renderer = QSvgRenderer(logo_path)

        # Progress message
        self.message = "Loading..."
        self.progress = 0

        # Draw the splash screen
        self._draw_splash()

    def _draw_splash(self):
        """Draw the splash screen content"""
        pixmap = QPixmap(480, 320)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Draw background with rounded corners
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(229, 231, 235))  # Light gray border
        painter.drawRoundedRect(0, 0, 480, 320, 16, 16)

        # Draw gradient accent at top
        gradient = QLinearGradient(0, 0, 480, 0)
        gradient.setColorAt(0, QColor(37, 99, 235))  # Blue
        gradient.setColorAt(0.5, QColor(16, 185, 129))  # Green
        gradient.setColorAt(1, QColor(236, 72, 153))  # Pink
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, 480, 6, 3, 3)

        # Draw logo
        if self.svg_renderer:
            logo_size = 120
            logo_x = (480 - logo_size) // 2
            logo_y = 40
            logo_rect = QRectF(logo_x, logo_y, logo_size, logo_size)
            self.svg_renderer.render(painter, logo_rect)

        # Draw title
        title_font = QFont("SF Pro Display", 28)
        title_font.setWeight(QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(31, 41, 55))  # Dark gray
        painter.drawText(0, 175, 480, 40, Qt.AlignCenter, "FRESCO Studio")

        # Draw subtitle
        subtitle_font = QFont("SF Pro Display", 12)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(107, 114, 128))  # Medium gray
        painter.drawText(0, 210, 480, 25, Qt.AlignCenter, "Quantum Coupled Channels Calculations")

        # Draw progress bar background
        bar_x = 80
        bar_y = 260
        bar_width = 320
        bar_height = 4
        painter.setBrush(QColor(229, 231, 235))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bar_x, bar_y, bar_width, bar_height, 2, 2)

        # Draw progress bar fill
        if self.progress > 0:
            fill_width = int(bar_width * self.progress / 100)
            progress_gradient = QLinearGradient(bar_x, 0, bar_x + bar_width, 0)
            progress_gradient.setColorAt(0, QColor(37, 99, 235))
            progress_gradient.setColorAt(1, QColor(16, 185, 129))
            painter.setBrush(progress_gradient)
            painter.drawRoundedRect(bar_x, bar_y, fill_width, bar_height, 2, 2)

        # Draw message
        msg_font = QFont("SF Pro Display", 10)
        painter.setFont(msg_font)
        painter.setPen(QColor(156, 163, 175))  # Light gray
        painter.drawText(0, 275, 480, 20, Qt.AlignCenter, self.message)

        # Draw version
        version_font = QFont("SF Pro Display", 9)
        painter.setFont(version_font)
        painter.setPen(QColor(209, 213, 219))
        painter.drawText(0, 295, 480, 20, Qt.AlignCenter, "Version 1.0.0")

        painter.end()

        self.setPixmap(pixmap)

    def setProgress(self, value: int, message: str = None):
        """Update progress bar and message"""
        self.progress = min(100, max(0, value))
        if message:
            self.message = message
        self._draw_splash()
        QApplication.processEvents()

    def showMessage(self, message: str, alignment=Qt.AlignBottom | Qt.AlignHCenter, color=QColor(156, 163, 175)):
        """Override to update our custom message"""
        self.message = message
        self._draw_splash()
        QApplication.processEvents()


def show_splash():
    """Create and show the splash screen, return it for later closing"""
    splash = FrescoSplashScreen()
    splash.show()
    QApplication.processEvents()
    return splash
