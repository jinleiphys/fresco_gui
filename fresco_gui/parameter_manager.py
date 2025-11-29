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


def parse_fresco_parameter_values(input_text: str) -> Dict[str, Any]:
    """
    Parse FRESCO input file and extract parameter values from the &FRESCO namelist

    Args:
        input_text: Content of FRESCO input file

    Returns:
        Dictionary of parameter names to their values
    """
    import re

    parameter_values = {}

    # Find &FRESCO namelist section (case insensitive, also handle &Fresco)
    fresco_pattern = r'&FRESCO\s+(.*?)\s*/'
    match = re.search(fresco_pattern, input_text, re.DOTALL | re.IGNORECASE)

    if match:
        namelist_content = match.group(1)

        # Extract parameter assignments: param=value or param = value
        # Value can be numbers, strings, or comma-separated lists
        param_pattern = r'(\w+)\s*=\s*([^,\s]+(?:\s*,\s*[^,\s]+)*)'
        param_matches = re.finditer(param_pattern, namelist_content)

        for match in param_matches:
            param_name = match.group(1).lower()
            param_value_str = match.group(2).strip()

            # Only process if it's a valid FRESCO parameter
            if param_name in FRESCO_NAMELIST.parameters:
                # Try to parse the value
                try:
                    # Check if it's a number (int or float)
                    if '.' in param_value_str or 'e' in param_value_str.lower():
                        param_value = float(param_value_str)
                    else:
                        param_value = int(param_value_str)
                except ValueError:
                    # If not a number, keep as string (remove quotes if present)
                    param_value = param_value_str.strip("'\"")

                parameter_values[param_name] = param_value

    return parameter_values


def parse_partition_namelist(input_text: str) -> dict:
    """
    Parse the first &PARTITION namelist to extract projectile and target information

    Args:
        input_text: Content of FRESCO input file

    Returns:
        Dictionary with keys: namep, massp, zp, jp, namet, masst, zt, jt
    """
    import re

    partition_info = {}

    # Find first &PARTITION namelist
    pattern = r'&PARTITION\s+(.*?)\s*/'
    match = re.search(pattern, input_text, re.DOTALL | re.IGNORECASE)

    if match:
        namelist_content = match.group(1)

        # Extract each parameter
        params_to_extract = {
            'namep': str,
            'massp': float,
            'zp': float,
            'jp': float,
            'namet': str,
            'masst': float,
            'zt': float,
            'jt': float,
        }

        for param_name, param_type in params_to_extract.items():
            # Pattern to match parameter=value
            # Handle both quoted strings and unquoted values
            if param_type == str:
                # For strings, match quoted values (with anything inside quotes) or unquoted values
                param_pattern = rf'{param_name}\s*=\s*(["\'])(.*?)\1|{param_name}\s*=\s*([^\s,]+)'
            else:
                # For numbers, match unquoted numeric values
                param_pattern = rf'{param_name}\s*=\s*([^\s,]+)'

            param_match = re.search(param_pattern, namelist_content, re.IGNORECASE)

            if param_match:
                try:
                    if param_type == str:
                        # For quoted strings, group(2) has the content
                        # For unquoted strings, group(3) has the content
                        value_str = param_match.group(2) if param_match.group(2) is not None else param_match.group(3)
                        if value_str:
                            partition_info[param_name] = value_str.strip()
                    else:
                        value_str = param_match.group(1).strip()
                        partition_info[param_name] = param_type(value_str)
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Could not parse {param_name}: {e}")

    return partition_info


def parse_all_partition_namelists(input_text: str) -> list:
    """
    Parse all &PARTITION namelists from FRESCO input file

    Args:
        input_text: Content of FRESCO input file

    Returns:
        List of dictionaries, each containing partition parameters
    """
    import re

    partition_list = []

    # Find all &PARTITION namelists (but not the terminator)
    pattern = r'&PARTITION\s+(.*?)\s*/'
    matches = re.findall(pattern, input_text, re.DOTALL | re.IGNORECASE)

    for namelist_content in matches:
        # Skip empty namelists (terminators)
        if not namelist_content.strip():
            continue

        partition_info = {}

        # Extract each parameter
        params_to_extract = {
            'namep': str,
            'massp': float,
            'zp': float,
            'jp': float,
            'namet': str,
            'masst': float,
            'zt': float,
            'jt': float,
            'qval': float,
            'nex': int,
        }

        for param_name, param_type in params_to_extract.items():
            # Pattern to match parameter=value
            if param_type == str:
                # For strings, match quoted values or unquoted values
                param_pattern = rf'{param_name}\s*=\s*(["\'])(.*?)\1|{param_name}\s*=\s*([^\s,]+)'
            else:
                # For numbers, match unquoted numeric values
                param_pattern = rf'{param_name}\s*=\s*([^\s,]+)'

            param_match = re.search(param_pattern, namelist_content, re.IGNORECASE)

            if param_match:
                try:
                    if param_type == str:
                        # For quoted strings, group(2) has the content
                        # For unquoted strings, group(3) has the content
                        value_str = param_match.group(2) if param_match.group(2) is not None else param_match.group(3)
                        if value_str:
                            partition_info[param_name] = value_str.strip()
                    else:
                        value_str = param_match.group(1).strip()
                        partition_info[param_name] = param_type(value_str)
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Could not parse {param_name}: {e}")

        partition_list.append(partition_info)

    return partition_list


