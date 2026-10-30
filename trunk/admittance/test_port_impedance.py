"""Regression check for the WSCC GFOR port response."""

from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from MosaicEngine.AdmittanceCalculation.port_impedance import responses


def test_wscc_gfor_port_at_one_hertz():
    admittance, impedance, name = responses(np.array([1.0]), bus=4)
    assert name == "WSCC GFOR1"
    assert admittance.shape == impedance.shape == (1, 2, 2)
    assert np.all(np.isfinite(admittance))
    assert np.all(np.isfinite(impedance))
    np.testing.assert_allclose(admittance[0, 0, 0],
                               -0.71688 + 0.067244j, rtol=2e-4, atol=2e-4)
    np.testing.assert_allclose(impedance[0, 0, 0],
                               0.057024 + 0.008146j, rtol=2e-4, atol=2e-4)
