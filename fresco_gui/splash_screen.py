"""
Splash Screen for FRESCO Studio

Displays a modern splash screen with animated logo on application startup.
"""

import os
import math
from PySide6.QtWidgets import QSplashScreen, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QRectF


class FrescoSplashScreen(QSplashScreen):
    """Modern splash screen with animated logo"""

    def __init__(self):
        # Create a pixmap for the splash screen
        pixmap = QPixmap(480, 320)
        pixmap.fill(QColor(255, 255, 255))  # White background

        super().__init__(pixmap)

        # Set window flags for frameless splash
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # Ignore mouse clicks - don't close on click
        self.setEnabled(False)

        # Animation state
        self.animation_angle = 0.0

        # Progress message
        self.message = "Loading..."
        self.progress = 0

        # Draw the splash screen
        self._draw_splash()

        # Start animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(30)  # ~33 FPS

    def _animate(self):
        """Update animation frame"""
        self.animation_angle += 3.0  # Degrees per frame
        if self.animation_angle >= 360:
            self.animation_angle -= 360
        self._draw_splash()

    def close(self):
        """Stop animation when closing"""
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        super().close()

    def _draw_splash(self):
        """Draw the splash screen content"""
        pixmap = QPixmap(480, 320)
        pixmap.fill(QColor(255, 255, 255))  # White background

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
        logo_size = 120
        logo_x = (480 - logo_size) // 2
        logo_y = 40
        logo_rect = QRectF(logo_x, logo_y, logo_size, logo_size)

        # Always draw animated logo (ignore SVG)
        center_x = logo_x + logo_size // 2
        center_y = logo_y + logo_size // 2

        # Orbit parameters
        orbit_rx = 50  # Semi-major axis
        orbit_ry = 20  # Semi-minor axis
        orbit_colors = [
            QColor(59, 130, 246),   # Blue
            QColor(16, 185, 129),   # Green
            QColor(236, 72, 153),   # Pink
        ]
        orbit_rotations = [-30, 30, 90]  # Degrees

        # Draw orbits
        for i, (color, rotation) in enumerate(zip(orbit_colors, orbit_rotations)):
            pen = QPen(color, 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(rotation)
            painter.drawEllipse(-orbit_rx, -orbit_ry, orbit_rx * 2, orbit_ry * 2)
            painter.restore()

        # Draw nucleus
        nucleus_gradient = QLinearGradient(center_x - 22, center_y - 22, center_x + 22, center_y + 22)
        nucleus_gradient.setColorAt(0, QColor(79, 142, 247))
        nucleus_gradient.setColorAt(1, QColor(37, 99, 235))
        painter.setBrush(nucleus_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center_x - 22, center_y - 22, 44, 44)

        # Draw "F" in nucleus
        f_font = QFont("Arial", 22)
        f_font.setWeight(QFont.Bold)
        painter.setFont(f_font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(center_x - 9, center_y + 8, "F")

        # Draw animated electrons
        electron_radius = 6
        for i, (color, rotation) in enumerate(zip(orbit_colors, orbit_rotations)):
            # Each electron at different phase
            angle_rad = math.radians(self.animation_angle + i * 120)
            rot_rad = math.radians(rotation)

            # Position on ellipse
            ex = orbit_rx * math.cos(angle_rad)
            ey = orbit_ry * math.sin(angle_rad)

            # Rotate position
            rx = ex * math.cos(rot_rad) - ey * math.sin(rot_rad)
            ry = ex * math.sin(rot_rad) + ey * math.cos(rot_rad)

            # Draw electron with glow effect
            glow_color = QColor(color)
            glow_color.setAlpha(100)
            painter.setBrush(glow_color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(center_x + rx - electron_radius - 2),
                               int(center_y + ry - electron_radius - 2),
                               electron_radius * 2 + 4, electron_radius * 2 + 4)

            # Draw electron
            painter.setBrush(color)
            painter.drawEllipse(int(center_x + rx - electron_radius),
                               int(center_y + ry - electron_radius),
                               electron_radius * 2, electron_radius * 2)

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
        painter.drawText(0, 210, 480, 25, Qt.AlignCenter, "Coupled Channels Calculations for Direct Nuclear Reactions")

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

    def mousePressEvent(self, event):
        """Ignore mouse clicks - don't close splash on click"""
        event.ignore()


def show_splash():
    """Create and show the splash screen, return it for later closing"""
    splash = FrescoSplashScreen()
    splash.show()
    QApplication.processEvents()
    return splash
