"""
Dynamic Parameter Manager for FRESCO GUI
Manages the categorization of parameters between General and Advanced sections
"""

from typing import Set, List, Dict, Any, Optional
from fresco_namelist import FRESCO_NAMELIST


class ParameterManager:
    """
    Manages dynamic categorization of FRESCO parameters between General and Advanced sections.

    The manager adapts the parameter display based on:
    1. Calculation type (elastic, inelastic, transfer, etc.)
    2. Parameters found in loaded input files

    This provides a cleaner UI by showing only the most relevant parameters in the General section.
    """

    def __init__(self, calculation_type: str = "default"):
        """
        Initialize the parameter manager

        Args:
            calculation_type: Type of calculation ("elastic", "inelastic", "transfer", or "default")
        """
        self.calculation_type = calculation_type
        self.input_file_parameters: Set[str] = set()

        # Get default parameters for this calculation type
        self.default_general_params = FRESCO_NAMELIST.DEFAULT_GENERAL_PARAMS.get(
            calculation_type,
            FRESCO_NAMELIST.DEFAULT_GENERAL_PARAMS["default"]
        )

        # Current categorization
        self.general_params: List[str] = []
        self.advanced_params: List[str] = []

        # Initialize with default categorization
        self.reset_to_default()

    def reset_to_default(self):
        """Reset to default categorization (no input file loaded)"""
        self.input_file_parameters.clear()

        # Get all parameter names from FRESCO_NAMELIST
        all_param_names = list(FRESCO_NAMELIST.parameters.keys())

        # Set General parameters to defaults
        self.general_params = [p for p in self.default_general_params if p in all_param_names]

        # Set Advanced parameters to all others
        self.advanced_params = [p for p in all_param_names if p not in self.general_params]

        print(f"[ParameterManager] Reset to default: {len(self.general_params)} general, "
              f"{len(self.advanced_params)} advanced")

    def update_from_input_file(self, file_parameters: Set[str]):
        """
        Update parameter categorization based on parameters found in an input file

        Args:
            file_parameters: Set of parameter names found in the input file
        """
        self.input_file_parameters = file_parameters

        # Get all parameter names
        all_param_names = set(FRESCO_NAMELIST.parameters.keys())

        # Start with default General parameters
        new_general = set(self.default_general_params)

        # Add parameters from input file that are not already in default general
        params_to_promote = file_parameters & all_param_names - new_general
        new_general.update(params_to_promote)

        # Update categorization
        self.general_params = sorted(new_general)
        self.advanced_params = sorted(all_param_names - new_general)

        print(f"[ParameterManager] Updated from input file: {len(self.general_params)} general, "
              f"{len(self.advanced_params)} advanced")
        print(f"[ParameterManager] Promoted to general: {sorted(params_to_promote)}")

    def is_general_parameter(self, param_name: str) -> bool:
        """Check if a parameter is currently in the General section"""
        return param_name in self.general_params

    def is_advanced_parameter(self, param_name: str) -> bool:
        """Check if a parameter is currently in the Advanced section"""
        return param_name in self.advanced_params

    def is_from_input_file(self, param_name: str) -> bool:
        """Check if a parameter was found in the loaded input file"""
        return param_name in self.input_file_parameters

    def get_general_parameters(self) -> List[str]:
        """Get list of parameters currently in General section"""
        return self.general_params.copy()

    def get_advanced_parameters(self) -> List[str]:
        """Get list of parameters currently in Advanced section"""
        return self.advanced_params.copy()

    def get_general_parameter_details(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about General parameters

        Returns:
            List of dicts with parameter metadata including name, label, tooltip, etc.
        """
        details = []
        for param_name in self.general_params:
            param_config = FRESCO_NAMELIST.get_parameter(param_name)
            if param_config:
                details.append({
                    'name': param_name,
                    'label': param_config.label,
                    'tooltip': param_config.tooltip,
                    'type': param_config.param_type,
                    'default': param_config.default,
                    'minimum': param_config.minimum,
                    'maximum': param_config.maximum,
                    'step': param_config.step,
                    'options': param_config.options,
                    'category': param_config.category,
                    'is_from_file': param_name in self.input_file_parameters
                })
        return details

    def get_advanced_parameters_by_category(self) -> Dict[str, List[str]]:
        """
        Get Advanced parameters grouped by category

        Returns:
            Dict mapping category name to list of parameter names
        """
        params_by_category = {}

        for param_name in self.advanced_params:
            param_config = FRESCO_NAMELIST.get_parameter(param_name)
            if param_config:
                category = param_config.category
                if category not in params_by_category:
                    params_by_category[category] = []
                params_by_category[category].append(param_name)

        return params_by_category

    def get_categorization_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current parameter categorization

        Returns:
            Dict with summary information
        """
        return {
            'calculation_type': self.calculation_type,
            'total_parameters': len(FRESCO_NAMELIST.parameters),
            'general_count': len(self.general_params),
            'advanced_count': len(self.advanced_params),
            'general_params': self.general_params,
            'advanced_params': self.advanced_params,
            'parameters_from_file': len(self.input_file_parameters),
            'promoted_params': sorted(self.input_file_parameters - set(self.default_general_params))
        }

    def set_calculation_type(self, calculation_type: str):
        """
        Change the calculation type and reset to new defaults

        Args:
            calculation_type: New calculation type
        """
        if calculation_type != self.calculation_type:
            self.calculation_type = calculation_type

            # Update default general params
            self.default_general_params = FRESCO_NAMELIST.DEFAULT_GENERAL_PARAMS.get(
                calculation_type,
                FRESCO_NAMELIST.DEFAULT_GENERAL_PARAMS["default"]
            )

            # If we have input file parameters, re-apply them with new defaults
            if self.input_file_parameters:
                self.update_from_input_file(self.input_file_parameters)
            else:
                self.reset_to_default()


def parse_fresco_input_parameters(input_text: str) -> Set[str]:
    """
    Parse FRESCO input file text and extract parameter names from the &FRESCO namelist

    Args:
        input_text: Content of FRESCO input file

    Returns:
        Set of parameter names found in the &FRESCO namelist
    """
    import re

    parameters_found = set()

    # Find &FRESCO namelist section
    fresco_pattern = r'&FRESCO\s+(.*?)\s*/'
    match = re.search(fresco_pattern, input_text, re.DOTALL | re.IGNORECASE)

    if match:
        namelist_content = match.group(1)

        # Extract parameter assignments (param=value)
        # Handle various formats: param=value, param = value, param=value,value2
        param_pattern = r'(\w+)\s*='
        param_matches = re.finditer(param_pattern, namelist_content)

        for match in param_matches:
            param_name = match.group(1).lower()
            # Only include if it's a valid FRESCO parameter
            if param_name in FRESCO_NAMELIST.parameters:
                parameters_found.add(param_name)

    return parameters_found


def detect_calculation_type(input_text: str) -> str:
    """
    Automatically detect the type of FRESCO calculation from input file

    Args:
        input_text: Content of FRESCO input file

    Returns:
        Calculation type: "elastic", "inelastic", "transfer", or "default"
    """
    import re

    # Count namelists
    partition_count = len(re.findall(r'&PARTITION', input_text, re.IGNORECASE))
    states_count = len(re.findall(r'&STATES', input_text, re.IGNORECASE))
    coupling_count = len(re.findall(r'&COUPLING', input_text, re.IGNORECASE))
    overlap_count = len(re.findall(r'&OVERLAP', input_text, re.IGNORECASE))

    # Detection logic
    if overlap_count > 0:
        # Has OVERLAP namelists → Transfer reaction
        return "transfer"
    elif coupling_count > 0 and partition_count == 1:
        # Has COUPLING but only one PARTITION → Inelastic scattering
        return "inelastic"
    elif partition_count == 1 and states_count <= 2 and coupling_count == 0:
        # Single PARTITION, 1-2 STATES, no COUPLING → Elastic scattering
        return "elastic"
    elif partition_count > 1:
        # Multiple PARTITIONs without OVERLAP → could be transfer, default to transfer
        return "transfer"
    else:
        # Unable to determine, use default
        return "default"
