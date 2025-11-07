#!/usr/bin/env python3
"""Test POT parsing"""

import sys
sys.path.insert(0, '/Users/jinlei/code/fresco_gui/fresco_gui')

from parameter_manager import parse_pot_namelists

# Read the input file
with open('/Users/jinlei/Downloads/fresco-09-KoningDR-s1-E001.000.in', 'r') as f:
    input_text = f.read()

# Parse POTs
pot_list = parse_pot_namelists(input_text)

print(f"Found {len(pot_list)} POT namelists:\n")

for i, pot in enumerate(pot_list, 1):
    print(f"POT #{i}:")
    for key, value in sorted(pot.items()):
        print(f"  {key} = {value}")
    print()
