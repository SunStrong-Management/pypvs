# tests/test_greet.py
import unittest

from pypvs.pvs import get_sn


class TestGetSN(unittest.TestCase):
    def test_pvs(self):
        self.assertEqual(get_sn(), "Serial number: 123456")


if __name__ == "__main__":
    unittest.main()
