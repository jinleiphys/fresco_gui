"""
Review Step for FRESCO Studio Wizard

Final step: Review and generate FRESCO input.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QFrame, QGridLayout, QGroupBox, QPushButton, QSplitter,
    QScrollArea
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont

from wizard_step_widget import WizardStepWidget, ValidationMessage
from reaction_parser import ReactionType


class ReviewStep(WizardStepWidget):
    """
    Final Step: Review and Generate.

    Display a summary of all wizard settings and
    preview the generated FRESCO input file.
    """

    # Signal emitted when user wants to generate input
    generate_requested = Signal()

    def __init__(self):
        super().__init__(
            step_id="review",
            title="Review & Generate",
            description="Review your configuration and generate the FRESCO input file. "
                        "You can go back to any step to make changes."
        )
        self.wizard_data = {}

    def init_step_ui(self):
        """Initialize the step UI"""
        # Main splitter for summary and preview
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Configuration summary
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setContentsMargins(0, 0, 8, 0)

        summary_title = QLabel("Configuration Summary")
        summary_title.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #374151;
            padding-bottom: 8px;
        """)
        summary_layout.addWidget(summary_title)

        # Scrollable summary content
        summary_scroll = QScrollArea()
        summary_scroll.setWidgetResizable(True)
        summary_scroll.setFrameShape(QScrollArea.NoFrame)

        self.summary_content = QWidget()
        self.summary_layout = QVBoxLayout(self.summary_content)
        self.summary_layout.setSpacing(12)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)

        # Placeholder sections
        self._create_summary_sections()

        self.summary_layout.addStretch()
        summary_scroll.setWidget(self.summary_content)
        summary_layout.addWidget(summary_scroll, 1)

        splitter.addWidget(summary_widget)

        # Right side: Input preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(8, 0, 0, 0)

        preview_title = QLabel("Generated Input Preview")
        preview_title.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #374151;
            padding-bottom: 8px;
        """)
        preview_layout.addWidget(preview_title)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Monaco", 11))
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        preview_layout.addWidget(self.preview_text, 1)

        # Copy button
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
            }
        """)
        copy_btn.clicked.connect(self._copy_to_clipboard)
        preview_layout.addWidget(copy_btn)

        splitter.addWidget(preview_widget)

        # Set splitter sizes
        splitter.setSizes([400, 500])

        self.content_layout.addWidget(splitter, 1)

        # Validation summary at bottom
        self.validation_summary = QLabel("")
        self.validation_summary.setWordWrap(True)
        self.validation_summary.setStyleSheet("""
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
        """)
        self.content_layout.addWidget(self.validation_summary)

    def _create_summary_sections(self):
        """Create summary section placeholders"""
        # Reaction summary
        self.reaction_summary = self._create_summary_card("Reaction")
        self.summary_layout.addWidget(self.reaction_summary)

        # Particles summary
        self.particles_summary = self._create_summary_card("Particles")
        self.summary_layout.addWidget(self.particles_summary)

        # Potentials summary
        self.potentials_summary = self._create_summary_card("Optical Potentials")
        self.summary_layout.addWidget(self.potentials_summary)

        # Additional section (states/couplings for inelastic, overlap for transfer)
        self.additional_summary = self._create_summary_card("Additional Configuration")
        self.additional_summary.hide()
        self.summary_layout.addWidget(self.additional_summary)

    def _create_summary_card(self, title: str) -> QGroupBox:
        """Create a summary card widget"""
        card = QGroupBox(title)
        card.setStyleSheet("""
            QGroupBox {
                font-weight: 600;
                font-size: 13px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                padding-top: 20px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                background-color: white;
                color: #374151;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(4)

        # Content label
        content = QLabel("-")
        content.setWordWrap(True)
        content.setStyleSheet("color: #4b5563; font-size: 12px; font-weight: normal;")
        content.setObjectName("content")
        layout.addWidget(content)

        return card

    def _update_summary_card(self, card: QGroupBox, content: str):
        """Update a summary card's content"""
        label = card.findChild(QLabel, "content")
        if label:
            label.setText(content)

    def set_wizard_data(self, data: dict):
        """Update with complete wizard data"""
        self.wizard_data = data
        self._update_summary()
        self._update_preview()
        self.run_validation()

    def _update_summary(self):
        """Update summary display"""
        data = self.wizard_data

        # Reaction summary
        reaction_text = []
        if 'reaction_input' in data:
            rd = data['reaction_input']
            reaction_text.append(f"<b>Equation:</b> {rd.get('equation', '-')}")
            reaction_text.append(f"<b>Type:</b> {rd.get('reaction_type', '-')}")
            reaction_text.append(f"<b>Energy:</b> {rd.get('energy', 0):.2f} MeV")
            if rd.get('q_value') is not None:
                reaction_text.append(f"<b>Q-value:</b> {rd['q_value']:.3f} MeV")
        self._update_summary_card(self.reaction_summary, "<br>".join(reaction_text) or "-")

        # Particles summary
        particles_text = []
        if 'particle_config' in data:
            pd = data['particle_config']
            if 'projectile' in pd:
                p = pd['projectile']
                particles_text.append(
                    f"<b>Projectile:</b> {p.get('name', '-')} "
                    f"(A={p.get('mass_number', 0)}, Z={p.get('atomic_number', 0)})"
                )
            if 'target' in pd:
                t = pd['target']
                particles_text.append(
                    f"<b>Target:</b> {t.get('name', '-')} "
                    f"(A={t.get('mass_number', 0)}, Z={t.get('atomic_number', 0)})"
                )
        if 'exit_channel' in data:
            ed = data['exit_channel']
            if 'ejectile' in ed:
                e = ed['ejectile']
                particles_text.append(
                    f"<b>Ejectile:</b> {e.get('name', '-')} "
                    f"(A={e.get('mass_number', 0)}, Z={e.get('atomic_number', 0)})"
                )
            if 'residual' in ed:
                r = ed['residual']
                particles_text.append(
                    f"<b>Residual:</b> {r.get('name', '-')} "
                    f"(A={r.get('mass_number', 0)}, Z={r.get('atomic_number', 0)})"
                )
        self._update_summary_card(self.particles_summary, "<br>".join(particles_text) or "-")

        # Potentials summary
        pot_text = []
        if 'potential_setup' in data:
            pots = data['potential_setup'].get('potentials', [])
            type_names = {0: 'Coulomb', 1: 'Volume', 2: 'Surface', 3: 'Spin-Orbit'}
            for pot in pots:
                ptype = pot.get('type', -1)
                tname = type_names.get(ptype, f'Type {ptype}')
                pot_text.append(f"• {tname}")
        self._update_summary_card(self.potentials_summary, "<br>".join(pot_text) or "None configured")

        # Additional configuration
        add_text = []
        if 'states' in data:
            states = data['states'].get('states', [])
            add_text.append(f"<b>States:</b> {len(states)} defined")
        if 'coupling' in data:
            couplings = data['coupling'].get('couplings', [])
            add_text.append(f"<b>Couplings:</b> {len(couplings)} defined")
        if 'transferred_particle' in data:
            tp = data['transferred_particle']
            add_text.append(
                f"<b>Transferred:</b> A={tp.get('transferred_a', 0)}, "
                f"Z={tp.get('transferred_z', 0)}"
            )
        if 'overlap' in data:
            ol = data['overlap']
            proj_be = ol.get('projectile_overlap', {}).get('binding_energy', 0)
            targ_be = ol.get('target_overlap', {}).get('binding_energy', 0)
            add_text.append(f"<b>Binding:</b> {proj_be:.3f} / {targ_be:.3f} MeV")

        if add_text:
            self.additional_summary.show()
            self._update_summary_card(self.additional_summary, "<br>".join(add_text))
        else:
            self.additional_summary.hide()

    def _update_preview(self):
        """Update the input preview"""
        # This will be replaced by actual input generation
        preview = self._generate_input_preview()
        self.preview_text.setPlainText(preview)

    def _generate_input_preview(self) -> str:
        """Generate FRESCO input preview from wizard data"""
        lines = []
        data = self.wizard_data

        # Header comment
        lines.append("! FRESCO input generated by FRESCO Studio Wizard")
        lines.append("")

        # Get reaction data
        rd = data.get('reaction_input', {})
        equation = rd.get('equation', '')
        energy = rd.get('energy', 10.0)
        reaction_type = rd.get('reaction_type')

        lines.append(f"! Reaction: {equation} @ {energy:.2f} MeV")
        lines.append("")

        # FRESCO namelist
        lines.append("&FRESCO")
        lines.append(f"  hcm=0.1 rmatch=30.0")
        lines.append(f"  jtmax=50 absend=0.001")
        lines.append(f"  thmin=0.0 thmax=180.0 thinc=1.0")

        if reaction_type == ReactionType.TRANSFER:
            lines.append("  it0=1")
        else:
            lines.append("  it0=0")

        lines.append("/")
        lines.append("")

        # Partition (entrance channel)
        pd = data.get('particle_config', {})
        proj = pd.get('projectile', {})
        targ = pd.get('target', {})

        lines.append("&PARTITION")
        lines.append(f"  namep='{proj.get('name', 'proj')}'")
        lines.append(f"  massp={proj.get('mass', 1.0):.6f}")
        lines.append(f"  zp={proj.get('atomic_number', 1)}")
        lines.append(f"  namet='{targ.get('name', 'target')}'")
        lines.append(f"  masst={targ.get('mass', 10.0):.6f}")
        lines.append(f"  zt={targ.get('atomic_number', 5)}")
        lines.append(f"  qval=0.0")
        lines.append(f"  nex=1")
        lines.append("/")
        lines.append("")

        # States
        lines.append("&STATES")
        lines.append(f"  jp={proj.get('spin', 0.0)}")
        lines.append(f"  bandp=1 ep=0.0")
        lines.append(f"  jt={targ.get('spin', 0.0)}")
        lines.append(f"  bandt=1 et=0.0")
        lines.append(f"  cpot=1")
        lines.append("/")
        lines.append("")

        # Potentials
        pot_data = data.get('potential_setup', {})
        pots = pot_data.get('potentials', [])

        for i, pot in enumerate(pots, 1):
            pot_type = pot.get('type', 1)
            lines.append("&POT")
            lines.append(f"  kp=1 type={pot_type}")

            if pot_type == 0:  # Coulomb
                rc = pot.get('rc', 1.25)
                ap = proj.get('mass_number', 1)
                at = targ.get('mass_number', 10)
                lines.append(f"  p1={ap} p2={at} p3={rc}")
            elif pot_type == 1:  # Volume
                v = pot.get('V', 50.0)
                r0 = pot.get('r0', 1.17)
                a = pot.get('a', 0.75)
                w = pot.get('W', 10.0)
                rw = pot.get('rW', 1.32)
                aw = pot.get('aW', 0.52)
                lines.append(f"  p1={v:.2f} p2={r0:.2f} p3={a:.2f}")
                lines.append(f"  p4={w:.2f} p5={rw:.2f} p6={aw:.2f}")
            elif pot_type == 2:  # Surface
                vd = pot.get('Vd', 0.0)
                r0d = pot.get('r0d', 1.32)
                ad = pot.get('ad', 0.52)
                wd = pot.get('Wd', 10.0)
                rwd = pot.get('rWd', 1.32)
                awd = pot.get('aWd', 0.52)
                lines.append(f"  p1={vd:.2f} p2={r0d:.2f} p3={ad:.2f}")
                lines.append(f"  p4={wd:.2f} p5={rwd:.2f} p6={awd:.2f}")
            elif pot_type == 3:  # Spin-orbit
                vso = pot.get('Vso', 6.0)
                rso = pot.get('rso', 1.01)
                aso = pot.get('aso', 0.75)
                lines.append(f"  p1={vso:.2f} p2={rso:.2f} p3={aso:.2f}")

            lines.append("/")
            lines.append("")

        # Transfer-specific: exit channel partition
        if reaction_type == ReactionType.TRANSFER:
            ed = data.get('exit_channel', {})
            eject = ed.get('ejectile', {})
            resid = ed.get('residual', {})
            qval = rd.get('q_value', 0.0)

            lines.append("&PARTITION")
            lines.append(f"  namep='{eject.get('name', 'eject')}'")
            lines.append(f"  massp={eject.get('mass', 1.0):.6f}")
            lines.append(f"  zp={eject.get('atomic_number', 1)}")
            lines.append(f"  namet='{resid.get('name', 'resid')}'")
            lines.append(f"  masst={resid.get('mass', 10.0):.6f}")
            lines.append(f"  zt={resid.get('atomic_number', 5)}")
            lines.append(f"  qval={qval:.3f}")
            lines.append(f"  nex=1")
            lines.append("/")
            lines.append("")

            lines.append("&STATES")
            lines.append(f"  jp={eject.get('spin', 0.0)}")
            lines.append(f"  bandp=1 ep=0.0")
            lines.append(f"  jt={resid.get('spin', 0.0)}")
            lines.append(f"  bandt=1 et={ed.get('residual_excitation', 0.0):.3f}")
            lines.append(f"  cpot=2")
            lines.append("/")
            lines.append("")

            # Exit channel potentials (placeholder)
            lines.append("! Exit channel potentials")
            lines.append("&POT kp=2 type=0 p1=1 p2=1 p3=1.25 /")
            lines.append("&POT kp=2 type=1 p1=50.0 p2=1.17 p3=0.75 p4=10.0 p5=1.32 p6=0.52 /")
            lines.append("")

            # Overlap
            ol = data.get('overlap', {})
            tp = data.get('transferred_particle', {})

            lines.append("! Overlap functions")
            lines.append("&OVERLAP")
            lines.append(f"  kn1=1 ic1=1 ic2=2 in=1 kind=0")
            lines.append(f"  nn={tp.get('projectile_quantum', {}).get('n', 0)}")
            lines.append(f"  l={tp.get('projectile_quantum', {}).get('l', 0)}")
            lines.append(f"  sn=0.5 j={tp.get('projectile_quantum', {}).get('j2', 1)/2.0}")
            lines.append(f"  be={ol.get('projectile_overlap', {}).get('binding_energy', 2.225):.3f}")
            lines.append("/")
            lines.append("")

            lines.append("&OVERLAP")
            lines.append(f"  kn1=2 ic1=2 ic2=1 in=-1 kind=0")
            lines.append(f"  nn={tp.get('target_quantum', {}).get('n', 1)}")
            lines.append(f"  l={tp.get('target_quantum', {}).get('l', 2)}")
            lines.append(f"  sn=0.5 j={tp.get('target_quantum', {}).get('j2', 5)/2.0}")
            lines.append(f"  be={ol.get('target_overlap', {}).get('binding_energy', 10.0):.3f}")
            lines.append("/")
            lines.append("")

        # Lab energy
        lines.append(f"&DATA")
        lines.append(f"  lab={energy:.3f}")
        lines.append("/")
        lines.append("")

        return "\n".join(lines)

    def _copy_to_clipboard(self):
        """Copy preview to clipboard"""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.preview_text.toPlainText())

    def get_generated_input(self) -> str:
        """Get the generated FRESCO input text"""
        return self.preview_text.toPlainText()

    def get_data(self):
        """Get current step data"""
        from wizard_step_widget import StepData

        return StepData(
            values={
                'generated_input': self.preview_text.toPlainText()
            },
            is_valid=self._is_completed,
            validation_messages=self._validation_messages
        )

    def set_data(self, data: dict):
        """Set step data"""
        pass  # Review step doesn't accept external data

    def validate(self):
        """Validate current step"""
        messages = []

        # Check if we have minimum required data
        if not self.wizard_data:
            messages.append(ValidationMessage(
                level='error',
                message='No configuration data available'
            ))
            return messages

        if 'reaction_input' not in self.wizard_data:
            messages.append(ValidationMessage(
                level='error',
                message='Reaction not configured'
            ))

        if 'particle_config' not in self.wizard_data:
            messages.append(ValidationMessage(
                level='error',
                message='Particles not configured'
            ))

        if 'potential_setup' not in self.wizard_data:
            messages.append(ValidationMessage(
                level='warning',
                message='No optical potentials configured'
            ))

        # Update validation summary display
        if any(m.level == 'error' for m in messages):
            self.validation_summary.setText(
                "⚠️ Configuration incomplete. Please review previous steps."
            )
            self.validation_summary.setStyleSheet("""
                padding: 12px;
                border-radius: 4px;
                font-size: 13px;
                background-color: #fef2f2;
                color: #991b1b;
                border: 1px solid #fecaca;
            """)
        else:
            self.validation_summary.setText(
                "✓ Configuration complete. Ready to generate FRESCO input."
            )
            self.validation_summary.setStyleSheet("""
                padding: 12px;
                border-radius: 4px;
                font-size: 13px;
                background-color: #d1fae5;
                color: #065f46;
                border: 1px solid #a7f3d0;
            """)

            messages.append(ValidationMessage(
                level='success',
                message='Ready to generate FRESCO input'
            ))

        return messages
