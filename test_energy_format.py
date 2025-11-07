#!/usr/bin/env python3
"""Test energy format generation"""

# Simulate the energy widget behavior
def get_fresco_format_single(energy):
    """Single energy format"""
    return f"elab={energy:.3f}"

def get_fresco_format_multiple(boundaries, intervals):
    """Multiple energies - array format"""
    elab_values = " ".join(f"{e:.3f}" for e in boundaries)
    nlab_values = " ".join(str(n) for n in intervals)
    n_boundaries = len(boundaries)
    n_intervals = len(intervals)
    return f"elab(1:{n_boundaries})={elab_values}  nlab(1:{n_intervals})={nlab_values}"

# Test cases
print("Single energy:")
print(get_fresco_format_single(30.0))
print()

print("Multiple energies (like B1 example):")
print(get_fresco_format_multiple([6.9, 11.0, 49.35], [1, 1]))
print()

# Test namelist insertion
namelist_before = """ &FRESCO
     hcm=0.1 rmatch=60 jtmax=50
 /"""

energy_string = get_fresco_format_multiple([6.9, 11.0, 49.35], [1, 1])
namelist_after = namelist_before.rsplit('/', 1)[0] + f"\n     {energy_string} /\n"

print("Namelist after insertion:")
print(namelist_after)
