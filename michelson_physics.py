"""Ideal lossless Michelson model. All distances are in nm.

The chosen port convention has a dark detector at equal optical arm lengths.
The source output is the returning beam, excluding the incident beam.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Readout:
    displacement_nm: float
    path_difference_nm: float
    phase_rad: float
    detector_intensity: float
    source_return_intensity: float


def michelson_readout(
    displacement_nm, wavelength_nm=632.8, input_intensity=1.0,
    initial_path_difference_nm=0.0,
):
    """Return time-averaged intensities for equal-area, coherent beams.

    Assumptions: air/vacuum arms, ideal mirrors, a lossless 50:50 splitter,
    perfect spatial/polarization overlap, and quasi-static mirror motion.
    initial_path_difference_nm is the *round-trip* optical path difference.
    """
    values = (displacement_nm, wavelength_nm, input_intensity,
              initial_path_difference_nm)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("All parameters must be finite")
    if wavelength_nm <= 0 or input_intensity < 0:
        raise ValueError("Wavelength must be positive and intensity nonnegative")
    delta = initial_path_difference_nm + 2.0 * displacement_nm
    phase = math.tau * delta / wavelength_nm
    detector = input_intensity * math.sin(phase / 2.0) ** 2
    source_return = input_intensity * math.cos(phase / 2.0) ** 2
    return Readout(displacement_nm, delta, phase, detector, source_return)
