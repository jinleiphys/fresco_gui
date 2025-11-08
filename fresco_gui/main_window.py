"""
Main window for FRESCO Quantum Studio application
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QToolBar, QStatusBar, QFileDialog, QMessageBox, QToolButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence
import os

from input_panel import InputPanel
from plot_widget import PlotWidget
from log_widget import LogWidget
from runner import FrescoRunner
from styles import apply_modern_style
from path_utils import get_repo_root, find_executable, get_default_test_directory, get_executable_info


class MainWindow(QMainWindow):
    """Main application window with modern layout"""

    def __init__(self):
        super().__init__()
        self.fresco_runner = FrescoRunner()
        self.current_file = None
        self.working_directory = None  # Store current working directory
        self.is_running_fresco = False  # Track whether FRESCO is running

        # Detect repository root and default paths
        self.repo_root = get_repo_root()
        self.default_test_dir = get_default_test_directory(self.repo_root)

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("FRESCO Quantum Studio - Coupled Channels Calculations")
        self.setGeometry(100, 100, 1600, 900)

        # Apply modern styling (default: light theme, change to "dark" for dark theme)
        apply_modern_style(self)

        # Create central widget with splitter layout FIRST
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter (horizontal)
        splitter = QSplitter(Qt.Horizontal)

        # Left panel: Input editor
        self.input_panel = InputPanel()
        splitter.addWidget(self.input_panel)

        # Right panel: Tabs for plotting and output
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.right_tabs = QTabWidget()
        self.right_tabs.setDocumentMode(True)

        # Plot tab
        self.plot_widget = PlotWidget()
        self.right_tabs.addTab(self.plot_widget, "Plot")

        # Log tab
        self.log_widget = LogWidget()
        self.right_tabs.addTab(self.log_widget, "Output Log")

        right_layout.addWidget(self.right_tabs)
        splitter.addWidget(right_widget)

        # Set initial splitter sizes (40% input, 60% output/plot)
        splitter.setSizes([640, 960])

        main_layout.addWidget(splitter)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # NOW create menu bar and toolbar (after widgets exist)
        self.create_menus()
        self.create_toolbar()

    def create_menus(self):
        """Create menu bar with all menu items"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_file)
        file_menu.addAction(self.save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        self.run_action = QAction("&Run FRESCO", self)
        self.run_action.setShortcut("Ctrl+R")
        self.run_action.triggered.connect(self.run_fresco)
        run_menu.addAction(self.run_action)

        self.stop_action = QAction("&Stop", self)
        self.stop_action.setShortcut("Ctrl+.")
        self.stop_action.setEnabled(False)
        self.stop_action.triggered.connect(self.stop_fresco)
        run_menu.addAction(self.stop_action)

        run_menu.addSeparator()

        clear_log_action = QAction("&Clear Log", self)
        clear_log_action.triggered.connect(self.log_widget.clear)
        run_menu.addAction(clear_log_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        theme_menu = view_menu.addMenu("&Theme")

        light_theme_action = QAction("&Light", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_theme_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(self.show_docs)
        help_menu.addAction(docs_action)

    def create_toolbar(self):
        """Create toolbar with quick action buttons"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New file
        new_btn = QAction("New", self)
        new_btn.setToolTip("Create new input file (Ctrl+N)")
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)

        # Open file
        open_btn = QAction("Open", self)
        open_btn.setToolTip("Open input file (Ctrl+O)")
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)

        # Save file
        save_btn = QAction("Save", self)
        save_btn.setToolTip("Save input file (Ctrl+S)")
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        # Run FRESCO - Create as QToolButton with custom styling
        run_tool_btn = QToolButton()
        run_tool_btn.setText("Run")
        run_tool_btn.setToolTip("Run FRESCO calculation (Ctrl+R)")
        run_tool_btn.setObjectName("runButton")
        run_tool_btn.clicked.connect(self.run_fresco)
        toolbar.addWidget(run_tool_btn)
        self.run_btn_widget = run_tool_btn

        # Stop FRESCO - Create as QToolButton with custom styling
        stop_tool_btn = QToolButton()
        stop_tool_btn.setText("Stop")
        stop_tool_btn.setToolTip("Stop running calculation (Ctrl+.)")
        stop_tool_btn.setObjectName("stopButton")
        stop_tool_btn.setEnabled(False)
        stop_tool_btn.clicked.connect(self.stop_fresco)
        toolbar.addWidget(stop_tool_btn)
        self.stop_btn_widget = stop_tool_btn

    def setup_connections(self):
        """Setup signal-slot connections"""
        self.fresco_runner.output_ready.connect(self.log_widget.append_output)
        self.fresco_runner.error_ready.connect(self.log_widget.append_error)
        self.fresco_runner.finished.connect(self.on_calculation_finished)
        self.fresco_runner.started.connect(self.on_calculation_started)

        # Setup auto-save callback
        self.input_panel.set_auto_save_callback(self.auto_save)

    def new_file(self):
        """Create a new input file"""
        reply = QMessageBox.question(
            self, "New File",
            "Clear input editor?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.input_panel.clear_input()
            self.current_file = None
            self.status_bar.showMessage("New file created")

    def open_file(self):
        """Open an existing input file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open FRESCO Input File",
            self.default_test_dir,
            "Input Files (*.in *.inp *.dat);;All Files (*)"
        )

        if file_path:
            try:
                self.input_panel.load_from_file(file_path)
                self.current_file = file_path
                # Set working directory to the directory of the input file
                self.working_directory = os.path.dirname(file_path)
                self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        """Save the current input file"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Save the input file with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save FRESCO Input File",
            self.default_test_dir,
            "Input Files (*.in);;All Files (*)"
        )

        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.working_directory = os.path.dirname(file_path)

    def save_to_file(self, file_path):
        """Save input data to a file"""
        try:
            self.input_panel.save_to_file(file_path)
            self.status_bar.showMessage(f"Saved: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def auto_save(self):
        """Auto-save current file (only if a file is already open)"""
        if self.current_file:
            try:
                self.input_panel.save_to_file(self.current_file)
                self.status_bar.showMessage(f"Auto-saved: {os.path.basename(self.current_file)}", 2000)
            except Exception as e:
                self.log_widget.append_warning(f"Auto-save failed: {str(e)}")

    def run_fresco(self):
        """Run FRESCO calculation"""
        # Check if we have an input file
        if not self.current_file:
            # Prompt to save first
            reply = QMessageBox.question(
                self, "Save Input File",
                "Please save the input file before running FRESCO.\nSave now?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.save_file_as()
                if not self.current_file:  # User canceled save
                    return
            else:
                return

        # Auto-save before running (save any modifications)
        try:
            self.input_panel.save_to_file(self.current_file)
            self.log_widget.append_info(f"Auto-saved input file before running: {os.path.basename(self.current_file)}")
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save input file:\n{str(e)}\n\nContinue running anyway?")

        # Find FRESCO executable
        exe_path, msg, found = get_executable_info("fresco", self.repo_root)
        if not found:
            QMessageBox.warning(self, "FRESCO Not Found", msg)
            return

        # Set working directory to the directory of the input file
        if self.working_directory is None:
            self.working_directory = os.path.dirname(self.current_file)

        # Clear log and start calculation
        self.log_widget.clear()
        self.log_widget.append_info(f"Starting FRESCO calculation...")
        self.log_widget.append_info(f"Executable: {exe_path}")
        self.log_widget.append_info(f"Input file: {self.current_file}")
        self.log_widget.append_info(f"Working directory: {self.working_directory}")
        self.log_widget.append_info("")

        # Switch to log tab
        self.right_tabs.setCurrentIndex(1)

        # Run FRESCO
        self.is_running_fresco = True
        self.fresco_runner.run(exe_path, self.current_file, self.working_directory)

    def stop_fresco(self):
        """Stop the running calculation"""
        self.fresco_runner.stop()
        self.log_widget.append_warning("Calculation stopped by user")

    def on_calculation_started(self):
        """Handle calculation start"""
        self.run_btn_widget.setEnabled(False)
        self.stop_btn_widget.setEnabled(True)
        self.status_bar.showMessage("Running FRESCO...")

    def on_calculation_finished(self, exit_code):
        """Handle calculation completion"""
        self.run_btn_widget.setEnabled(True)
        self.stop_btn_widget.setEnabled(False)

        if exit_code == 0:
            self.log_widget.append_success("Calculation completed successfully!")
            self.status_bar.showMessage("Calculation completed")

            # Load and display results
            self.plot_widget.load_results(self.working_directory)

            # Switch to plot tab
            self.right_tabs.setCurrentIndex(0)
        else:
            self.log_widget.append_error(f"Calculation failed with exit code {exit_code}")
            self.status_bar.showMessage(f"Calculation failed (exit code: {exit_code})")

        self.is_running_fresco = False

    def change_theme(self, theme):
        """Change the application theme"""
        apply_modern_style(self, theme)
        self.status_bar.showMessage(f"Theme changed to {theme}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
<h2>FRESCO Quantum Studio</h2>
<p><b>Version 1.0.0</b></p>
<p>Modern graphical interface for FRESCO coupled channels calculations</p>
<br>
<p><b>FRESCO</b> - Finite Range Extended Search Code<br>
for coupled reaction channels</p>
<br>
<p><b>Contact:</b> jinlei@fewbody.com</p>
<br>
<p>Built with PySide6 and matplotlib</p>
<p>© 2024 FRESCO Team</p>
"""
        QMessageBox.about(self, "About FRESCO Quantum Studio", about_text)

    def show_docs(self):
        """Show documentation link"""
        docs_text = """
<h3>FRESCO Documentation</h3>
<p>For detailed documentation, please visit the FRESCO website or see the manual in the fresco_code/man directory.</p>
<br>
<p><b>Quick Start:</b></p>
<ol>
<li>Create or load a FRESCO input file (File → Open)</li>
<li>Edit the input parameters in the editor</li>
<li>Save your input file (File → Save)</li>
<li>Run the calculation (Run → Run FRESCO)</li>
<li>View results in the Plot tab</li>
</ol>
<br>
<p><b>Contact:</b> jinlei@fewbody.com for support</p>
"""
        QMessageBox.information(self, "Documentation", docs_text)

    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_running_fresco:
            reply = QMessageBox.question(
                self, "Calculation Running",
                "A calculation is currently running. Stop and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.fresco_runner.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
