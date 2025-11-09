"""
Widget for managing OVERLAP namelists in FRESCO calculations

Handles both one-particle (KIND 0-4) and two-particle (KIND 6-9) form factors
according to FRESCO manual section 3.5
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QSpinBox, QDoubleSpinBox, QLabel, QComboBox,
    QScrollArea, QLineEdit, QCheckBox
)
from PySide6.QtCore import Qt, Signal


class SingleOverlapWidget(QWidget):
    """Widget for a single OVERLAP namelist configuration"""

    removed = Signal(object)  # Signal emitted when this overlap should be removed

    def __init__(self, overlap_index=1):
        super().__init__()
        self.overlap_index = overlap_index
        self.init_ui()

    def init_ui(self):
        """Initialize single overlap widget"""
        # Create collapsible group box
        self.group_box = QGroupBox(f"Overlap #{self.overlap_index}")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(True)  # Start expanded

        layout = QVBoxLayout(self.group_box)

        # Use a form layout
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # Basic identification parameters
        basic_label = QLabel("<b>Basic Parameters:</b>")
        form_layout.addRow(basic_label)

        self.kn1 = QSpinBox()
        self.kn1.setRange(1, 99)
        self.kn1.setValue(1)
        self.kn1.setToolTip("Form factor index (or start of range for two-particle)")
        form_layout.addRow("KN1:", self.kn1)

        self.kn2 = QSpinBox()
        self.kn2.setRange(0, 99)
        self.kn2.setValue(0)
        self.kn2.setToolTip("End of range for two-particle (0 for one-particle)")
        form_layout.addRow("KN2:", self.kn2)

        self.ic1 = QSpinBox()
        self.ic1.setRange(1, 9)
        self.ic1.setValue(1)
        self.ic1.setToolTip("Core partition number")
        form_layout.addRow("IC1:", self.ic1)

        self.ic2 = QSpinBox()
        self.ic2.setRange(1, 9)
        self.ic2.setValue(2)
        self.ic2.setToolTip("Composite partition number")
        form_layout.addRow("IC2:", self.ic2)

        self.in_param = QSpinBox()
        self.in_param.setRange(-2, 2)
        self.in_param.setValue(1)
        self.in_param.setToolTip("1=projectile, 2=target, <0 for relativistic correction")
        form_layout.addRow("IN:", self.in_param)

        # KIND selector
        self.kind = QComboBox()
        self.kind.addItems([
            "0 - (L,S)J coupling (typical transfer)",
            "1 - LS coupling",
            "2 - Eigenstate in deformed potential",
            "3 - Coupled core+(ls)j",
            "4 - Dalitz-Thacker Triton",
            "6 - Two-particle: (Lnn,(l,S12)j12)J12",
            "7 - Two-particle: ((Lnn,l)Lt,(S12,Jcore)St)Jcom",
            "9 - Two-particle: (Lnn,(l,S12)j12)J12,Jcore,Jcom"
        ])
        self.kind.setCurrentIndex(0)
        self.kind.currentIndexChanged.connect(self.on_kind_changed)
        form_layout.addRow("KIND:", self.kind)

        form_layout.addRow(QLabel(""))  # Spacer

        # One-particle parameters
        self.one_particle_label = QLabel("<b>One-Particle Parameters:</b>")
        form_layout.addRow(self.one_particle_label)

        self.ch1 = QLineEdit("A")
        self.ch1.setMaxLength(1)
        self.ch1.setToolTip("Single-character identifier (A-M for +parity, N-Z for -parity)")
        form_layout.addRow("CH1:", self.ch1)

        self.nn = QSpinBox()
        self.nn.setRange(0, 20)
        self.nn.setValue(1)
        self.nn.setToolTip("Number of nodes (one-particle) or NPAIRS (two-particle)")
        form_layout.addRow("NN/NPAIRS:", self.nn)

        self.l = QSpinBox()
        self.l.setRange(0, 20)
        self.l.setValue(0)
        self.l.setToolTip("L=LN angular momentum (one-particle) or lmin (two-particle)")
        form_layout.addRow("L/lmin:", self.l)

        self.lmax = QSpinBox()
        self.lmax.setRange(0, 20)
        self.lmax.setValue(0)
        self.lmax.setToolTip("Maximum L (one-particle) or lmax (two-particle)")
        form_layout.addRow("LMAX/lmax:", self.lmax)

        self.sn = QDoubleSpinBox()
        self.sn.setRange(0.0, 10.0)
        self.sn.setSingleStep(0.5)
        self.sn.setValue(0.5)
        self.sn.setToolTip("Intrinsic spin (one-particle) or Smin (two-particle)")
        form_layout.addRow("SN/Smin:", self.sn)

        self.ia = QSpinBox()
        self.ia.setRange(0, 99)
        self.ia.setValue(1)
        self.ia.setToolTip("Index of core state (0 = specify later)")
        form_layout.addRow("IA:", self.ia)

        self.jn = QDoubleSpinBox()
        self.jn.setRange(0.0, 20.0)
        self.jn.setSingleStep(0.5)
        self.jn.setValue(0.5)
        self.jn.setToolTip("Vector sum L+S (one-particle) or J12 (two-particle)")
        form_layout.addRow("JN/J12:", self.jn)

        self.ib = QSpinBox()
        self.ib.setRange(0, 99)
        self.ib.setValue(1)
        self.ib.setToolTip("Index of composite state (0 = specify later)")
        form_layout.addRow("IB:", self.ib)

        form_layout.addRow(QLabel(""))  # Spacer

        # Binding parameters
        binding_label = QLabel("<b>Binding Parameters:</b>")
        form_layout.addRow(binding_label)

        self.kbpot = QSpinBox()
        self.kbpot.setRange(1, 99)
        self.kbpot.setValue(1)
        self.kbpot.setToolTip("Binding potential index (one-particle) or T isospin (two-particle)")
        form_layout.addRow("KBPOT/T:", self.kbpot)

        self.krpot = QSpinBox()
        self.krpot.setRange(0, 99)
        self.krpot.setValue(0)
        self.krpot.setToolTip("Transfer potential index (one-particle) or KNZR (two-particle)")
        form_layout.addRow("KRPOT/KNZR:", self.krpot)

        self.be = QDoubleSpinBox()
        self.be.setRange(-50.0, 50.0)
        self.be.setDecimals(3)
        self.be.setValue(2.224)
        self.be.setToolTip("Binding energy (positive=bound) or EPS threshold (two-particle)")
        form_layout.addRow("BE/EPS:", self.be)

        self.isc = QSpinBox()
        self.isc.setRange(-2, 14)
        self.isc.setValue(0)
        self.isc.setToolTip("Scaling control for binding energy or continuum weighting")
        form_layout.addRow("ISC:", self.isc)

        form_layout.addRow(QLabel(""))  # Spacer

        # Output and spectroscopy
        output_label = QLabel("<b>Output & Spectroscopy:</b>")
        form_layout.addRow(output_label)

        self.ipc = QSpinBox()
        self.ipc.setRange(0, 4)
        self.ipc.setValue(1)
        self.ipc.setToolTip("Print control (0-4)")
        form_layout.addRow("IPC:", self.ipc)

        self.nfl = QSpinBox()
        self.nfl.setRange(-99, 99)
        self.nfl.setValue(0)
        self.nfl.setToolTip("File I/O: <0 write, >0 read, 0 no I/O")
        form_layout.addRow("NFL:", self.nfl)

        self.nam = QSpinBox()
        self.nam.setRange(-99, 99)
        self.nam.setValue(0)
        self.nam.setToolTip("Spectroscopic number (-1=use AMPL for mass)")
        form_layout.addRow("NAM:", self.nam)

        self.ampl = QDoubleSpinBox()
        self.ampl.setRange(0.0, 100.0)
        self.ampl.setDecimals(4)
        self.ampl.setValue(1.0)
        self.ampl.setToolTip("Spectroscopic amplitude (√NAM × AMPL)")
        form_layout.addRow("AMPL:", self.ampl)

        layout.addLayout(form_layout)

        # Remove button
        remove_btn = QPushButton("Remove this Overlap")
        remove_btn.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(remove_btn)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)

    def on_kind_changed(self, index):
        """Update labels and tooltips based on KIND selection"""
        kind_value = self.get_kind_value()
        is_two_particle = kind_value >= 6

        if is_two_particle:
            self.one_particle_label.setText("<b>Two-Particle Parameters:</b>")
            self.nn.setToolTip("NPAIRS: number of pair-products to sum")
            self.l.setToolTip("lmin: minimum orbital angular momentum")
            self.lmax.setToolTip("lmax: maximum orbital angular momentum")
            self.sn.setToolTip("Smin: minimum S12 (Smax=1.0 always)")
            self.jn.setToolTip("J12: total angular momentum of two-particle state")
            self.kbpot.setToolTip("T: total isospin (0 or 1)")
            self.krpot.setToolTip("KNZR: KN index for N-N relative motion")
            self.be.setToolTip("EPS: threshold percentage for omitting small components")
        else:
            self.one_particle_label.setText("<b>One-Particle Parameters:</b>")
            self.nn.setToolTip("Number of radial nodes")
            self.l.setToolTip("L=LN: angular momentum")
            self.lmax.setToolTip("Maximum L in summation")
            self.sn.setToolTip("Intrinsic spin of bound nucleon")
            self.jn.setToolTip("Vector sum L+S")
            self.kbpot.setToolTip("Binding potential index KP")
            self.krpot.setToolTip("Transfer potential index (0=use KBPOT)")
            self.be.setToolTip("Binding energy (positive for bound, negative for continuum)")

    def get_kind_value(self):
        """Get the numeric KIND value from the combo box"""
        kind_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 7, 7: 9}
        return kind_map.get(self.kind.currentIndex(), 0)

    def get_overlap_data(self):
        """Get all overlap parameters as a dictionary"""
        return {
            'kn1': self.kn1.value(),
            'kn2': self.kn2.value(),
            'ic1': self.ic1.value(),
            'ic2': self.ic2.value(),
            'in': self.in_param.value(),
            'kind': self.get_kind_value(),
            'ch1': self.ch1.text() if self.ch1.text() else 'A',
            'nn': self.nn.value(),
            'l': self.l.value(),
            'lmax': self.lmax.value(),
            'sn': self.sn.value(),
            'ia': self.ia.value(),
            'jn': self.jn.value(),
            'ib': self.ib.value(),
            'kbpot': self.kbpot.value(),
            'krpot': self.krpot.value(),
            'be': self.be.value(),
            'isc': self.isc.value(),
            'ipc': self.ipc.value(),
            'nfl': self.nfl.value(),
            'nam': self.nam.value(),
            'ampl': self.ampl.value()
        }

    def set_overlap_data(self, data):
        """Set overlap parameters from a dictionary"""
        if 'kn1' in data:
            self.kn1.setValue(data['kn1'])
        if 'kn2' in data:
            self.kn2.setValue(data['kn2'])
        if 'ic1' in data:
            self.ic1.setValue(data['ic1'])
        if 'ic2' in data:
            self.ic2.setValue(data['ic2'])
        if 'in' in data:
            self.in_param.setValue(data['in'])
        if 'kind' in data:
            # Map KIND value to combo box index
            kind_map = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 6: 5, 7: 6, 9: 7}
            self.kind.setCurrentIndex(kind_map.get(data['kind'], 0))
        if 'ch1' in data:
            self.ch1.setText(data['ch1'])
        if 'nn' in data:
            self.nn.setValue(data['nn'])
        if 'l' in data:
            self.l.setValue(data['l'])
        if 'lmax' in data:
            self.lmax.setValue(data['lmax'])
        if 'sn' in data:
            self.sn.setValue(data['sn'])
        if 'ia' in data:
            self.ia.setValue(data['ia'])
        if 'jn' in data:
            self.jn.setValue(data['jn'])
        if 'ib' in data:
            self.ib.setValue(data['ib'])
        if 'kbpot' in data:
            self.kbpot.setValue(data['kbpot'])
        if 'krpot' in data:
            self.krpot.setValue(data['krpot'])
        if 'be' in data:
            self.be.setValue(data['be'])
        if 'isc' in data:
            self.isc.setValue(data['isc'])
        if 'ipc' in data:
            self.ipc.setValue(data['ipc'])
        if 'nfl' in data:
            self.nfl.setValue(data['nfl'])
        if 'nam' in data:
            self.nam.setValue(data['nam'])
        if 'ampl' in data:
            self.ampl.setValue(data['ampl'])


class OverlapManagerWidget(QWidget):
    """Widget for managing multiple OVERLAP namelists"""

    def __init__(self):
        super().__init__()
        self.overlap_widgets = []
        self.init_ui()

    def init_ui(self):
        """Initialize the overlap manager widget"""
        # Create collapsible group box
        self.group_box = QGroupBox("Overlap Form Factors (One- and Two-Particle)")
        self.group_box.setCheckable(True)
        self.group_box.setChecked(False)  # Start collapsed

        layout = QVBoxLayout(self.group_box)

        # Info label
        info_label = QLabel(
            "Define particle-nucleus form factors for transfer reactions.\n"
            "KIND 0-4: one-particle states | KIND 6-9: two-particle states"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Scroll area for overlaps
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        scroll_widget = QWidget()
        self.overlaps_layout = QVBoxLayout(scroll_widget)
        self.overlaps_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Add overlap button
        add_btn = QPushButton("+ Add Overlap")
        add_btn.clicked.connect(self.add_overlap)
        layout.addWidget(add_btn)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.group_box)

    def add_overlap(self, overlap_data=None):
        """Add a new overlap widget"""
        overlap_index = len(self.overlap_widgets) + 1
        overlap_widget = SingleOverlapWidget(overlap_index)
        overlap_widget.removed.connect(self.remove_overlap)

        if overlap_data:
            overlap_widget.set_overlap_data(overlap_data)

        self.overlap_widgets.append(overlap_widget)
        # Insert before the stretch
        self.overlaps_layout.insertWidget(len(self.overlap_widgets) - 1, overlap_widget)

    def remove_overlap(self, overlap_widget):
        """Remove an overlap widget"""
        if overlap_widget in self.overlap_widgets:
            self.overlap_widgets.remove(overlap_widget)
            overlap_widget.setParent(None)
            overlap_widget.deleteLater()

            # Renumber remaining overlaps
            for i, widget in enumerate(self.overlap_widgets, 1):
                widget.overlap_index = i
                widget.group_box.setTitle(f"Overlap #{i}")

    def get_all_overlaps_data(self):
        """Get data from all overlap widgets"""
        return [widget.get_overlap_data() for widget in self.overlap_widgets]

    def set_all_overlaps_data(self, overlaps_list):
        """Set all overlaps from a list of dictionaries"""
        # Clear existing overlaps
        for widget in self.overlap_widgets[:]:
            self.remove_overlap(widget)

        # Add new overlaps
        for overlap_data in overlaps_list:
            self.add_overlap(overlap_data)

    def generate_overlap_namelists(self):
        """Generate &OVERLAP namelists text"""
        if not self.overlap_widgets:
            return ""

        namelists = []
        for overlap_data in self.get_all_overlaps_data():
            # Build namelist line
            params = []

            # Basic parameters
            if overlap_data['kn2'] > 0:
                params.append(f"kn1={overlap_data['kn1']}")
                params.append(f"kn2={overlap_data['kn2']}")
            else:
                params.append(f"kn1={overlap_data['kn1']}")

            params.append(f"ic1={overlap_data['ic1']}")
            params.append(f"ic2={overlap_data['ic2']}")
            params.append(f"in={overlap_data['in']}")
            params.append(f"kind={overlap_data['kind']}")

            # One/two-particle parameters
            if overlap_data['kind'] < 6:
                # One-particle
                params.append(f"ch1='{overlap_data['ch1']}'")
                params.append(f"nn={overlap_data['nn']}")
                params.append(f"l={overlap_data['l']}")
                if overlap_data['lmax'] > 0:
                    params.append(f"lmax={overlap_data['lmax']}")
                params.append(f"sn={overlap_data['sn']}")
            else:
                # Two-particle
                params.append(f"npairs={overlap_data['nn']}")
                params.append(f"lmin={overlap_data['l']}")
                params.append(f"lmax={overlap_data['lmax']}")
                params.append(f"smin={overlap_data['sn']}")

            params.append(f"ia={overlap_data['ia']}")
            params.append(f"jn={overlap_data['jn']}")
            params.append(f"ib={overlap_data['ib']}")

            # Binding parameters
            if overlap_data['kind'] < 6:
                params.append(f"kbpot={overlap_data['kbpot']}")
                if overlap_data['krpot'] > 0:
                    params.append(f"krpot={overlap_data['krpot']}")
                params.append(f"be={overlap_data['be']}")
            else:
                # Two-particle uses different names
                params.append(f"t={overlap_data['kbpot']}")
                if overlap_data['krpot'] > 0:
                    params.append(f"knzr={overlap_data['krpot']}")
                params.append(f"eps={overlap_data['be']}")

            if overlap_data['isc'] != 0:
                params.append(f"isc={overlap_data['isc']}")
            if overlap_data['ipc'] != 1:
                params.append(f"ipc={overlap_data['ipc']}")
            if overlap_data['nfl'] != 0:
                params.append(f"nfl={overlap_data['nfl']}")

            # Spectroscopic amplitude
            if overlap_data['nam'] != 0:
                params.append(f"nam={overlap_data['nam']}")
                params.append(f"ampl={overlap_data['ampl']}")

            # Create namelist
            namelist = f"&OVERLAP {' '.join(params)} /"
            namelists.append(namelist)

        return "\n".join(namelists)
