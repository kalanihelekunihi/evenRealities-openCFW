# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_putf_boundary import execute, programs


class PutfBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=programs()[1]

    def test_eof_failure(self):
        self.assertEqual(execute(self.code,0x10206998,0x10206c70,0x3000,10,0xffffffff),
                         (0,[(10,0x3000)]))

    def test_other_negative_result_is_success(self):
        self.assertEqual(execute(self.code,0x10206998,0x10206c70,0x3000,255,0x80000000),
                         (1,[(255,0x3000)]))

    def test_wrong_fputc_target(self):
        with self.assertRaisesRegex(ValueError,'target'):
            execute(self.code,0x10206998,0x10206c74,0x3000,10,10)
