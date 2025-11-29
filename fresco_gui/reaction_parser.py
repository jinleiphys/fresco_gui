"""
Reaction Equation Parser for FRESCO Studio

Parses nuclear reaction equations in various formats:
- Elastic/Inelastic: "p+ni78", "alpha+c12", "alpha+c12*"
- Transfer: "n14(f17,ne18)c13", "c12(d,p)c13", "40Ca(d,p)41Ca"

Automatically detects reaction type and extracts particle information.
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from enum import Enum

from mass_database import (
    get_nucleus_info, calculate_q_value, NucleusInfo,
    resolve_particle, get_atomic_number, get_mass, get_default_spin
)


class ReactionType(Enum):
    """Types of nuclear reactions"""
    ELASTIC = "elastic"
    INELASTIC = "inelastic"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"


@dataclass
class ParsedReaction:
    """Complete parsed reaction information"""
    reaction_type: ReactionType
    equation: str  # Original equation string

    # Particles
    projectile: Optional[NucleusInfo] = None
    target: Optional[NucleusInfo] = None
    ejectile: Optional[NucleusInfo] = None  # For transfer reactions
    residual: Optional[NucleusInfo] = None  # For transfer reactions

    # Calculated values
    q_value: Optional[float] = None
    is_target_excited: bool = False  # For inelastic

    # Parsing metadata
    parse_success: bool = False
    parse_errors: List[str] = field(default_factory=list)
    parse_warnings: List[str] = field(default_factory=list)

    def get_display_string(self) -> str:
        """Get a formatted display string for the reaction"""
        if self.reaction_type == ReactionType.TRANSFER:
            if all([self.projectile, self.target, self.ejectile, self.residual]):
                return f"{self.target.name}({self.projectile.name},{self.ejectile.name}){self.residual.name}"
        elif self.reaction_type in [ReactionType.ELASTIC, ReactionType.INELASTIC]:
            if self.projectile and self.target:
                suffix = "*" if self.is_target_excited else ""
                return f"{self.projectile.name} + {self.target.name}{suffix}"
        return self.equation


class ReactionParser:
    """
    Parser for nuclear reaction equations.

    Supports multiple input formats and automatically detects reaction type.
    """

    def __init__(self):
        # Regex patterns for different reaction formats
        # Transfer: target(projectile,ejectile)residual
        self.transfer_pattern = re.compile(
            r'^([a-zA-Z0-9]+)\s*\(\s*([a-zA-Z0-9]+)\s*,\s*([a-zA-Z0-9]+)\s*\)\s*([a-zA-Z0-9]+)$'
        )

        # Elastic/Inelastic: projectile + target or projectile+target
        self.elastic_pattern = re.compile(
            r'^([a-zA-Z0-9]+)\s*\+\s*([a-zA-Z0-9]+)(\*?)$'
        )

    def parse(self, equation: str) -> ParsedReaction:
        """
        Parse a reaction equation string.

        Args:
            equation: Reaction equation (e.g., "p+ni78", "n14(f17,ne18)c13")

        Returns:
            ParsedReaction object with parsed information
        """
        equation = equation.strip()

        result = ParsedReaction(
            reaction_type=ReactionType.UNKNOWN,
            equation=equation
        )

        if not equation:
            result.parse_errors.append("Empty equation")
            return result

        # Try to detect and parse based on format
        # First, try transfer reaction format (contains parentheses)
        if '(' in equation and ')' in equation:
            return self._parse_transfer(equation, result)

        # Then try elastic/inelastic format (contains +)
        if '+' in equation:
            return self._parse_elastic_inelastic(equation, result)

        result.parse_errors.append(
            "Unrecognized format. Use 'proj+target' for elastic/inelastic "
            "or 'target(proj,eject)resid' for transfer reactions."
        )
        return result

    def _parse_transfer(self, equation: str, result: ParsedReaction) -> ParsedReaction:
        """Parse transfer reaction format: target(projectile,ejectile)residual"""
        match = self.transfer_pattern.match(equation)

        if not match:
            result.parse_errors.append(
                "Invalid transfer format. Expected: target(projectile,ejectile)residual"
            )
            return result

        target_str, proj_str, eject_str, resid_str = match.groups()

        # Parse each particle
        result.target = get_nucleus_info(target_str)
        result.projectile = get_nucleus_info(proj_str)
        result.ejectile = get_nucleus_info(eject_str)
        result.residual = get_nucleus_info(resid_str)

        # Check for parse errors
        if result.target is None:
            result.parse_errors.append(f"Unknown target nucleus: '{target_str}'")
        if result.projectile is None:
            result.parse_errors.append(f"Unknown projectile: '{proj_str}'")
        if result.ejectile is None:
            result.parse_errors.append(f"Unknown ejectile: '{eject_str}'")
        if result.residual is None:
            result.parse_errors.append(f"Unknown residual nucleus: '{resid_str}'")

        if result.parse_errors:
            return result

        # Validate conservation laws
        self._validate_transfer_conservation(result)

        # Calculate Q-value
        if all([result.projectile, result.target, result.ejectile, result.residual]):
            result.q_value = calculate_q_value(
                result.projectile, result.target,
                result.ejectile, result.residual
            )

        result.reaction_type = ReactionType.TRANSFER
        result.parse_success = len(result.parse_errors) == 0

        return result

    def _parse_elastic_inelastic(self, equation: str, result: ParsedReaction) -> ParsedReaction:
        """Parse elastic/inelastic format: projectile + target[*]"""
        match = self.elastic_pattern.match(equation)

        if not match:
            result.parse_errors.append(
                "Invalid format. Expected: projectile + target (use * for inelastic)"
            )
            return result

        proj_str, target_str, excited_marker = match.groups()

        # Parse particles
        result.projectile = get_nucleus_info(proj_str)
        result.target = get_nucleus_info(target_str)

        # Check for parse errors
        if result.projectile is None:
            result.parse_errors.append(f"Unknown projectile: '{proj_str}'")
        if result.target is None:
            result.parse_errors.append(f"Unknown target nucleus: '{target_str}'")

        if result.parse_errors:
            return result

        # Determine if elastic or inelastic
        result.is_target_excited = (excited_marker == '*')
        result.reaction_type = (
            ReactionType.INELASTIC if result.is_target_excited
            else ReactionType.ELASTIC
        )

        # For elastic scattering, Q=0
        result.q_value = 0.0

        result.parse_success = len(result.parse_errors) == 0

        return result

    def _validate_transfer_conservation(self, result: ParsedReaction):
        """Validate charge and mass conservation for transfer reactions"""
        if not all([result.projectile, result.target, result.ejectile, result.residual]):
            return

        # Check charge conservation (Z)
        z_initial = result.projectile.atomic_number + result.target.atomic_number
        z_final = result.ejectile.atomic_number + result.residual.atomic_number

        if z_initial != z_final:
            result.parse_warnings.append(
                f"Charge not conserved: Z_initial={z_initial}, Z_final={z_final}"
            )

        # Check mass number conservation (A)
        a_initial = result.projectile.mass_number + result.target.mass_number
        a_final = result.ejectile.mass_number + result.residual.mass_number

        if a_initial != a_final:
            result.parse_warnings.append(
                f"Mass number not conserved: A_initial={a_initial}, A_final={a_final}"
            )

    def suggest_completion(self, partial: str) -> List[str]:
        """
        Suggest completions for a partial reaction equation.

        Args:
            partial: Partial equation string

        Returns:
            List of suggested completions
        """
        suggestions = []
        partial = partial.strip().lower()

        # Common reaction examples
        examples = [
            "p+ni78",
            "alpha+c12",
            "alpha+c12*",
            "d+ca40",
            "c12(d,p)c13",
            "ca40(d,p)ca41",
            "n14(f17,ne18)c13",
            "be10(d,p)be11",
            "o16(d,p)o17",
        ]

        for example in examples:
            if example.startswith(partial) or partial in example:
                suggestions.append(example)

        return suggestions[:5]  # Return top 5 suggestions


def parse_reaction(equation: str) -> ParsedReaction:
    """
    Convenience function to parse a reaction equation.

    Args:
        equation: Reaction equation string

    Returns:
        ParsedReaction object
    """
    parser = ReactionParser()
    return parser.parse(equation)


# Utility functions for getting reaction information
def get_transferred_particle(reaction: ParsedReaction) -> Optional[NucleusInfo]:
    """
    Determine the transferred particle for a transfer reaction.

    For A(a,b)B: transferred particle x is such that
    a = b + x (stripping) or A = B + x (pickup)

    Returns:
        NucleusInfo for the transferred particle, or None if not determinable
    """
    if reaction.reaction_type != ReactionType.TRANSFER:
        return None

    if not all([reaction.projectile, reaction.target, reaction.ejectile, reaction.residual]):
        return None

    # Calculate transferred particle properties
    # For stripping: a -> b + x, so x = a - b
    # For pickup: A + x -> B, so x = B - A

    # Try stripping first (more common)
    x_z = reaction.projectile.atomic_number - reaction.ejectile.atomic_number
    x_a = reaction.projectile.mass_number - reaction.ejectile.mass_number

    if x_z >= 0 and x_a > 0:
        # Valid stripping
        from mass_database import get_element_symbol, get_mass

        symbol = get_element_symbol(x_z)
        if symbol:
            mass = get_mass(symbol, x_a)
            if mass:
                return NucleusInfo(
                    symbol=symbol,
                    mass_number=x_a,
                    atomic_number=x_z,
                    mass=mass,
                    name=f"{x_a}{symbol}" if x_a > 1 else symbol
                )

    # Try pickup
    x_z = reaction.residual.atomic_number - reaction.target.atomic_number
    x_a = reaction.residual.mass_number - reaction.target.mass_number

    if x_z >= 0 and x_a > 0:
        from mass_database import get_element_symbol, get_mass

        symbol = get_element_symbol(x_z)
        if symbol:
            mass = get_mass(symbol, x_a)
            if mass:
                return NucleusInfo(
                    symbol=symbol,
                    mass_number=x_a,
                    atomic_number=x_z,
                    mass=mass,
                    name=f"{x_a}{symbol}" if x_a > 1 else symbol
                )

    return None


def is_stripping_reaction(reaction: ParsedReaction) -> bool:
    """
    Determine if a transfer reaction is stripping (projectile loses nucleons).

    Returns True for stripping, False for pickup.
    """
    if reaction.reaction_type != ReactionType.TRANSFER:
        return False

    if not reaction.projectile or not reaction.ejectile:
        return False

    # Stripping: projectile mass decreases (a -> b + x)
    return reaction.projectile.mass_number > reaction.ejectile.mass_number