def parse_pot_namelists(input_text: str) -> list:
    """
    Parse all &POT namelists from FRESCO input file

    Args:
        input_text: Content of FRESCO input file

    Returns:
        List of dictionaries, each containing POT parameters
    """
    import re

    pot_list = []

    # Find all &POT namelists
    pattern = r'&POT\s+(.*?)\s*/'
    matches = re.findall(pattern, input_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        # Skip empty POT namelists (only whitespace)
        if not match.strip():
            continue

        pot_params = {}

        # Parse simple parameters (kp, type, shape, ap, at, rc)
        simple_params = {
            'kp': int,
            'type': int,
            'shape': int,
            'ap': float,
            'at': float,
            'rc': float,
        }

        for param_name, param_type in simple_params.items():
            param_pattern = rf'{param_name}\s*=\s*([^\s,]+)'
            param_match = re.search(param_pattern, match, re.IGNORECASE)

            if param_match:
                value_str = param_match.group(1).strip()
                try:
                    pot_params[param_name] = param_type(value_str)
                except ValueError:
                    print(f"Warning: Could not parse POT {param_name}={value_str}")

        # Parse p(1:n) array syntax: p(1:3)= 51.2614 1.2131 0.6646
        p_array_pattern = r'p\(1:(\d+)\)\s*=\s*([\d\.\-\s]+)'
        p_match = re.search(p_array_pattern, match, re.IGNORECASE)

        if p_match:
            num_params = int(p_match.group(1))
            values_str = p_match.group(2).strip()
            # Split values by whitespace
            values = values_str.split()

            # Assign to p1, p2, p3, etc.
            for i, value_str in enumerate(values[:num_params], start=1):
                try:
                    pot_params[f'p{i}'] = float(value_str)
                except ValueError:
                    print(f"Warning: Could not parse POT p{i}={value_str}")
        else:
            # Also try parsing individual p1=, p2=, p3= if array syntax not found
            for i in range(1, 7):
                param_pattern = rf'p{i}\s*=\s*([^\s,]+)'
                param_match = re.search(param_pattern, match, re.IGNORECASE)
                if param_match:
                    try:
                        pot_params[f'p{i}'] = float(param_match.group(1).strip())
                    except ValueError:
                        pass

        if pot_params:  # Only add if we found any parameters
            pot_list.append(pot_params)

    return pot_list


def parse_states_namelists(input_text: str) -> list:
    """
    Parse all &STATES namelists from FRESCO input file

    Args:
        input_text: Content of FRESCO input file

    Returns:
        List of dictionaries, each containing STATES parameters
    """
    import re

    states_list = []

    # Find all &STATES namelists
    pattern = r'&STATES\s+(.*?)\s*/'
    matches = re.findall(pattern, input_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        # Skip empty STATES namelists
        if not match.strip():
            continue

        states_params = {}

        # Parse all possible parameters
        params_to_extract = {
            'jp': float,
            'copyp': int,
            'bandp': int,
            'ep': float,
            'kkp': float,
            'tp': float,
            'jt': float,
            'copyt': int,
            'bandt': int,
            'et': float,
            'kkt': float,
            'tt': float,
            'kp': int,
            'cpot': int,
        }

        for param_name, param_type in params_to_extract.items():
            param_pattern = rf'{param_name}\s*=\s*([^\s,]+)'
            param_match = re.search(param_pattern, match, re.IGNORECASE)

            if param_match:
                try:
                    value_str = param_match.group(1).strip()
                    states_params[param_name] = param_type(value_str)
                except (ValueError, AttributeError):
                    pass

        # Parse boolean parameters
        bool_params = ['fexch', 'ignore']
        for param_name in bool_params:
            param_pattern = rf'{param_name}\s*=\s*([TF])'
            param_match = re.search(param_pattern, match, re.IGNORECASE)
            if param_match:
                states_params[param_name] = param_match.group(1).upper() == 'T'

        if states_params:
            states_list.append(states_params)

    return states_list


def parse_coupling_namelists(input_text: str) -> list:
    """
    Parse all &COUPLING namelists from FRESCO input file

    Args:
        input_text: Content of FRESCO input file

    Returns:
        List of dictionaries, each containing COUPLING parameters
    """
    import re

    coupling_list = []

    # Find all &COUPLING namelists
    pattern = r'&COUPLING\s+(.*?)\s*/'
    matches = re.findall(pattern, input_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        # Skip empty COUPLING namelists
        if not match.strip():
            continue

        coupling_params = {}

        # Parse all possible parameters
        params_to_extract = {
            'kind': int,
            'icfrom': int,
            'icto': int,
            'iafrom': int,
            'iato': int,
            'ip1': int,
            'ip2': int,
            'ip3': int,
            'lambda': int,
            'jbeta': float,
        }

        for param_name, param_type in params_to_extract.items():
            param_pattern = rf'{param_name}\s*=\s*([^\s,]+)'
            param_match = re.search(param_pattern, match, re.IGNORECASE)

            if param_match:
                try:
                    value_str = param_match.group(1).strip()
                    coupling_params[param_name] = param_type(value_str)
                except (ValueError, AttributeError):
                    pass

        if coupling_params:
            coupling_list.append(coupling_params)

    # Parse CFP namelists and attach to the last coupling (for transfer reactions)
    cfp_list = parse_cfp_namelists(input_text)
    if cfp_list and coupling_list:
        # Attach CFP list to the last coupling (typically the transfer coupling)
        coupling_list[-1]['cfp_list'] = cfp_list

    return coupling_list


def parse_cfp_namelists(input_text: str) -> list:
    """
    Parse all &CFP namelists from FRESCO input file

    Args:
        input_text: Content of FRESCO input file

    Returns:
        List of dictionaries, each containing CFP parameters
    """
    import re

    cfp_list = []

    # Find all &CFP namelists
    pattern = r'&CFP\s+(.*?)\s*/'
    matches = re.findall(pattern, input_text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        # Skip empty CFP namelists (terminating &CFP /)
        if not match.strip():
            continue

        cfp_params = {}

        # Parse all CFP parameters
        params_to_extract = {
            'in': int,
            'ib': int,
            'ia': int,
            'kn': int,
            'a': float,
        }

        for param_name, param_type in params_to_extract.items():
            param_pattern = rf'{param_name}\s*=\s*([^\s,]+)'
            param_match = re.search(param_pattern, match, re.IGNORECASE)

            if param_match:
                try:
                    value_str = param_match.group(1).strip()
                    cfp_params[param_name] = param_type(value_str)
                except (ValueError, AttributeError):
                    pass

        if cfp_params:
            cfp_list.append(cfp_params)

    return cfp_list


def detect_calculation_type(input_text: str) -> str:
    """
    Automatically detect the type of FRESCO calculation from input file

    Args:
        input_text: Content of FRESCO input file

    Returns:
        Calculation type: "elastic", "inelastic", "transfer", or "default"
    """
    import re

    # Find all namelists with their content (not just empty markers)
    # Pattern: &NAMELIST ... / (with content between)
    def has_content_namelist(namelist_name, text):
        """Check if a namelist has actual content (not just &NAME /)"""
        pattern = rf'&{namelist_name}\s+(.*?)\s*/'
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        # Check if any match has non-whitespace content
        return any(match.strip() for match in matches)

    def count_content_namelists(namelist_name, text):
        """Count namelists with actual content"""
        pattern = rf'&{namelist_name}\s+(.*?)\s*/'
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        # Count only those with non-whitespace content
        return sum(1 for match in matches if match.strip())

    # Count namelists with actual content
    partition_count = count_content_namelists('PARTITION', input_text)
    states_count = count_content_namelists('STATES', input_text)
    has_coupling = has_content_namelist('COUPLING', input_text)
    has_overlap = has_content_namelist('OVERLAP', input_text)

    # Detection logic
    # Key insight: Number of STATES is the most important indicator:
    # - Elastic: 1 STATE (ground state only)
    # - Inelastic: 2+ STATES (ground + excited states)
    # - Transfer: Multiple PARTITIONs or has OVERLAP

    if has_overlap:
        # Has non-empty OVERLAP → Transfer reaction
        return "transfer"
    elif partition_count > 1:
        # Multiple PARTITIONs → Transfer reaction
        return "transfer"
    elif states_count >= 2:
        # Multiple STATES (ground + excited) → Inelastic scattering
        # Note: COUPLING may be empty in the input file but still inelastic
        return "inelastic"
    elif partition_count == 1 and states_count == 1:
        # Single PARTITION, single STATE → Elastic scattering
        return "elastic"
    else:
        # Unable to determine, use default
        return "default"


def parse_overlap_namelists(input_text: str) -> List[Dict[str, Any]]:
    """
    Parse &OVERLAP namelists from FRESCO input file

    Returns:
        List of dictionaries containing overlap parameters
    """
    import re

    overlaps = []

    # Find all &OVERLAP namelists (including empty ones as terminators)
    pattern = r'&OVERLAP\s*(.*?)\s*/'
    matches = re.findall(pattern, input_text, re.IGNORECASE | re.DOTALL)

    for match_text in matches:
        # Skip empty namelists (terminators)
        if not match_text.strip():
            continue

        overlap_data = {}

        # Parse key=value pairs
        # Handle both integers, floats, and strings
        kv_pattern = r'(\w+)\s*=\s*([^,\s]+)'
        kv_matches = re.findall(kv_pattern, match_text, re.IGNORECASE)

        for key, value in kv_matches:
            key_lower = key.lower()

            # Remove quotes from string values
            value_clean = value.strip().strip("'\"")

            # Convert to appropriate type
            try:
                # Try integer first
                if '.' not in value_clean:
                    overlap_data[key_lower] = int(value_clean)
                else:
                    # Float
                    overlap_data[key_lower] = float(value_clean)
            except ValueError:
                # Keep as string (e.g., CH1)
                overlap_data[key_lower] = value_clean

        # Handle two-particle specific parameters (npairs, lmin, lmax, smin, etc.)
        # Map to standard names used in widget
        if 'npairs' in overlap_data:
            overlap_data['nn'] = overlap_data.pop('npairs')
        if 'lmin' in overlap_data:
            overlap_data['l'] = overlap_data.pop('lmin')
        if 'smin' in overlap_data:
            overlap_data['sn'] = overlap_data.pop('smin')
        # Map 'j' to 'jn' (FRESCO sometimes uses 'j' instead of 'jn')
        if 'j' in overlap_data:
            overlap_data['jn'] = overlap_data.pop('j')
        if 'j12' in overlap_data:
            overlap_data['jn'] = overlap_data.pop('j12')
        if 't' in overlap_data:
            overlap_data['kbpot'] = overlap_data.pop('t')
        if 'knzr' in overlap_data:
            overlap_data['krpot'] = overlap_data.pop('knzr')
        if 'eps' in overlap_data:
            overlap_data['be'] = overlap_data.pop('eps')

        # Set defaults for missing parameters
        if 'kn1' not in overlap_data:
            overlap_data['kn1'] = 1
        if 'kn2' not in overlap_data:
            overlap_data['kn2'] = 0
        if 'ic1' not in overlap_data:
            overlap_data['ic1'] = 1
        if 'ic2' not in overlap_data:
            overlap_data['ic2'] = 2
        if 'in' not in overlap_data:
            overlap_data['in'] = 1
        if 'kind' not in overlap_data:
            overlap_data['kind'] = 0
        if 'ch1' not in overlap_data:
            overlap_data['ch1'] = 'A'
        if 'nn' not in overlap_data:
            overlap_data['nn'] = 1
        if 'l' not in overlap_data:
            overlap_data['l'] = 0
        if 'lmax' not in overlap_data:
            overlap_data['lmax'] = 0
        if 'sn' not in overlap_data:
            overlap_data['sn'] = 0.5
        if 'ia' not in overlap_data:
            overlap_data['ia'] = 1
        if 'jn' not in overlap_data:
            overlap_data['jn'] = 0.5
        if 'ib' not in overlap_data:
            # For kind=0 (one-body), ib defaults to 0
            # For kind>=3 (stripping/pickup), ib defaults to 1
            overlap_data['ib'] = 0 if overlap_data.get('kind', 0) == 0 else 1
        if 'kbpot' not in overlap_data:
            overlap_data['kbpot'] = 1
        if 'krpot' not in overlap_data:
            overlap_data['krpot'] = 0
        if 'be' not in overlap_data:
            overlap_data['be'] = 2.224
        if 'isc' not in overlap_data:
            overlap_data['isc'] = 0
        if 'ipc' not in overlap_data:
            overlap_data['ipc'] = 1
        if 'nfl' not in overlap_data:
            overlap_data['nfl'] = 0
        if 'nam' not in overlap_data:
            overlap_data['nam'] = 0
        if 'ampl' not in overlap_data:
            overlap_data['ampl'] = 1.0

        overlaps.append(overlap_data)

    return overlaps
