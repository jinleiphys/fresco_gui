"""
Widget for managing multiple energy definitions in FRESCO calculations

FRESCO energy scanning system:
- Single: elab=30.0 (single energy point)
- Range: elab(1:n)=E1 E2 ... En  nlab(1:n-1)=N1 N2 ... Nn-1
  where Ei are energy boundaries and Ni is number of points between Ei and Ei+1

Example: elab(1:3)=6.9 11.00 49.350  nlab(1:2)=1 1
  - Calculates 1 point between 6.9 and 11.00 MeV
  - Calculates 1 point between 11.00 and 49.35 MeV
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QDoubleSpinBox, QSpinBox, QLabel, QHeaderView
)
from PySide6.QtCore import Qt, Signal


class EnergyArrayWidget(QWidget):
    """Widget for managing energy scanning ranges in FRESCO"""

    # Signal emitted when energies change
    energies_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the energy array widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header with Add/Remove buttons
        header_layout = QHBoxLayout()
        header_label = QLabel("Energy Scanning Range:")
        header_label.setStyleSheet("font-weight: 600; color: #374151;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        add_btn = QPushButton("+ Add Boundary")
        add_btn.clicked.connect(self.add_boundary)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        header_layout.addWidget(add_btn)

        remove_btn = QPushButton("- Remove Selected")
        remove_btn.clicked.connect(self.remove_selected)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        header_layout.addWidget(remove_btn)

        layout.addLayout(header_layout)

        # Energy table: Energy boundaries and points between intervals
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Energy Boundary [MeV]", "Points to Next"])

        # Set column widths - use Interactive mode so user can resize if needed
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().resizeSection(0, 180)  # Wider for energy values
        self.table.horizontalHeader().resizeSection(1, 120)  # Points to next

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setMaximumHeight(200)  # Increased height for better visibility
        self.table.verticalHeader().setDefaultSectionSize(44)  # Taller rows to prevent clipping

        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e5e7eb;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #d1d5db;
                font-weight: 600;
                color: #374151;
            }
        """)

        layout.addWidget(self.table)

        # Start with single energy point (default for simple calculations)
        self.add_boundary(30.0, None)  # Single energy point

    def add_boundary(self, energy=30.0, points_to_next=1):
        """
        Add a new energy boundary to the table

        When adding a boundary to a table with existing boundaries:
        - The previous last boundary gets a "points to next" spinbox
        - The new boundary becomes the last one (with disabled "points to next")

        Args:
            energy: Energy boundary value in MeV
            points_to_next: Number of points between this boundary and next (None for last boundary)
        """
        # If we're adding a new boundary and there are existing rows,
        # update the previous last row to have a spinbox
        if points_to_next is None and self.table.rowCount() > 0:
            prev_last_row = self.table.rowCount() - 1
            # Replace the disabled label with a spinbox
            nlab_spin = QSpinBox()
            nlab_spin.setRange(1, 1000)
            nlab_spin.setValue(1)  # Default: 1 point to next boundary
            nlab_spin.setMinimumHeight(32)  # Ensure spinbox has enough height
            nlab_spin.valueChanged.connect(self.energies_changed.emit)
            self.table.setCellWidget(prev_last_row, 1, nlab_spin)

        row = self.table.rowCount()
        self.table.insertRow(row)

        # Energy boundary spinbox
        energy_spin = QDoubleSpinBox()
        energy_spin.setRange(0.0, 10000.0)
        energy_spin.setDecimals(3)
        energy_spin.setValue(energy)
        energy_spin.setMinimumHeight(32)  # Ensure spinbox has enough height
        energy_spin.valueChanged.connect(self.energies_changed.emit)
        self.table.setCellWidget(row, 0, energy_spin)

        # Points to next boundary (disabled for last row)
        if points_to_next is not None:
            nlab_spin = QSpinBox()
            nlab_spin.setRange(1, 1000)
            nlab_spin.setValue(points_to_next)
            nlab_spin.setMinimumHeight(32)  # Ensure spinbox has enough height
            nlab_spin.valueChanged.connect(self.energies_changed.emit)
            self.table.setCellWidget(row, 1, nlab_spin)
        else:
            # Last boundary - show disabled label
            label = QLabel("—")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #9ca3af;")
            self.table.setCellWidget(row, 1, label)

        self.energies_changed.emit()

    def remove_selected(self):
        """Remove selected rows from the table"""
        # Get selected row indexes from selection model
        selection_model = self.table.selectionModel()
        if not selection_model:
            return

        selected_indexes = selection_model.selectedRows()
        selected_rows = set(index.row() for index in selected_indexes)

        # If no rows selected, do nothing
        if not selected_rows:
            return

        # Keep at least one row (minimum one energy point)
        if len(selected_rows) >= self.table.rowCount():
            return

        # Remove rows in reverse order to maintain indices
        for row in sorted(selected_rows, reverse=True):
            self.table.removeRow(row)

        # Update last row to have no "points to next"
        self._update_last_row()
        self.energies_changed.emit()

    def _update_last_row(self):
        """Update the last row to disable 'points to next' spinbox"""
        if self.table.rowCount() == 0:
            return

        last_row = self.table.rowCount() - 1
        # Replace spinbox with disabled label
        label = QLabel("—")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #9ca3af;")
        self.table.setCellWidget(last_row, 1, label)

    def get_boundaries_and_intervals(self):
        """
        Get energy boundaries and interval point counts

        Returns:
            Tuple of (boundaries, intervals) where:
            - boundaries: List of energy values
            - intervals: List of point counts (length = len(boundaries) - 1)
        """
        boundaries = []
        intervals = []

        for row in range(self.table.rowCount()):
            energy_widget = self.table.cellWidget(row, 0)
            if energy_widget:
                boundaries.append(energy_widget.value())

                # Get nlab for this interval (if not last row)
                if row < self.table.rowCount() - 1:
                    nlab_widget = self.table.cellWidget(row, 1)
                    if isinstance(nlab_widget, QSpinBox):
                        intervals.append(nlab_widget.value())

        return boundaries, intervals

    def set_boundaries_and_intervals(self, boundaries, intervals):
        """
        Set energy boundaries and interval point counts

        Args:
            boundaries: List of energy values
            intervals: List of point counts (should have len(boundaries)-1 elements)
        """
        # Clear existing rows
        self.table.setRowCount(0)

        # Add boundaries
        if not boundaries:
            boundaries = [30.0]  # Single energy point by default
            intervals = []

        # Ensure intervals has correct length
        while len(intervals) < len(boundaries) - 1:
            intervals.append(1)

        for i, energy in enumerate(boundaries):
            if i < len(boundaries) - 1:
                # Not last boundary - has points to next
                points = intervals[i] if i < len(intervals) else 1
                self.add_boundary(energy, points)
            else:
                # Last boundary - no points to next
                self.add_boundary(energy, None)

    def get_fresco_format(self):
        """
        Generate FRESCO namelist format string for elab/nlab

        Returns:
            String in format "elab(1:n)=E1 E2 ... En  nlab(1:m)=N1 N2 ... Nm"
            where n = number of boundaries, m = number of intervals = n-1
        """
        boundaries, intervals = self.get_boundaries_and_intervals()

        if len(boundaries) == 0:
            return "elab=30.0"

        if len(boundaries) == 1:
            # Single energy point - simple format
            return f"elab={boundaries[0]:.3f}"

        # Multiple boundaries - array format
        # Format energy values: use integer format for 0, otherwise use 3 decimals
        elab_values = " ".join(f"{int(e)}" if e == 0 else f"{e:.3f}" for e in boundaries)
        nlab_values = " ".join(str(n) for n in intervals)
        n_boundaries = len(boundaries)
        n_intervals = len(intervals)

        return f"elab(1:{n_boundaries})={elab_values}  nlab(1:{n_intervals})={nlab_values}"

    def parse_fresco_format(self, input_text):
        """
        Parse FRESCO input text to extract elab/nlab values

        Supports:
        - Single: elab=30.0
        - Array: elab(1:n)=E1 E2 ... En  nlab(1:m)=N1 N2 ... Nm

        Args:
            input_text: FRESCO input file content
        """
        import re

        boundaries = []
        intervals = []

        # Find &FRESCO namelist
        fresco_pattern = r'&FRESCO\s+(.*?)\s*/'
        match = re.search(fresco_pattern, input_text, re.DOTALL | re.IGNORECASE)

        if not match:
            return

        namelist_content = match.group(1)

        # Try array format first: elab(1:n)=val1 val2 val3
        elab_array_pattern = r'elab\s*\(\s*1\s*:\s*(\d+)\s*\)\s*=\s*([\d\.\s]+)'
        elab_match = re.search(elab_array_pattern, namelist_content, re.IGNORECASE)

        if elab_match:
            # Array format found - parse energy boundaries
            n = int(elab_match.group(1))
            boundaries = [float(x) for x in elab_match.group(2).split()]

            # Try to find nlab array - intervals between boundaries
            nlab_array_pattern = r'nlab\s*\(\s*1\s*:\s*\d+\s*\)\s*=\s*([\d\s]+)'
            nlab_match = re.search(nlab_array_pattern, namelist_content, re.IGNORECASE)

            if nlab_match:
                intervals = [int(x) for x in nlab_match.group(1).split()]
            else:
                # Default: 1 point per interval
                intervals = [1] * (len(boundaries) - 1)

            # Pad intervals if needed (should have n-1 intervals for n boundaries)
            while len(intervals) < len(boundaries) - 1:
                intervals.append(1)

        else:
            # Try single value format: elab=30.0
            elab_single_pattern = r'elab\s*=\s*([\d\.]+)'
            elab_match = re.search(elab_single_pattern, namelist_content, re.IGNORECASE)

            if elab_match:
                # Single energy point
                boundaries = [float(elab_match.group(1))]
                intervals = []

        # Update widget if we found energies
        if boundaries:
            self.set_boundaries_and_intervals(boundaries, intervals)
