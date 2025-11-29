"""
Nuclear Mass Database for FRESCO Studio

Contains atomic masses (in amu), atomic numbers, and common nuclear properties
for reaction equation parsing and Q-value calculations.

Data sources: AME2020 atomic mass evaluation
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# Element symbol to atomic number mapping
ELEMENT_TO_Z = {
    'n': 0,   # neutron
    'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5,
    'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
    'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,
    'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20,
    'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25,
    'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30,
    'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35,
    'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40,
    'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45,
    'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
    'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55,
    'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60,
    'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65,
    'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70,
    'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75,
    'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80,
    'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85,
    'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90,
    'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95,
    'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100,
}

# Reverse mapping: Z to element symbol
Z_TO_ELEMENT = {v: k for k, v in ELEMENT_TO_Z.items()}

# Particle aliases for common names
PARTICLE_ALIASES = {
    # Nucleons
    'p': ('H', 1),      # proton
    'n': ('n', 1),      # neutron
    'proton': ('H', 1),
    'neutron': ('n', 1),

    # Light ions
    'd': ('H', 2),      # deuteron
    't': ('H', 3),      # triton
    'deuteron': ('H', 2),
    'triton': ('H', 3),
    'alpha': ('He', 4),
    'a': ('He', 4),
    '3he': ('He', 3),
    'he3': ('He', 3),
    '4he': ('He', 4),
    'he4': ('He', 4),

    # Common light nuclei
    '6li': ('Li', 6),
    '7li': ('Li', 7),
    '9be': ('Be', 9),
    '10be': ('Be', 10),
    '10b': ('B', 10),
    '11b': ('B', 11),
    '12c': ('C', 12),
    '13c': ('C', 13),
    '14c': ('C', 14),
    '14n': ('N', 14),
    '15n': ('N', 15),
    '16o': ('O', 16),
    '17o': ('O', 17),
    '18o': ('O', 18),
    '17f': ('F', 17),
    '18f': ('F', 18),
    '19f': ('F', 19),
    '18ne': ('Ne', 18),
    '20ne': ('Ne', 20),
}

# Atomic masses in atomic mass units (u)
# Key: (element_symbol, mass_number)
# Value: atomic mass in u
ATOMIC_MASSES: Dict[Tuple[str, int], float] = {
    # Neutron
    ('n', 1): 1.008665,

    # Hydrogen isotopes
    ('H', 1): 1.007825,   # proton
    ('H', 2): 2.014102,   # deuteron
    ('H', 3): 3.016049,   # triton

    # Helium isotopes
    ('He', 3): 3.016029,
    ('He', 4): 4.002603,  # alpha
    ('He', 6): 6.018889,
    ('He', 8): 8.033922,

    # Lithium isotopes
    ('Li', 6): 6.015123,
    ('Li', 7): 7.016005,
    ('Li', 8): 8.022487,
    ('Li', 9): 9.026790,
    ('Li', 11): 11.043798,

    # Beryllium isotopes
    ('Be', 7): 7.016930,
    ('Be', 8): 8.005305,
    ('Be', 9): 9.012182,
    ('Be', 10): 10.013534,
    ('Be', 11): 11.021658,
    ('Be', 12): 12.026921,

    # Boron isotopes
    ('B', 8): 8.024607,
    ('B', 10): 10.012937,
    ('B', 11): 11.009305,
    ('B', 12): 12.014352,

    # Carbon isotopes
    ('C', 10): 10.016853,
    ('C', 11): 11.011434,
    ('C', 12): 12.000000,
    ('C', 13): 13.003355,
    ('C', 14): 14.003242,
    ('C', 15): 15.010599,

    # Nitrogen isotopes
    ('N', 12): 12.018613,
    ('N', 13): 13.005739,
    ('N', 14): 14.003074,
    ('N', 15): 15.000109,
    ('N', 16): 16.006102,

    # Oxygen isotopes
    ('O', 14): 14.008596,
    ('O', 15): 15.003066,
    ('O', 16): 15.994915,
    ('O', 17): 16.999132,
    ('O', 18): 17.999161,
    ('O', 19): 19.003580,

    # Fluorine isotopes
    ('F', 17): 17.002095,
    ('F', 18): 18.000938,
    ('F', 19): 18.998403,
    ('F', 20): 19.999981,

    # Neon isotopes
    ('Ne', 18): 18.005708,
    ('Ne', 19): 19.001880,
    ('Ne', 20): 19.992440,
    ('Ne', 21): 20.993847,
    ('Ne', 22): 21.991385,

    # Sodium isotopes
    ('Na', 22): 21.994437,
    ('Na', 23): 22.989769,
    ('Na', 24): 23.990963,

    # Magnesium isotopes
    ('Mg', 24): 23.985042,
    ('Mg', 25): 24.985837,
    ('Mg', 26): 25.982593,

    # Aluminum isotopes
    ('Al', 26): 25.986892,
    ('Al', 27): 26.981539,

    # Silicon isotopes
    ('Si', 28): 27.976927,
    ('Si', 29): 28.976495,
    ('Si', 30): 29.973770,

    # Phosphorus
    ('P', 31): 30.973762,

    # Sulfur isotopes
    ('S', 32): 31.972071,
    ('S', 33): 32.971459,
    ('S', 34): 33.967867,

    # Chlorine isotopes
    ('Cl', 35): 34.968853,
    ('Cl', 37): 36.965903,

    # Argon isotopes
    ('Ar', 36): 35.967545,
    ('Ar', 38): 37.962732,
    ('Ar', 40): 39.962383,

    # Potassium isotopes
    ('K', 39): 38.963707,
    ('K', 40): 39.963999,
    ('K', 41): 40.961826,

    # Calcium isotopes
    ('Ca', 40): 39.962591,
    ('Ca', 41): 40.962278,
    ('Ca', 42): 41.958618,
    ('Ca', 43): 42.958767,
    ('Ca', 44): 43.955482,
    ('Ca', 48): 47.952534,

    # Scandium
    ('Sc', 45): 44.955912,

    # Titanium isotopes
    ('Ti', 46): 45.952632,
    ('Ti', 47): 46.951763,
    ('Ti', 48): 47.947946,
    ('Ti', 49): 48.947870,
    ('Ti', 50): 49.944791,

    # Iron isotopes
    ('Fe', 54): 53.939611,
    ('Fe', 56): 55.934938,
    ('Fe', 57): 56.935394,
    ('Fe', 58): 57.933276,

    # Nickel isotopes
    ('Ni', 58): 57.935343,
    ('Ni', 60): 59.930786,
    ('Ni', 62): 61.928345,
    ('Ni', 64): 63.927966,
    ('Ni', 78): 77.963180,  # Exotic

    # Copper isotopes
    ('Cu', 63): 62.929598,
    ('Cu', 65): 64.927790,

    # Zinc isotopes
    ('Zn', 64): 63.929142,
    ('Zn', 66): 65.926033,
    ('Zn', 68): 67.924844,
    ('Zn', 70): 69.925319,

    # Lead isotopes
    ('Pb', 206): 205.974465,
    ('Pb', 207): 206.975897,
    ('Pb', 208): 207.976652,

    # Uranium isotopes
    ('U', 235): 235.043930,
    ('U', 238): 238.050788,
}


@dataclass
class NucleusInfo:
    """Information about a specific nucleus"""
    symbol: str         # Element symbol (e.g., 'C', 'He')
    mass_number: int    # A (e.g., 12, 4)
    atomic_number: int  # Z (e.g., 6, 2)
    mass: float         # Atomic mass in amu
    name: str           # Display name (e.g., '12C', 'alpha')

    @property
    def neutron_number(self) -> int:
        """Return N = A - Z"""
        return self.mass_number - self.atomic_number


def get_atomic_number(symbol: str) -> Optional[int]:
    """Get atomic number (Z) from element symbol"""
    # Normalize case for lookup
    if len(symbol) == 1:
        symbol = symbol.upper()
    elif len(symbol) == 2:
        symbol = symbol[0].upper() + symbol[1].lower()

    return ELEMENT_TO_Z.get(symbol)


def get_element_symbol(z: int) -> Optional[str]:
    """Get element symbol from atomic number (Z)"""
    return Z_TO_ELEMENT.get(z)


def get_mass(symbol: str, mass_number: int) -> Optional[float]:
    """
    Get atomic mass for a specific isotope.

    Args:
        symbol: Element symbol (e.g., 'C', 'He')
        mass_number: Mass number A

    Returns:
        Atomic mass in amu, or None if not found
    """
    # Normalize symbol
    if len(symbol) == 1:
        symbol = symbol.upper()
    elif len(symbol) == 2:
        symbol = symbol[0].upper() + symbol[1].lower()

    mass = ATOMIC_MASSES.get((symbol, mass_number))

    # If not in table, estimate from A
    if mass is None:
        # Simple approximation: mass ≈ A * 0.99925 (binding energy correction)
        mass = mass_number * 0.99925

    return mass


def resolve_particle(name: str) -> Optional[Tuple[str, int]]:
    """
    Resolve a particle name to (element_symbol, mass_number).

    Handles aliases like 'p', 'd', 'alpha', as well as isotope
    notation like '12C', 'c12', '12c'.

    Args:
        name: Particle name (case insensitive)

    Returns:
        Tuple of (symbol, mass_number) or None if unrecognized
    """
    import re

    name_lower = name.lower().strip()

    # Check aliases first
    if name_lower in PARTICLE_ALIASES:
        return PARTICLE_ALIASES[name_lower]

    # Try to parse isotope notation: "12C", "C12", "c12", "12c"
    # Pattern 1: Number first, then element (e.g., "12C", "12c")
    match = re.match(r'^(\d+)([a-zA-Z]{1,2})$', name)
    if match:
        mass_number = int(match.group(1))
        symbol = match.group(2)
        if len(symbol) == 1:
            symbol = symbol.upper()
        else:
            symbol = symbol[0].upper() + symbol[1].lower()

        if symbol in ELEMENT_TO_Z:
            return (symbol, mass_number)

    # Pattern 2: Element first, then number (e.g., "C12", "c12")
    match = re.match(r'^([a-zA-Z]{1,2})(\d+)$', name)
    if match:
        symbol = match.group(1)
        mass_number = int(match.group(2))
        if len(symbol) == 1:
            symbol = symbol.upper()
        else:
            symbol = symbol[0].upper() + symbol[1].lower()

        if symbol in ELEMENT_TO_Z:
            return (symbol, mass_number)

    # Try just the element name (will need mass number from context)
    if len(name_lower) <= 2:
        if len(name_lower) == 1:
            symbol = name_lower.upper()
        else:
            symbol = name_lower[0].upper() + name_lower[1].lower()

        if symbol in ELEMENT_TO_Z:
            # Return with mass_number = 0 to indicate it needs to be specified
            return (symbol, 0)

    return None


def get_nucleus_info(name: str) -> Optional[NucleusInfo]:
    """
    Get complete information about a nucleus from its name.

    Args:
        name: Particle name (e.g., 'p', 'alpha', '12C', 'c12')

    Returns:
        NucleusInfo object or None if unrecognized
    """
    result = resolve_particle(name)
    if result is None:
        return None

    symbol, mass_number = result
    if mass_number == 0:
        return None  # Mass number required

    z = get_atomic_number(symbol)
    if z is None:
        return None

    mass = get_mass(symbol, mass_number)

    # Generate display name
    if symbol == 'H' and mass_number == 1:
        display_name = 'p'
    elif symbol == 'H' and mass_number == 2:
        display_name = 'd'
    elif symbol == 'H' and mass_number == 3:
        display_name = 't'
    elif symbol == 'He' and mass_number == 4:
        display_name = 'alpha'
    elif symbol == 'He' and mass_number == 3:
        display_name = '3He'
    elif symbol == 'n' and mass_number == 1:
        display_name = 'n'
    else:
        display_name = f"{mass_number}{symbol}"

    return NucleusInfo(
        symbol=symbol,
        mass_number=mass_number,
        atomic_number=z,
        mass=mass,
        name=display_name
    )


def calculate_q_value(projectile: NucleusInfo, target: NucleusInfo,
                      ejectile: NucleusInfo, residual: NucleusInfo) -> float:
    """
    Calculate Q-value for a reaction: A(a,b)B

    Q = (M_a + M_A - M_b - M_B) * c^2

    Args:
        projectile: Incoming particle 'a'
        target: Target nucleus 'A'
        ejectile: Outgoing particle 'b'
        residual: Residual nucleus 'B'

    Returns:
        Q-value in MeV
    """
    # 1 amu = 931.494 MeV/c^2
    AMU_TO_MEV = 931.494

    mass_initial = projectile.mass + target.mass
    mass_final = ejectile.mass + residual.mass

    q_value = (mass_initial - mass_final) * AMU_TO_MEV

    return q_value


# Default ground state spins for common nuclei
# Key: (symbol, mass_number), Value: spin (J)
DEFAULT_SPINS: Dict[Tuple[str, int], float] = {
    ('n', 1): 0.5,    # neutron
    ('H', 1): 0.5,    # proton
    ('H', 2): 1.0,    # deuteron
    ('H', 3): 0.5,    # triton
    ('He', 3): 0.5,
    ('He', 4): 0.0,   # alpha
    ('Li', 6): 1.0,
    ('Li', 7): 1.5,
    ('Be', 9): 1.5,
    ('B', 10): 3.0,
    ('B', 11): 1.5,
    ('C', 12): 0.0,
    ('C', 13): 0.5,
    ('C', 14): 0.0,
    ('N', 14): 1.0,
    ('N', 15): 0.5,
    ('O', 16): 0.0,
    ('O', 17): 2.5,
    ('O', 18): 0.0,
    ('F', 17): 2.5,
    ('F', 18): 1.0,
    ('F', 19): 0.5,
    ('Ne', 18): 0.0,
    ('Ne', 20): 0.0,
    ('Ca', 40): 0.0,
    ('Ca', 41): 3.5,
    ('Ca', 48): 0.0,
    ('Ni', 58): 0.0,
    ('Ni', 78): 0.0,
    ('Pb', 208): 0.0,
}

# Default ground state parities for common nuclei
# +1 for positive parity, -1 for negative parity
DEFAULT_PARITIES: Dict[Tuple[str, int], int] = {
    ('n', 1): 1,      # neutron 1/2+
    ('H', 1): 1,      # proton 1/2+
    ('H', 2): 1,      # deuteron 1+
    ('H', 3): 1,      # triton 1/2+
    ('He', 3): 1,     # 3He 1/2+
    ('He', 4): 1,     # alpha 0+
    ('Li', 6): 1,     # 1+
    ('Li', 7): -1,    # 3/2-
    ('Be', 9): -1,    # 3/2-
    ('B', 10): 1,     # 3+
    ('B', 11): -1,    # 3/2-
    ('C', 12): 1,     # 0+
    ('C', 13): -1,    # 1/2-  (p-shell)
    ('C', 14): 1,     # 0+
    ('N', 14): 1,     # 1+
    ('N', 15): -1,    # 1/2-
    ('O', 16): 1,     # 0+
    ('O', 17): 1,     # 5/2+  (d-shell)
    ('O', 18): 1,     # 0+
    ('F', 17): 1,     # 5/2+
    ('F', 18): 1,     # 1+
    ('F', 19): 1,     # 1/2+
    ('Ne', 18): 1,    # 0+
    ('Ne', 20): 1,    # 0+
    ('Ca', 40): 1,    # 0+
    ('Ca', 41): -1,   # 7/2-
    ('Ca', 48): 1,    # 0+
    ('Ni', 58): 1,    # 0+
    ('Ni', 78): 1,    # 0+
    ('Pb', 208): 1,   # 0+
}


def get_default_spin(symbol: str, mass_number: int) -> float:
    """
    Get default ground state spin for a nucleus.

    Args:
        symbol: Element symbol
        mass_number: Mass number A

    Returns:
        Default spin value (0.0 if not known)
    """
    return DEFAULT_SPINS.get((symbol, mass_number), 0.0)


def get_default_parity(symbol: str, mass_number: int) -> int:
    """
    Get default ground state parity for a nucleus.

    Args:
        symbol: Element symbol
        mass_number: Mass number A

    Returns:
        Default parity: +1 for positive, -1 for negative
        Defaults to +1 if not known
    """
    return DEFAULT_PARITIES.get((symbol, mass_number), 1)
