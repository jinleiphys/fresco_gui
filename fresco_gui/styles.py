"""
FRESCO Studio - Modern Design System
Professional, unified styling with light and dark themes
"""

# =============================================================================
# DESIGN TOKENS - Color System
# =============================================================================

# Light Theme Colors
LIGHT_COLORS = {
    # Primary
    'primary': '#2563eb',          # Modern blue
    'primary_hover': '#1d4ed8',
    'primary_active': '#1e40af',
    'primary_light': '#eff6ff',

    # Surface & Background
    'bg_primary': '#ffffff',
    'bg_secondary': '#f9fafb',
    'bg_tertiary': '#f3f4f6',
    'bg_elevated': '#ffffff',

    # Text
    'text_primary': '#111827',
    'text_secondary': '#6b7280',
    'text_tertiary': '#9ca3af',
    'text_inverse': '#ffffff',

    # Borders
    'border_primary': '#e5e7eb',
    'border_secondary': '#d1d5db',
    'border_focus': '#2563eb',

    # Semantic Colors
    'success': '#10b981',
    'success_light': '#d1fae5',
    'warning': '#f59e0b',
    'warning_light': '#fef3c7',
    'error': '#ef4444',
    'error_light': '#fee2e2',
    'info': '#3b82f6',
    'info_light': '#dbeafe',

    # Interactive
    'hover': '#f9fafb',
    'active': '#f3f4f6',
    'disabled': '#e5e7eb',
    'disabled_text': '#9ca3af',

    # Shadows
    'shadow_sm': 'rgba(0, 0, 0, 0.05)',
    'shadow_md': 'rgba(0, 0, 0, 0.1)',
    'shadow_lg': 'rgba(0, 0, 0, 0.15)',
}

# Dark Theme Colors
DARK_COLORS = {
    # Primary
    'primary': '#3b82f6',
    'primary_hover': '#60a5fa',
    'primary_active': '#2563eb',
    'primary_light': '#1e3a8a',

    # Surface & Background
    'bg_primary': '#111827',
    'bg_secondary': '#1f2937',
    'bg_tertiary': '#374151',
    'bg_elevated': '#1f2937',

    # Text
    'text_primary': '#f9fafb',
    'text_secondary': '#d1d5db',
    'text_tertiary': '#9ca3af',
    'text_inverse': '#111827',

    # Borders
    'border_primary': '#374151',
    'border_secondary': '#4b5563',
    'border_focus': '#3b82f6',

    # Semantic Colors
    'success': '#10b981',
    'success_light': '#064e3b',
    'warning': '#f59e0b',
    'warning_light': '#78350f',
    'error': '#ef4444',
    'error_light': '#7f1d1d',
    'info': '#3b82f6',
    'info_light': '#1e3a8a',

    # Interactive
    'hover': '#1f2937',
    'active': '#374151',
    'disabled': '#374151',
    'disabled_text': '#6b7280',

    # Shadows
    'shadow_sm': 'rgba(0, 0, 0, 0.3)',
    'shadow_md': 'rgba(0, 0, 0, 0.4)',
    'shadow_lg': 'rgba(0, 0, 0, 0.5)',
}

# =============================================================================
# DESIGN TOKENS - Spacing (8px grid system)
# =============================================================================
SPACING = {
    'xs': '4px',
    'sm': '8px',
    'md': '12px',
    'lg': '16px',
    'xl': '24px',
    'xxl': '32px',
}

# =============================================================================
# DESIGN TOKENS - Typography
# =============================================================================
TYPOGRAPHY = {
    'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'font_mono': '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace',

    # Font sizes
    'text_xs': '11px',
    'text_sm': '12px',
    'text_base': '13px',
    'text_lg': '14px',
    'text_xl': '16px',
    'text_2xl': '18px',
    'text_3xl': '24px',

    # Font weights
    'weight_normal': '400',
    'weight_medium': '500',
    'weight_semibold': '600',
    'weight_bold': '700',
}

