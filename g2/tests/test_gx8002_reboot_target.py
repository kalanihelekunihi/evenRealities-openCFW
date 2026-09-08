# SPDX-License-Identifier: MIT
import sys
import json
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_reboot import execute, verify

class RebootInterpreterTests(unittest.TestCase):
    def test_report_json_roundtrip(self):
        report=verify()
        self.assertEqual(report,json.loads(json.dumps(report)))

    def test_only_self_loop_is_terminal(self):
        with self.assertRaisesRegex(ValueError,'unexpected branch'):
            execute({0:('br','0x2',2)},0,0)
    def test_unexpected_call(self):
        with self.assertRaisesRegex(ValueError,'unexpected call'):
            execute({0:('bsr','0x1234',4)},0,0)
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:('bkpt','',2)},0,0)

if __name__=='__main__':unittest.main()
