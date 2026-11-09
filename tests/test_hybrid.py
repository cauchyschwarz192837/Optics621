"""Independent electrostatic symmetry and potential-bounds checks."""
import unittest
import numpy as np
from hybrid.source import bias
class HybridBiasTests(unittest.TestCase):
    def test_symmetric_electrodes(self):
        x=(np.arange(80)-39.5)*.1
        z=(np.arange(65)-39.5)*.1
        v,ex,ez=bias(x,z,4)
        np.testing.assert_allclose(v,-v[:,::-1],atol=1e-9)
        self.assertLessEqual(abs(v).max(),.500000001)
        self.assertLess(ex[np.argmin(abs(z-1.25)),40],0.)
