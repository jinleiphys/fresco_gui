"""
POT (Potential) Namelist Manager for FRESCO
Manages optical potential parameters for FRESCO calculations
"""


class PotParameter:
    """Represents a single POT namelist parameter"""

    def __init__(self, name, label, tooltip, param_type="number",
                 default=None, minimum=None, maximum=None, step=None,
                 options=None, category="basic"):
        self.name = name
        self.label = label
        self.tooltip = tooltip
        self.param_type = param_type  # "number", "text", "select", "checkbox"
        self.default = default
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.options = options  # For "select" type: list of (value, display_text) tuples
        self.category = category


class PotNamelist:
    """Manages all POT namelist parameters for FRESCO"""

    # Category definitions with icons
    categories = {
        "basic": {"title": "Basic", "icon": "🔧"},
        "type0": {"title": "Coulomb (TYPE=0)", "icon": "⚡"},
        "volume": {"title": "Volume Potential (TYPE=1)", "icon": "🌊"},
        "surface": {"title": "Surface Potential (TYPE=2)", "icon": "📊"},
        "spinorbit": {"title": "Spin-Orbit (TYPE=3,4)", "icon": "🌀"},
        "tensor": {"title": "Tensor Forces (TYPE=5-8)", "icon": "📐"},
        "deformation": {"title": "Deformation (TYPE=10-17)", "icon": "🔮"},
        "advanced": {"title": "Advanced Options", "icon": "⚙️"},
    }

    # Basic parameters that are shown in the main form
    BASIC_PARAMETERS = ['kp', 'type', 'shape']

    def __init__(self):
        self.parameters = {}
        self._define_parameters()

    def _define_parameters(self):
        """Define all POT namelist parameters"""
        params = self.parameters

        # ========== Basic Parameters ==========
        params["kp"] = PotParameter(
            "kp", "Partition number (kp)",
            "Partition index to which this potential applies (1,2,3,...). "
            "Multiple POT namelists can have the same kp to build up the potential.",
            default=1, step=1, minimum=1, maximum=20, category="basic"
        )

        params["type"] = PotParameter(
            "type", "Potential type (type)",
            "Type of potential component:\n"
            "0 = Coulomb potential (defines radii)\n"
            "1 = Central volume potential\n"
            "2 = Central surface (derivative) potential\n"
            "3 = Spin-orbit for projectile\n"
            "4 = Spin-orbit for target\n"
            "5 = Tr tensor force for projectile\n"
            "6 = Tr tensor force for target\n"
            "7 = Tensor force between L and combined spins\n"
            "8 = Spin-spin force\n"
            "9 = Effective mass reduction\n"
            "10-17 = Deformation and coupling potentials",
            param_type="select",
            options=[
                (0, "0: Coulomb"),
                (1, "1: Volume"),
                (2, "2: Surface"),
                (3, "3: Spin-orbit (projectile)"),
                (4, "4: Spin-orbit (target)"),
                (8, "8: Deformation"),
            ],
            default=0, category="basic"
        )

        params["shape"] = PotParameter(
            "shape", "Radial shape (shape)",
            "Radial form factor shape:\n"
            "0 = Woods-Saxon\n"
            "1 = Woods-Saxon squared\n"
            "2 = Gaussian\n"
            "3 = Yukawa\n"
            "4 = Exponential\n"
            "5,6 = Reid soft core\n"
            "7,8,9 = Read from external file\n"
            "-1 = Fourier-Bessel\n"
            "10-19 = Write potential to file\n"
            "20-29 = Read J/π-dependent potential\n"
            "30+ = Add L/J-dependent factor",
            param_type="select",
            options=[
                (0, "0: Woods-Saxon"),
                (1, "1: WS Squared"),
                (2, "2: Gaussian"),
                (3, "3: Yukawa"),
                (4, "4: Exponential"),
                (-1, "-1: Fourier-Bessel"),
            ],
            default=0, category="basic"
        )

        params["it"] = PotParameter(
            "it", "Iteration flag (it)",
            "Controls iterative treatment:\n"
            "1 or 3: Include only iteratively\n"
            "2 or 3: Do NOT subtract in KIND=3,4 single-particle couplings",
            default=0, step=1, minimum=0, maximum=3, category="basic"
        )

        # ========== TYPE=0 (Coulomb) Parameters ==========
        params["at"] = PotParameter(
            "at", "Target mass (at)",
            "Target mass number A_t (or p1 for type=0). "
            "Used to calculate radius scaling: CC = A_t^(1/3) + A_p^(1/3)",
            default=12.0, step=0.1, minimum=0.0, maximum=300.0, category="type0"
        )

        params["ap"] = PotParameter(
            "ap", "Projectile mass (ap)",
            "Projectile mass number A_p (or p2 for type=0). "
            "Used to calculate radius scaling: CC = A_t^(1/3) + A_p^(1/3)",
            default=4.0, step=0.1, minimum=0.0, maximum=300.0, category="type0"
        )

        params["rc"] = PotParameter(
            "rc", "Coulomb radius (rc)",
            "Coulomb radius parameter r_c (p3 for type=0, in fm). "
            "Actual radius = rc * CC where CC = A_t^(1/3) + A_p^(1/3)",
            default=1.3, step=0.01, minimum=0.0, maximum=5.0, category="type0"
        )

        params["ac"] = PotParameter(
            "ac", "Coulomb diffuseness (ac)",
            "Coulomb diffuseness parameter a_c (p4 for type=0, in fm)",
            default=0.0, step=0.01, minimum=0.0, maximum=2.0, category="type0"
        )

        # ========== Volume/Surface Potential Parameters (TYPE=1,2) ==========
        # Real part
        params["p1"] = PotParameter(
            "p1", "Real depth V (p1)",
            "Depth of real potential (MeV). Negative for attractive potential.",
            default=50.0, step=1.0, minimum=-500.0, maximum=500.0, category="volume"
        )

        params["p2"] = PotParameter(
            "p2", "Real radius r0 (p2)",
            "Radius parameter r_0 for real potential (fm). "
            "Actual radius R = p2 * CC",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="volume"
        )

        params["p3"] = PotParameter(
            "p3", "Real diffuseness a (p3)",
            "Diffuseness parameter a for real potential (fm)",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="volume"
        )

        # Imaginary part
        params["p4"] = PotParameter(
            "p4", "Imaginary depth W (p4)",
            "Depth of imaginary potential (MeV). Negative for absorption.",
            default=0.0, step=1.0, minimum=-500.0, maximum=500.0, category="volume"
        )

        params["p5"] = PotParameter(
            "p5", "Imaginary radius r0W (p5)",
            "Radius parameter r_0W for imaginary potential (fm). "
            "Actual radius R = p5 * CC",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="volume"
        )

        params["p6"] = PotParameter(
            "p6", "Imaginary diffuseness aW (p6)",
            "Diffuseness parameter aW for imaginary potential (fm)",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="volume"
        )

        params["p0"] = PotParameter(
            "p0", "Additional parameter (p0/p7)",
            "Additional parameter p0 (also called p7). Usage depends on context:\n"
            "- For some potential types, provides extra flexibility\n"
            "- If p0 > 0, updates CC = p0^(1/3)",
            default=0.0, step=0.1, minimum=0.0, maximum=100.0, category="volume"
        )

        # Alternative naming (v, vr0, va, w, wr0, wa)
        params["v"] = PotParameter(
            "v", "Real depth V (MeV)",
            "Equivalent to p1: depth of real potential (MeV)",
            default=50.0, step=1.0, minimum=-500.0, maximum=500.0, category="volume"
        )

        params["vr0"] = PotParameter(
            "vr0", "Real radius r0 (fm)",
            "Equivalent to p2: radius parameter for real potential",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="volume"
        )

        params["va"] = PotParameter(
            "va", "Real diffuseness a (fm)",
            "Equivalent to p3: diffuseness for real potential",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="volume"
        )

        params["w"] = PotParameter(
            "w", "Imaginary depth W (MeV)",
            "Equivalent to p4: depth of imaginary potential (MeV)",
            default=0.0, step=1.0, minimum=-500.0, maximum=500.0, category="volume"
        )

        params["wr0"] = PotParameter(
            "wr0", "Imaginary radius r0W (fm)",
            "Equivalent to p5: radius parameter for imaginary potential",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="volume"
        )

        params["wa"] = PotParameter(
            "wa", "Imaginary diffuseness aW (fm)",
            "Equivalent to p6: diffuseness for imaginary potential",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="volume"
        )

        # ========== Surface Potential Parameters ==========
        params["wd"] = PotParameter(
            "wd", "Surface imaginary depth W_D",
            "Depth of surface imaginary (derivative) potential (MeV)",
            default=0.0, step=1.0, minimum=-500.0, maximum=500.0, category="surface"
        )

        params["wdr0"] = PotParameter(
            "wdr0", "Surface imaginary radius r0D",
            "Radius parameter for surface imaginary potential (fm)",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="surface"
        )

        params["awd"] = PotParameter(
            "awd", "Surface imaginary diffuseness aD",
            "Diffuseness parameter for surface imaginary potential (fm)",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="surface"
        )

        # ========== Spin-Orbit Parameters ==========
        params["vso"] = PotParameter(
            "vso", "Spin-orbit strength V_SO",
            "Spin-orbit potential strength (MeV). "
            "Multiplied by ℏ²/(m_π² c²) = 2.0",
            default=0.0, step=0.1, minimum=-100.0, maximum=100.0, category="spinorbit"
        )

        params["rso0"] = PotParameter(
            "rso0", "Spin-orbit radius r_SO",
            "Radius parameter for spin-orbit potential (fm)",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="spinorbit"
        )

        params["aso"] = PotParameter(
            "aso", "Spin-orbit diffuseness a_SO",
            "Diffuseness for spin-orbit potential (fm)",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="spinorbit"
        )

        params["vsot"] = PotParameter(
            "vsot", "Target spin-orbit V_SOt",
            "Spin-orbit strength for target (TYPE=4)",
            default=0.0, step=0.1, minimum=-100.0, maximum=100.0, category="spinorbit"
        )

        params["rsot0"] = PotParameter(
            "rsot0", "Target SO radius r_SOt",
            "Radius parameter for target spin-orbit potential (fm)",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="spinorbit"
        )

        params["asot"] = PotParameter(
            "asot", "Target SO diffuseness a_SOt",
            "Diffuseness for target spin-orbit potential (fm)",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="spinorbit"
        )

        # ========== Tensor Force Parameters ==========
        params["vt"] = PotParameter(
            "vt", "Tensor strength V_T",
            "Tensor force strength (MeV fm²) for TYPE=5,6,7",
            default=0.0, step=0.1, minimum=-100.0, maximum=100.0, category="tensor"
        )

        params["rt0"] = PotParameter(
            "rt0", "Tensor radius r_T",
            "Radius parameter for tensor force (fm)",
            default=1.2, step=0.01, minimum=0.1, maximum=5.0, category="tensor"
        )

        params["at"] = PotParameter(
            "at", "Tensor diffuseness a_T",
            "Diffuseness for tensor force (fm)",
            default=0.65, step=0.01, minimum=0.1, maximum=2.0, category="tensor"
        )

        # ========== Deformation Parameters (TYPE=10-17) ==========
        params["beta"] = PotParameter(
            "beta", "Deformation β",
            "Deformation parameter β for collective model couplings. "
            "Used with TYPE=8 or TYPE=10,11 (deformed potentials)",
            default=0.0, step=0.01, minimum=-2.0, maximum=2.0, category="deformation"
        )

        params["beta2"] = PotParameter(
            "beta2", "Quadrupole β₂",
            "Quadrupole deformation parameter β₂ (λ=2)",
            default=0.0, step=0.01, minimum=-2.0, maximum=2.0, category="deformation"
        )

        params["beta3"] = PotParameter(
            "beta3", "Octupole β₃",
            "Octupole deformation parameter β₃ (λ=3)",
            default=0.0, step=0.01, minimum=-2.0, maximum=2.0, category="deformation"
        )

        params["beta4"] = PotParameter(
            "beta4", "Hexadecapole β₄",
            "Hexadecapole deformation parameter β₄ (λ=4)",
            default=0.0, step=0.01, minimum=-2.0, maximum=2.0, category="deformation"
        )

        # ========== Advanced Options ==========
        params["jl"] = PotParameter(
            "jl", "L/J dependence (jl)",
            "For SHAPE≥30: specify 'L' or 'J' for angular momentum dependence",
            param_type="select",
            options=[
                ('', "None"),
                ('L', "L: Orbital angular momentum"),
                ('J', "J: Total angular momentum"),
            ],
            default='', category="advanced"
        )

        params["lshape"] = PotParameter(
            "lshape", "L/J shape (lshape)",
            "Shape for L/J-dependent factor (with SHAPE≥30):\n"
            "0 = Woods-Saxon\n"
            "1 = WS squared\n"
            "2 = Gaussian",
            param_type="select",
            options=[
                (0, "0: Woods-Saxon"),
                (1, "1: WS Squared"),
                (2, "2: Gaussian"),
            ],
            default=0, category="advanced"
        )

        params["xlvary"] = PotParameter(
            "xlvary", "L/J center (xlvary)",
            "Center value for L/J-dependent factor. "
            "Factor peaks at L=xlvary or J=xlvary",
            default=0.0, step=0.5, minimum=0.0, maximum=20.0, category="advanced"
        )

        params["alvary"] = PotParameter(
            "alvary", "L/J width (alvary)",
            "Width parameter for L/J-dependent factor (similar to diffuseness)",
            default=1.0, step=0.1, minimum=0.1, maximum=10.0, category="advanced"
        )

        params["datafile"] = PotParameter(
            "datafile", "Data file (datafile)",
            "External file for reading potential form factors (SHAPE=7,8,9)",
            param_type="text",
            default="", category="advanced"
        )

    def get_parameter(self, name: str):
        """Get parameter definition by name"""
        return self.parameters.get(name)

    def get_parameters_by_category(self, category: str):
        """Get all parameters in a given category"""
        return [p for p in self.parameters.values() if p.category == category]

    def generate_pot_namelist(self, param_values: dict):
        """
        Generate a single &POT namelist block from parameter values

        Args:
            param_values: Dictionary of parameter_name: value

        Returns:
            String containing the &POT namelist block
        """
        if not param_values:
            return ""

        lines = ["&POT"]

        # Format each parameter
        for param_name, value in param_values.items():
            param = self.get_parameter(param_name)
            if param is None:
                continue

            # Format based on parameter type
            if param.param_type == "text":
                if value:
                    lines.append(f"{param_name}='{value}'")
            elif param.param_type == "checkbox":
                # Boolean values in FRESCO: T or F
                lines.append(f"{param_name}={'T' if value else 'F'}")
            elif param.param_type == "number":
                # Format numbers appropriately
                if isinstance(value, int) or (isinstance(value, float) and value == int(value)):
                    lines.append(f"{param_name}={int(value)}")
                else:
                    lines.append(f"{param_name}={value}")
            elif param.param_type == "select":
                # For select, value is already the appropriate type
                if isinstance(value, str) and value:
                    lines.append(f"{param_name}='{value}'")
                elif value is not None:
                    lines.append(f"{param_name}={value}")

        lines.append("/")
        lines.append("")

        return "\n".join(lines)


# Global instance
POT_NAMELIST = PotNamelist()
