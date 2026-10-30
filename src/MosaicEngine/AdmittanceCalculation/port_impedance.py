"""WSCC device admittance and remaining-grid impedance in qd coordinates."""

from __future__ import annotations

import numpy as np
from scipy.optimize import root
import VeraGridEngine.api as gce
from VeraGridEngine.enumerations import DeviceType
from VeraGridEngine.Simulations.PowerFlow.power_flow_driver import PowerFlowDriver, PowerFlowOptions
from VeraGridEngine.Simulations.Rms.rms_options import RmsOptions
from VeraGridEngine.Simulations.SmallSignalStabilityRms.small_signal_driver import SmallSignalStabilityRmsDriver
from VeraGridEngine.Simulations.SmallSignalStabilityRms.small_signal_options import RmsSmallSignalStabilityOptions

from MosaicData.models.wscc_case import build_wscc_grid
from .rms_port_analysis import (compute_device_admittance,
                                compute_grid_impedance_at_device_port, prepare_port)


def power_flow_options():
    return PowerFlowOptions(
        solver_type=gce.SolverType.NR, retry_with_other_methods=False,
        tolerance=1e-10, max_iter=50, control_q=False,
        control_taps_modules=False, control_taps_phase=False,
        control_remote_voltage=False, distributed_slack=False,
        initialize_angles=True, use_stored_guess=False, verbose=0,
    )


def responses(frequencies_hz, bus: int = 4, *, nonlinear_converters: bool = False):
    """Return (device Y_qd, grid Z_qd, device name) at WSCC bus 4 or 6."""

    frequencies_hz = np.asarray(frequencies_hz, dtype=float)
    if frequencies_hz.ndim != 1 or not np.all(np.isfinite(frequencies_hz)):
        raise ValueError("frequencies_hz must be a finite one-dimensional array")
    if bus not in (4, 6):
        raise ValueError("WSCC converter bus must be 4 or 6")

    grid = build_wscc_grid(dynamic_lines=True, full_dynamic_network=True,
                                 nonlinear_converters=nonlinear_converters)
    power_flow = PowerFlowDriver(grid, power_flow_options())
    power_flow.run()
    driver = SmallSignalStabilityRmsDriver(
        grid, rms_options=RmsOptions(time_step=.001),
        sss_options=RmsSmallSignalStabilityOptions(ss_assessment_time=0),
        pf_results=power_flow.results,
    )
    # The Mosaic RMS initializer does not seed every dynamic network state.
    # Refine its power-flow-based guess to a true DAE equilibrium before
    # forming the frequency-domain linearization.
    problem = driver.problem
    x0, dx0 = problem.get_x0(), problem.get_dx0()
    def residual(x):
        return np.concatenate((problem.rhs_state(x, dx0),
                               problem.rhs_algebraic(x, dx0)))
    if np.max(np.abs(residual(x0))) > 1e-7:
        solution = root(residual, x0, method="hybr", options={"maxfev": 1000})
        error = np.max(np.abs(residual(solution.x)))
        if not np.isfinite(error) or error > 1e-7:
            raise RuntimeError(f"WSCC RMS equilibrium failed to converge: {error:g}")
        for variable, value in zip((*problem.state_vars, *problem.algebraic_vars), solution.x):
            problem.init_guess[variable.uid] = float(value)
    selected_bus = next((item for item in grid.buses if item.name == f"Bus{bus}"), None)
    if selected_bus is None:
        raise ValueError(f"Bus {bus} is not in the WSCC circuit")
    generators = grid.get_injection_devices_grouped_by_bus().get(selected_bus, {}).get(
        DeviceType.GeneratorDevice, [])
    if len(generators) != 1:
        raise ValueError(f"Expected one generator at Bus{bus}; found {len(generators)}")
    port = prepare_port(driver, generators[0])
    return (compute_device_admittance(port, frequencies_hz),
            compute_grid_impedance_at_device_port(port, frequencies_hz),
            generators[0].name)
