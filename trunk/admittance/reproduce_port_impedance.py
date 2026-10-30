"""Print the self-contained Mosaic port responses for WSCC buses 4 and 6."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from MosaicEngine.AdmittanceCalculation.port_impedance import responses


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bus", type=int, choices=(4, 6), default=4)
    parser.add_argument("--nonlinear-converters", action="store_true")
    parser.add_argument("--frequencies", type=float, nargs="+", default=[1, 10, 100, 1000])
    args = parser.parse_args()
    frequencies = np.asarray(args.frequencies, dtype=float)
    device_admittance, grid_impedance, name = responses(
        frequencies, bus=args.bus, nonlinear_converters=args.nonlinear_converters)
    for frequency, admittance, impedance in zip(frequencies, device_admittance, grid_impedance):
        print(f"{name} at bus {args.bus}, {frequency:g} Hz")
        print("  converter Y_qd (injected current / voltage):",
              np.array2string(admittance, precision=6))
        print("  grid Z_qd (voltage / injected current):",
              np.array2string(impedance, precision=6))


if __name__ == "__main__":
    main()
