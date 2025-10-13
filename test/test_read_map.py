import unittest
import numpy as np
from read_map import convert_image_to_map

class TestReadMap(unittest.TestCase):
    def test_read_map_1(self):
        map_path = "maps/map_1.png"
        result_map, result_destination = convert_image_to_map(map_path, DEBUG_MODE=False)
        expected_map = np.array([
            [0., 0., 1., 1., 1., 1., 1., 0.],
            [1., 1., 1., 0., 0., 0., 1., 0.],
            [1., 0., 3., 0., 1., 0., 1., 1.],
            [1., 0., 1., 0., 0., 0., 0., 1.],
            [1., 0., 0., 0., 0., 1., 0., 1.],
            [1., 1., 0., 1., 0., 0., 0., 1.],
            [0., 1., 2., 0., 0., 1., 1., 1.],
            [0., 1., 1., 1., 1., 1., 0., 0.]
        ])
        expected_destination = [(3, 5)]
        np.testing.assert_array_equal(result_map, expected_map)
        self.assertEqual(result_destination, expected_destination)
        
    def test_read_map_3(self):
        map_path = "maps/map_3.png"
        result_map, result_destination = convert_image_to_map(map_path, DEBUG_MODE=False)
        expected_map = np.array([
            [0., 0., 1., 1., 1., 1., 1., 0.,],
            [1., 1., 1., 0., 0., 0., 1., 0.,],
            [1., 0., 3., 0., 1., 0., 1., 1.,],
            [1., 0., 1., 0., 0., 0., 0., 1.,],
            [1., 0., 0., 0., 0., 1., 0., 1.,],
            [1., 1., 3., 1., 0., 3., 0., 1.,],
            [0., 1., 2., 0., 0., 1., 1., 1.,],
            [0., 1., 1., 1., 1., 1., 0., 0.,],
        ])
        expected_destination = [(3, 5), (4, 2), (5, 4)]
        np.testing.assert_array_equal(result_map, expected_map)
        self.assertEqual(result_destination, expected_destination)
        
if __name__ == "__main__":
    unittest.main()