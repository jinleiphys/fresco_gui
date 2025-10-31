"""
FRESCO Namelist Parameter Definitions
Global parameter management for all FRESCO calculation types
"""

from typing import Dict, Any, List, Optional


class FrescoParameter:
    """Single FRESCO parameter definition"""

    def __init__(self, name: str, label: str, tooltip: str,
                 param_type: str = "number", default: Any = None,
                 step: float = None, minimum: float = None, maximum: float = None,
                 options: List[tuple] = None, category: str = "general"):
        self.name = name
        self.label = label
        self.tooltip = tooltip
        self.param_type = param_type  # "number", "text", "select", "checkbox"
        self.default = default
        self.step = step
        self.minimum = minimum
        self.maximum = maximum
        self.options = options or []  # For select type: [(value, text), ...]
        self.category = category


class FrescoNamelist:
    """
    Complete FRESCO namelist parameter definitions
    Organized by categories for easy management
    """

    # Basic parameters that appear in most calculations (deprecated, use DEFAULT_GENERAL_PARAMS instead)
    BASIC_PARAMETERS = [
        "hcm", "rmatch", "jtmax", "absend", "thmax", "thinc", "elab", "iter"
    ]

    # Default General parameters for different calculation types
    DEFAULT_GENERAL_PARAMS = {
        "elastic": [
            "hcm", "rmatch", "jtmax", "absend", "thmin", "thmax", "thinc",
            "elab", "iter", "chans", "smats", "xstabl"
        ],
        "inelastic": [
            "hcm", "rmatch", "jtmax", "absend", "thmin", "thmax", "thinc",
            "elab", "iter", "chans", "smats", "xstabl", "rasym", "accrcy",
            "jtmin", "jbord"
        ],
        "transfer": [
            "hcm", "rmatch", "jtmax", "absend", "thmin", "thmax", "thinc",
            "elab", "iter", "chans", "smats", "xstabl", "nnu", "rintp",
            "iblock"
        ],
        "default": [  # Fallback for any other calculation type
            "hcm", "rmatch", "jtmax", "absend", "thmin", "thmax", "thinc",
            "elab", "iter", "chans", "smats", "xstabl"
        ]
    }

    def __init__(self):
        self.parameters = self._init_parameters()
        self.categories = self._init_categories()

    def _init_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize parameter categories"""
        return {
            "radial": {
                "title": "Radial Coordinates",
                "description": "Wave function calculation and radial grid parameters",
                "icon": "📏"
            },
            "partialWaves": {
                "title": "Partial Waves",
                "description": "Angular momentum and J-value control",
                "icon": "🌀"
            },
            "angular": {
                "title": "Angular Distributions",
                "description": "Scattering angle and analyzing power parameters",
                "icon": "📐"
            },
            "coupled": {
                "title": "Coupled Equations",
                "description": "Coupling definition and accuracy parameters",
                "icon": "🔗"
            },
            "iterations": {
                "title": "Iterations & Convergence",
                "description": "Iteration control and convergence criteria",
                "icon": "🔄"
            },
            "output": {
                "title": "Output Control",
                "description": "File output and printing options",
                "icon": "📄"
            },
            "advanced": {
                "title": "Advanced Options",
                "description": "Specialized and advanced parameters",
                "icon": "⚙️"
            }
        }

    def _init_parameters(self) -> Dict[str, FrescoParameter]:
        """Initialize all FRESCO parameters"""
        params = {}

        # ============================================================
        # RADIAL COORDINATES
        # ============================================================
        params["hcm"] = FrescoParameter(
            "hcm", "Integration step size (hcm)",
            "Step size for integration in center-of-mass frame. Smaller values give more accurate results (typical: 0.05-0.1)",
            default=0.1, step=0.01, minimum=0.001, maximum=1.0, category="radial"
        )

        params["rmatch"] = FrescoParameter(
            "rmatch", "Matching radius (rmatch)",
            "Radius at which internal and asymptotic solutions are matched. If negative, use coupled Coulomb wave functions (typical: 20-60 fm)",
            default=60.0, step=0.1, minimum=-200.0, maximum=200.0, category="radial"
        )

        params["rintp"] = FrescoParameter(
            "rintp", "Non-local radius step (rintp)",
            "Non-local kernels calculated at Rf intervals of RINTP. Rounded to multiples of HCM",
            default=None, step=0.1, minimum=0.0, maximum=10.0, category="radial"
        )

        params["hnl"] = FrescoParameter(
            "hnl", "Non-local step size (hnl)",
            "Step size for non-local range discretization. Rounded to multiple or sub-multiple of HCM",
            default=None, step=0.01, minimum=0.001, maximum=1.0, category="radial"
        )

        params["rnl"] = FrescoParameter(
            "rnl", "Non-local range (rnl)",
            "Non-local range for kernels K0fi(Rf;Dfi)",
            default=None, step=0.1, minimum=0.0, maximum=50.0, category="radial"
        )

        params["centre"] = FrescoParameter(
            "centre", "Non-local center (centre)",
            "Center position for non-local range RNL",
            default=None, step=0.1, minimum=-10.0, maximum=10.0, category="radial"
        )

        params["accrcy"] = FrescoParameter(
            "accrcy", "Accuracy parameter (accrcy)",
            "Accuracy parameter for piecewise step length. Smaller gives greater accuracy (default=0.01)",
            default=0.01, step=0.001, minimum=0.0001, maximum=0.1, category="radial"
        )

        params["rasym"] = FrescoParameter(
            "rasym", "Asymptotic radius (rasym)",
            "Asymptotic radius for coupled Coulomb wave functions. If negative, determine from classical angle",
            default=None, step=0.1, minimum=-100.0, maximum=200.0, category="radial"
        )

        params["switch"] = FrescoParameter(
            "switch", "Switch radius (switch)",
            "Radius to switch from Airy functions to sines/cosines in piecewise method (default=1000 fm)",
            default=1000.0, step=10.0, minimum=10.0, maximum=10000.0, category="radial"
        )

        params["ajswtch"] = FrescoParameter(
            "ajswtch", "Angular momentum switch (ajswtch)",
            "Coupled Coulomb matching allowed only when J ≤ AJSWITCH (default=0.0)",
            default=0.0, step=0.5, minimum=0.0, maximum=100.0, category="radial"
        )

        # ============================================================
        # PARTIAL WAVES
        # ============================================================
        params["jtmin"] = FrescoParameter(
            "jtmin", "Minimum J (jtmin)",
            "Minimum total angular momentum. If negative, J < |JTMIN| include only incoming channel",
            default=0.0, step=0.5, minimum=-50.0, maximum=50.0, category="partialWaves"
        )

        params["jtmax"] = FrescoParameter(
            "jtmax", "Maximum J (jtmax)",
            "Maximum total angular momentum included in calculation",
            default=50.0, step=0.5, minimum=0.0, maximum=200.0, category="partialWaves"
        )

        params["absend"] = FrescoParameter(
            "absend", "Convergence criterion (absend)",
            "Stop if absorption < ABSEND mb for 3 successive J/parity sets. If negative, take full J interval",
            default=0.001, step=0.001, minimum=-1.0, maximum=1.0, category="partialWaves"
        )

        params["jump"] = FrescoParameter(
            "jump", "J-value intervals (jump)",
            "Calculate at intervals of JUMP(i) for J ≥ JBORD(i). Comma-separated for multiple intervals",
            param_type="text", default=None, category="partialWaves"
        )

        params["jbord"] = FrescoParameter(
            "jbord", "J-value borders (jbord)",
            "J borders for different JUMP intervals. Comma-separated values",
            param_type="text", default=None, category="partialWaves"
        )

        params["pset"] = FrescoParameter(
            "pset", "Parity restriction (pset)",
            "Restrict parity calculation",
            param_type="select", default=0,
            options=[(-1, "-1 (Negative parity only)"),
                    (0, "0 (No restriction)"),
                    (1, "+1 (Positive parity only)")],
            category="partialWaves"
        )

        params["jset"] = FrescoParameter(
            "jset", "Number of sets (jset)",
            "Number of CRC sets to calculate before stopping. 0 = all sets",
            default=0, step=1, minimum=0, maximum=1000, category="partialWaves"
        )

        params["llmax"] = FrescoParameter(
            "llmax", "Maximum L (llmax)",
            "Maximum partial wave L in any CRC set",
            default=None, step=1, minimum=0, maximum=500, category="partialWaves"
        )

        # ============================================================
        # ANGULAR DISTRIBUTIONS
        # ============================================================
        params["thmin"] = FrescoParameter(
            "thmin", "Minimum angle (thmin)",
            "Minimum center-of-mass scattering angle in degrees",
            default=0.0, step=0.1, minimum=0.0, maximum=180.0, category="angular"
        )

        params["thmax"] = FrescoParameter(
            "thmax", "Maximum angle (thmax)",
            "Maximum scattering angle. If negative, absolute cross sections instead of ratio to Rutherford",
            default=180.0, step=0.1, minimum=-180.0, maximum=180.0, category="angular"
        )

        params["thinc"] = FrescoParameter(
            "thinc", "Angle increment (thinc)",
            "Increment between calculated scattering angles in degrees",
            default=1.0, step=0.1, minimum=0.01, maximum=10.0, category="angular"
        )

        params["kqmax"] = FrescoParameter(
            "kqmax", "Max tensor rank (kqmax)",
            "Maximum tensor analyzing power rank K",
            default=0, step=1, minimum=0, maximum=10, category="angular"
        )

        params["pp"] = FrescoParameter(
            "pp", "Polarization type (pp)",
            "Calculate analyzing powers for specific particle",
            param_type="select", default=0,
            options=[(0, "0 - Projectile"),
                    (1, "1 - Target"),
                    (2, "2 - Ejectile"),
                    (3, "3 - Residual nucleus"),
                    (4, "4 - Projectile + Kyy")],
            category="angular"
        )

        params["koords"] = FrescoParameter(
            "koords", "Coordinate system (koords)",
            "Coordinate systems for analyzing powers",
            param_type="select", default=0,
            options=[(0, "0 - Madison coordinates"),
                    (1, "1 - Madison + Transverse"),
                    (2, "2 - Madison + Transverse + Recoil"),
                    (3, "3 - Madison + Transverse + Recoil + Hooton-Johnson")],
            category="angular"
        )

        # ============================================================
        # COUPLED EQUATIONS
        # ============================================================
        params["nnu"] = FrescoParameter(
            "nnu", "Angular integration points (nnu)",
            "Gaussian integration points for non-local transfer kernels. Multiple of 6, minimum 18",
            default=24, step=6, minimum=18, maximum=120, category="coupled"
        )

        params["maxl"] = FrescoParameter(
            "maxl", "Max L for kernels (maxl)",
            "Maximum L for non-local kernels. Default=JTMAX+6 if zero",
            default=None, step=1, minimum=0, maximum=500, category="coupled"
        )

        params["minl"] = FrescoParameter(
            "minl", "Min L for kernels (minl)",
            "Minimum L for non-local kernels. Default=|JTMIN|-6 if negative",
            default=None, step=1, minimum=-50, maximum=500, category="coupled"
        )

        params["epc"] = FrescoParameter(
            "epc", "Angular integration accuracy (epc)",
            "Percentage cutoff accuracy in NNU angular integration. Default=(30/NNU)²% if zero",
            default=None, step=0.1, minimum=0.0, maximum=100.0, category="coupled"
        )

        params["plane"] = FrescoParameter(
            "plane", "Coulomb zeroing (plane)",
            "Zero Coulomb potential for specific channels",
            param_type="select", default=None,
            options=[(None, "None (include all Coulomb)"),
                    (1, "1 - Zero elastic Coulomb"),
                    (2, "2 - Zero nonelastic Coulomb"),
                    (3, "3 - Zero all Coulomb")],
            category="coupled"
        )

        # ============================================================
        # ITERATIONS & CONVERGENCE
        # ============================================================
        params["elab"] = FrescoParameter(
            "elab", "Laboratory energy (elab)",
            "Laboratory energy of projectile in MeV. For multi-energy, use comma-separated values",
            param_type="text", default="30.0", category="iterations"
        )

        params["iter"] = FrescoParameter(
            "iter", "Number of iterations (iter)",
            "Number of iterations for solving coupled equations. For elastic scattering, 1 is sufficient",
            default=1, step=1, minimum=0, maximum=100, category="iterations"
        )

        params["iblock"] = FrescoParameter(
            "iblock", "Block structure (iblock)",
            "Block-diagonal structure: 0=general, 1=block-diagonal in partition index",
            param_type="select", default=0,
            options=[(0, "0 - General (full coupling)"),
                    (1, "1 - Block diagonal in partition")],
            category="iterations"
        )

        params["pcon"] = FrescoParameter(
            "pcon", "Print convergence (pcon)",
            "Print convergence of coupled equations: 0=no, 1=yes",
            param_type="select", default=0,
            options=[(0, "0 - No printing"),
                    (1, "1 - Print convergence")],
            category="iterations"
        )

        # ============================================================
        # OUTPUT CONTROL
        # ============================================================
        params["chans"] = FrescoParameter(
            "chans", "Print channels (chans)",
            "Print coupling matrix elements and channel info: 0=minimal, 1=full",
            param_type="select", default=1,
            options=[(0, "0 - Minimal output"),
                    (1, "1 - Full channel info")],
            category="output"
        )

        params["smats"] = FrescoParameter(
            "smats", "Print S-matrix (smats)",
            "Print S-matrix elements: 0=no, 1=diagonal, 2=all",
            param_type="select", default=2,
            options=[(0, "0 - No S-matrix"),
                    (1, "1 - Diagonal only"),
                    (2, "2 - All S-matrix elements")],
            category="output"
        )

        params["xstabl"] = FrescoParameter(
            "xstabl", "Print cross sections (xstabl)",
            "Print integrated cross sections: 0=no, 1=yes",
            param_type="select", default=1,
            options=[(0, "0 - No cross sections"),
                    (1, "1 - Print cross sections")],
            category="output"
        )

        params["nlab"] = FrescoParameter(
            "nlab", "Print lab angles (nlab)",
            "Print differential cross sections at lab angles: 0=c.m., 1=lab",
            param_type="select", default=0,
            options=[(0, "0 - Center-of-mass angles"),
                    (1, "1 - Laboratory angles")],
            category="output"
        )

        # ============================================================
        # ADVANCED OPTIONS
        # ============================================================
        params["rela"] = FrescoParameter(
            "rela", "Relativistic kinematics (rela)",
            "Relativistic options: 'a'=Ingemarsson eq(16), 'b'=eq(17), 'c'/'3d'=knockout",
            param_type="text", default=None, category="advanced"
        )

        params["unitmass"] = FrescoParameter(
            "unitmass", "Mass unit (unitmass)",
            "Unit in amu for MASS values read in (default=1.000)",
            default=1.000, step=0.001, minimum=0.1, maximum=10.0, category="advanced"
        )

        params["finec"] = FrescoParameter(
            "finec", "Fine structure constant (finec)",
            "1/(fine-structure constant) for electrostatic e² (default=137.03599)",
            default=137.03599, step=0.001, minimum=100.0, maximum=200.0, category="advanced"
        )

        params["hbarc"] = FrescoParameter(
            "hbarc", "ℏc constant (hbarc)",
            "Value of ℏc in MeV·fm (default=197.3269788)",
            default=197.3269788, step=0.001, minimum=100.0, maximum=300.0, category="advanced"
        )

        params["pel"] = FrescoParameter(
            "pel", "Elastic print (pel)",
            "Print elastic scattering only: 0=all, 1=elastic only",
            param_type="select", default=0,
            options=[(0, "0 - All channels"),
                    (1, "1 - Elastic only")],
            category="advanced"
        )

        params["exl"] = FrescoParameter(
            "exl", "Excitation print (exl)",
            "Print inelastic excitations: 0=all, 1=specific L-values",
            param_type="select", default=0,
            options=[(0, "0 - All excitations"),
                    (1, "1 - Specific L-values")],
            category="advanced"
        )

        return params

    def get_parameter(self, name: str) -> Optional[FrescoParameter]:
        """Get parameter by name"""
        return self.parameters.get(name)

    def get_parameters_by_category(self, category: str) -> List[FrescoParameter]:
        """Get all parameters in a category"""
        return [p for p in self.parameters.values() if p.category == category]

    def get_basic_parameters(self) -> List[FrescoParameter]:
        """Get basic/common parameters"""
        return [self.parameters[name] for name in self.BASIC_PARAMETERS if name in self.parameters]

    def get_advanced_parameters(self) -> List[FrescoParameter]:
        """Get advanced (non-basic) parameters"""
        return [p for name, p in self.parameters.items() if name not in self.BASIC_PARAMETERS]

    def generate_namelist_text(self, param_values: Dict[str, Any]) -> str:
        """
        Generate &FRESCO namelist text from parameter values
        Includes all provided values (even if they match defaults)
        Formats parameters 5 per line for better readability
        """
        lines = [" &FRESCO"]

        # Collect all parameter strings
        param_strings = []
        for name, value in param_values.items():
            if name in self.parameters:
                param = self.parameters[name]
                # Include the value if it's not None
                # Don't skip values that equal defaults - user explicitly set them
                if value is not None:
                    param_strings.append(f"{name}={value}")

        # Format 5 parameters per line
        PARAMS_PER_LINE = 5
        for i in range(0, len(param_strings), PARAMS_PER_LINE):
            chunk = param_strings[i:i + PARAMS_PER_LINE]
            line = "     " + " ".join(chunk)
            lines.append(line)

        lines.append(" /")
        return "\n".join(lines)


# Global instance
FRESCO_NAMELIST = FrescoNamelist()
