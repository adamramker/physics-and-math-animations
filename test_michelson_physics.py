"""Independent physical checkpoints; no graphics dependencies required."""
import math
import unittest
from michelson_physics import michelson_readout


class MichelsonPhysicsTests(unittest.TestCase):
    def test_equal_arms_return_all_light_to_source(self):
        result = michelson_readout(0, input_intensity=2.5)
        self.assertEqual(result.path_difference_nm, 0)
        self.assertAlmostEqual(result.detector_intensity, 0)
        self.assertAlmostEqual(result.source_return_intensity, 2.5)

    def test_quarter_wavelength_motion_swaps_ports(self):
        result = michelson_readout(632.8 / 4)
        self.assertAlmostEqual(result.path_difference_nm, 632.8 / 2)
        self.assertAlmostEqual(result.detector_intensity, 1)
        self.assertAlmostEqual(result.source_return_intensity, 0)

    def test_half_wavelength_motion_completes_one_fringe(self):
        result = michelson_readout(632.8 / 2)
        self.assertAlmostEqual(result.detector_intensity, 0)
        self.assertAlmostEqual(result.source_return_intensity, 1)

    def test_initial_optical_offset(self):
        result = michelson_readout(0, initial_path_difference_nm=632.8 / 4)
        self.assertAlmostEqual(result.detector_intensity, 0.5)
        self.assertAlmostEqual(result.source_return_intensity, 0.5)

    def test_energy_conservation_over_positive_and_negative_motion(self):
        for index in range(-200, 201):
            result = michelson_readout(index * 13.7, input_intensity=3.4)
            self.assertGreaterEqual(result.detector_intensity, 0)
            self.assertGreaterEqual(result.source_return_intensity, 0)
            self.assertAlmostEqual(
                result.detector_intensity + result.source_return_intensity, 3.4
            )

    def test_invalid_parameters(self):
        for kwargs in ({"wavelength_nm": 0}, {"input_intensity": -1},
                       {"displacement_nm": math.nan},
                       {"initial_path_difference_nm": math.inf}):
            args = {"displacement_nm": 0}
            args.update(kwargs)
            with self.assertRaises(ValueError):
                michelson_readout(**args)


if __name__ == "__main__":
    unittest.main()