# =============================================================================
# DESIGN TOKENS - Border & Radius
# =============================================================================
BORDERS = {
    'radius_sm': '4px',
    'radius_md': '6px',
    'radius_lg': '8px',
    'radius_xl': '12px',

    'width_thin': '1px',
    'width_normal': '1.5px',
    'width_thick': '2px',
}

# =============================================================================
# STYLE GENERATOR
# =============================================================================

def generate_theme_stylesheet(theme='light'):
    """Generate complete stylesheet for the theme"""
    colors = LIGHT_COLORS if theme == 'light' else DARK_COLORS

    return f"""
    /* ========================================================================= */
    /* GLOBAL STYLES */
    /* ========================================================================= */

    QMainWindow {{
        background-color: {colors['bg_secondary']};
    }}

    QWidget {{
        background-color: {colors['bg_primary']};
        color: {colors['text_primary']};
        font-family: {TYPOGRAPHY['font_family']};
        font-size: {TYPOGRAPHY['text_base']};
    }}

    /* ========================================================================= */
    /* GROUPBOX - Card Style */
    /* ========================================================================= */

    QGroupBox {{
        background-color: {colors['bg_elevated']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
        border-radius: {BORDERS['radius_lg']};
        margin-top: {SPACING['lg']};
        padding: {SPACING['lg']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
        font-size: {TYPOGRAPHY['text_lg']};
        color: {colors['text_primary']};
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: {SPACING['md']};
        padding: 0 {SPACING['sm']};
        background-color: transparent;
        color: {colors['text_primary']};
    }}

    QGroupBox:hover {{
        border-color: {colors['border_secondary']};
    }}

    /* ========================================================================= */
    /* BUTTONS - Modern Flat Style */
    /* ========================================================================= */

    QPushButton {{
        background-color: {colors['primary']};
        color: {colors['text_inverse']};
        border: none;
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']} {SPACING['lg']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
        font-size: {TYPOGRAPHY['text_sm']};
        min-height: 24px;
    }}

    QPushButton:hover {{
        background-color: {colors['primary_hover']};
    }}

    QPushButton:pressed {{
        background-color: {colors['primary_active']};
    }}

    QPushButton:disabled {{
        background-color: {colors['disabled']};
        color: {colors['disabled_text']};
    }}

    /* Secondary Button Style */
    QPushButton[styleClass="secondary"] {{
        background-color: {colors['bg_tertiary']};
        color: {colors['text_primary']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
    }}

    QPushButton[styleClass="secondary"]:hover {{
        background-color: {colors['hover']};
        border-color: {colors['border_secondary']};
    }}

    /* ========================================================================= */
    /* INPUT FIELDS - Clean Modern Style */
    /* ========================================================================= */

    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {{
        background-color: {colors['bg_primary']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']};
        color: {colors['text_primary']};
        selection-background-color: {colors['primary']};
        selection-color: {colors['text_inverse']};
    }}

    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
    QComboBox:focus, QTextEdit:focus {{
        border: {BORDERS['width_normal']} solid {colors['border_focus']};
        background-color: {colors['bg_primary']};
    }}

    QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover,
    QComboBox:hover, QTextEdit:hover {{
        border-color: {colors['border_secondary']};
    }}

    QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled,
    QComboBox:disabled, QTextEdit:disabled {{
        background-color: {colors['bg_tertiary']};
        color: {colors['disabled_text']};
    }}

    /* ========================================================================= */
    /* COMBOBOX - Modern Dropdown */
    /* ========================================================================= */

    QComboBox::drop-down {{
        border: none;
        width: 24px;
        padding-right: {SPACING['sm']};
    }}

    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {colors['text_secondary']};
        margin-right: {SPACING['xs']};
    }}

    QComboBox:hover::down-arrow {{
        border-top-color: {colors['primary']};
    }}

    QComboBox QAbstractItemView {{
        background-color: {colors['bg_elevated']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['xs']};
        selection-background-color: {colors['primary']};
        selection-color: {colors['text_inverse']};
    }}

    /* ========================================================================= */
    /* TABS - Clean Modern Design */
    /* ========================================================================= */

    QTabWidget::pane {{
        background-color: {colors['bg_primary']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
        border-radius: {BORDERS['radius_lg']};
        top: -1px;
    }}

    QTabBar::tab {{
        background-color: {colors['bg_secondary']};
        color: {colors['text_secondary']};
        border: none;
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']} {SPACING['lg']};
        margin-right: {SPACING['xs']};
        margin-bottom: {SPACING['xs']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        font-size: {TYPOGRAPHY['text_sm']};
        min-width: 80px;
    }}

    QTabBar::tab:selected {{
        background-color: {colors['primary']};
        color: {colors['text_inverse']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
    }}

    QTabBar::tab:hover:!selected {{
        background-color: {colors['hover']};
        color: {colors['text_primary']};
    }}

    /* ========================================================================= */
    /* SCROLLBARS - Minimal Modern Style */
    /* ========================================================================= */

    QScrollBar:vertical {{
        background-color: transparent;
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: {colors['border_secondary']};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {colors['text_tertiary']};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background-color: transparent;
        height: 10px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {colors['border_secondary']};
        border-radius: 5px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {colors['text_tertiary']};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: transparent;
        width: 0px;
    }}

    /* ========================================================================= */
    /* MENUBAR & MENU - Clean Modern Design */
    /* ========================================================================= */

    QMenuBar {{
        background-color: {colors['bg_elevated']};
        border-bottom: {BORDERS['width_thin']} solid {colors['border_primary']};
        padding: {SPACING['xs']} {SPACING['sm']};
        spacing: {SPACING['xs']};
    }}

    QMenuBar::item {{
        background-color: transparent;
        color: {colors['text_primary']};
        padding: {SPACING['sm']} {SPACING['md']};
        border-radius: {BORDERS['radius_sm']};
        font-weight: {TYPOGRAPHY['weight_medium']};
    }}

    QMenuBar::item:selected {{
        background-color: {colors['hover']};
    }}

    QMenuBar::item:pressed {{
        background-color: {colors['active']};
    }}

    QMenu {{
        background-color: {colors['bg_elevated']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
        border-radius: {BORDERS['radius_lg']};
        padding: {SPACING['xs']};
    }}

    QMenu::item {{
        background-color: transparent;
        color: {colors['text_primary']};
        padding: {SPACING['sm']} {SPACING['xl']};
        border-radius: {BORDERS['radius_sm']};
    }}

    QMenu::item:selected {{
        background-color: {colors['primary']};
        color: {colors['text_inverse']};
    }}

    QMenu::separator {{
        height: {BORDERS['width_thin']};
        background-color: {colors['border_primary']};
        margin: {SPACING['xs']} {SPACING['sm']};
    }}

    /* ========================================================================= */
    /* TOOLBAR - Flat Modern Design */
    /* ========================================================================= */

    QToolBar {{
        background-color: {colors['bg_elevated']};
        border-bottom: {BORDERS['width_thin']} solid {colors['border_primary']};
        spacing: {SPACING['sm']};
        padding: {SPACING['sm']};
    }}

    QToolButton {{
        background-color: transparent;
        color: {colors['text_primary']};
        border: {BORDERS['width_thin']} solid transparent;
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']} {SPACING['md']};
        font-weight: {TYPOGRAPHY['weight_medium']};
    }}

    QToolButton:hover {{
        background-color: {colors['hover']};
        border-color: {colors['border_primary']};
    }}

    QToolButton:pressed {{
        background-color: {colors['active']};
    }}

    /* ========================================================================= */
    /* STATUS BAR */
    /* ========================================================================= */

    QStatusBar {{
        background-color: {colors['bg_elevated']};
        border-top: {BORDERS['width_thin']} solid {colors['border_primary']};
        color: {colors['text_secondary']};
        font-size: {TYPOGRAPHY['text_sm']};
        padding: {SPACING['xs']} {SPACING['md']};
    }}

    /* ========================================================================= */
    /* SPLITTER */
    /* ========================================================================= */

    QSplitter::handle {{
        background-color: {colors['border_primary']};
        width: 1px;
        height: 1px;
    }}

    QSplitter::handle:hover {{
        background-color: {colors['primary']};
    }}

    /* ========================================================================= */
    /* LABELS */
    /* ========================================================================= */

    QLabel {{
        background-color: transparent;
        color: {colors['text_primary']};
    }}

    QFormLayout QLabel {{
        color: {colors['text_primary']};
        font-weight: {TYPOGRAPHY['weight_medium']};
    }}

    /* ========================================================================= */
    /* SCROLLAREA */
    /* ========================================================================= */

    QScrollArea {{
        background-color: transparent;
        border: none;
    }}

    /* ========================================================================= */
    /* CHECKBOXES */
    /* ========================================================================= */

    QCheckBox {{
        spacing: {SPACING['sm']};
        color: {colors['text_primary']};
    }}

    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: {BORDERS['width_thin']} solid {colors['border_secondary']};
        border-radius: {BORDERS['radius_sm']};
        background-color: {colors['bg_primary']};
    }}

    QCheckBox::indicator:hover {{
        border-color: {colors['primary']};
    }}

    QCheckBox::indicator:checked {{
        background-color: {colors['primary']};
        border-color: {colors['primary']};
        image: none;
    }}

    /* ========================================================================= */
    /* SPECIAL COMPONENT STYLES (Object Names) */
    /* ========================================================================= */

    /* Section Headers */
    QLabel#sectionHeader {{
        font-size: {TYPOGRAPHY['text_xl']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
        color: {colors['primary']};
        padding: {SPACING['sm']} 0;
    }}

    QLabel#pageHeader {{
        font-size: {TYPOGRAPHY['text_lg']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
        color: {colors['text_primary']};
        padding: {SPACING['xs']} 0;
    }}

    /* Info Labels */
    QLabel#infoLabel {{
        color: {colors['text_secondary']};
        font-size: {TYPOGRAPHY['text_sm']};
        font-style: italic;
        padding: {SPACING['xs']} 0;
    }}

    QLabel#footerHint {{
        color: {colors['text_secondary']};
        font-size: {TYPOGRAPHY['text_xs']};
        font-style: italic;
        padding: {SPACING['sm']} 0;
    }}

    /* Info Box (with background) */
    QLabel#infoBox {{
        color: {colors['text_secondary']};
        font-size: {TYPOGRAPHY['text_xs']};
        padding: {SPACING['sm']};
        background-color: {colors['bg_tertiary']};
        border-radius: {BORDERS['radius_md']};
    }}

    /* Count Label */
    QLabel#countLabel {{
        color: {colors['text_tertiary']};
        font-size: {TYPOGRAPHY['text_xs']};
        padding: {SPACING['xs']} 0;
    }}

    /* Parameter Labels (small) */
    QLabel#paramLabel {{
        font-size: {TYPOGRAPHY['text_xs']};
        color: {colors['text_primary']};
        font-weight: {TYPOGRAPHY['weight_medium']};
    }}

    /* POT Label */
    QLabel#potLabel {{
        font-weight: {TYPOGRAPHY['weight_medium']};
        color: {colors['text_secondary']};
        font-size: {TYPOGRAPHY['text_sm']};
    }}

    /* Category Button */
    QPushButton#categoryButton {{
        text-align: left;
        padding: {SPACING['sm']} {SPACING['md']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
        border-radius: {BORDERS['radius_md']};
        background-color: {colors['bg_primary']};
        font-size: {TYPOGRAPHY['text_sm']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        color: {colors['text_primary']};
    }}

    QPushButton#categoryButton:hover {{
        background-color: {colors['hover']};
        border-color: {colors['border_secondary']};
    }}

    QPushButton#categoryButton:checked {{
        background-color: {colors['primary']};
        color: {colors['text_inverse']};
        border-color: {colors['primary']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
    }}

    /* Reset Button */
    QPushButton#resetButton {{
        background-color: {colors['bg_tertiary']};
        color: {colors['text_primary']};
        border: {BORDERS['width_thin']} solid {colors['border_primary']};
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']} {SPACING['md']};
        font-size: {TYPOGRAPHY['text_xs']};
        font-weight: {TYPOGRAPHY['weight_medium']};
    }}

    QPushButton#resetButton:hover {{
        background-color: {colors['hover']};
        border-color: {colors['border_secondary']};
    }}

    QPushButton#resetButton:pressed {{
        background-color: {colors['active']};
    }}

    /* Preset/Success Button */
    QPushButton#presetButton {{
        background-color: {colors['success']};
        color: white;
        border: none;
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']} {SPACING['md']};
        font-weight: {TYPOGRAPHY['weight_medium']};
        font-size: {TYPOGRAPHY['text_sm']};
    }}

    QPushButton#presetButton:hover {{
        background-color: #059669;
    }}

    QPushButton#presetButton:pressed {{
        background-color: #047857;
    }}

    /* Remove Button - Error Red */
    QPushButton#removeButton {{
        background-color: {colors['error']};
        color: white;
        border: none;
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['xs']} {SPACING['md']};
        font-size: {TYPOGRAPHY['text_xs']};
        font-weight: {TYPOGRAPHY['weight_medium']};
    }}

    QPushButton#removeButton:hover {{
        background-color: #dc2626;
    }}

    QPushButton#removeButton:pressed {{
        background-color: #b91c1c;
    }}

    /* Run Button - Success Green */
    QToolButton#runButton {{
        background-color: {colors['success']};
        color: white;
        border: none;
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']} {SPACING['lg']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
        min-width: 60px;
    }}

    QToolButton#runButton:hover {{
        background-color: #059669;
    }}

    QToolButton#runButton:pressed {{
        background-color: #047857;
    }}

    QToolButton#runButton:disabled {{
        background-color: {colors['disabled']};
        color: {colors['disabled_text']};
    }}

    /* Stop Button - Error Red */
    QToolButton#stopButton {{
        background-color: {colors['error']};
        color: white;
        border: none;
        border-radius: {BORDERS['radius_md']};
        padding: {SPACING['sm']} {SPACING['lg']};
        font-weight: {TYPOGRAPHY['weight_semibold']};
        min-width: 60px;
    }}

    QToolButton#stopButton:hover {{
        background-color: #dc2626;
    }}

    QToolButton#stopButton:pressed {{
        background-color: #b91c1c;
    }}

    QToolButton#stopButton:disabled {{
        background-color: {colors['disabled']};
        color: {colors['disabled_text']};
    }}
    """


# =============================================================================
# PUBLIC API
# =============================================================================

LIGHT_THEME = generate_theme_stylesheet('light')
DARK_THEME = generate_theme_stylesheet('dark')


def apply_modern_style(widget, theme='light'):
    """
    Apply modern styling to a widget

    Args:
        widget: QWidget to apply styling to
        theme: 'light' or 'dark'
    """
    if theme == 'dark':
        widget.setStyleSheet(DARK_THEME)
    else:
        widget.setStyleSheet(LIGHT_THEME)


def get_color(color_name, theme='light'):
    """
    Get a color value from the theme

    Args:
        color_name: Name of the color (e.g., 'primary', 'text_primary')
        theme: 'light' or 'dark'

    Returns:
        Color hex code as string
    """
    colors = LIGHT_COLORS if theme == 'light' else DARK_COLORS
    return colors.get(color_name, '#000000')


def get_spacing(size):
    """Get spacing value (xs, sm, md, lg, xl, xxl)"""
    return SPACING.get(size, '8px')


def get_radius(size):
    """Get border radius value (sm, md, lg, xl)"""
    return BORDERS.get(f'radius_{size}', '6px')
