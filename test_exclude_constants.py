#!/usr/bin/env python3
"""Test that finec and hbarc are excluded from &FRESCO namelist"""

import sys
sys.path.insert(0, 'fresco_gui')

from fresco_namelist import FRESCO_NAMELIST

# Test data - simulate parameter values including finec and hbarc
test_params = {
    'hcm': 0.1,
    'rmatch': 60.0,
    'jtmax': 50.0,
    'absend': 0.001,
    'finec': 137.036,  # This should be excluded
    'hbarc': 197.327,  # This should be excluded
    'iter': 1,
    'chans': 1,
    'smats': 2,
    'xstabl': 1
}

print("Test parameters:")
for k, v in test_params.items():
    print(f"  {k} = {v}")

print("\nGenerating namelist...")
namelist_text = FRESCO_NAMELIST.generate_namelist_text(test_params)

print("\nGenerated namelist:")
print(namelist_text)

# Check if finec or hbarc appear in the namelist
print("\n" + "="*60)
print("VERIFICATION:")
print("="*60)

has_finec = 'finec' in namelist_text.lower()
has_hbarc = 'hbarc' in namelist_text.lower()

if has_finec:
    print("❌ FAIL: 'finec' found in namelist (should be excluded)")
else:
    print("✅ PASS: 'finec' not in namelist (correctly excluded)")

if has_hbarc:
    print("❌ FAIL: 'hbarc' found in namelist (should be excluded)")
else:
    print("✅ PASS: 'hbarc' not in namelist (correctly excluded)")

if not has_finec and not has_hbarc:
    print("\n✅ SUCCESS: Both finec and hbarc are correctly excluded from &FRESCO namelist")
    sys.exit(0)
else:
    print("\n❌ FAILURE: Physical constants still appearing in namelist")
    sys.exit(1)
