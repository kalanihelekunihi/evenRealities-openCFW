# SPDX-License-Identifier: MIT
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/extract_g2_pt_protocol_decomp.py"
SPEC = importlib.util.spec_from_file_location("extract_g2_pt", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PtProtocolDecompExtractionTests(unittest.TestCase):
    def test_parse_prefixed_log_and_reference(self):
        text = """INFO  CreateAndDumpFunctions.java> FUNCTION 0056f178 0056f178 0056f239 FUN_0056f178 (GhidraScript)
INFO  CreateAndDumpFunctions.java> REFERENCE 00400010 UNCONDITIONAL_CALL (GhidraScript)
INFO  CreateAndDumpFunctions.java> DECOMPILE_BEGIN (GhidraScript)
int FUN_0056f178(void)
{
  return 7;
}
INFO  CreateAndDumpFunctions.java> DECOMPILE_END (GhidraScript)
"""
        records = MODULE.parse_log(text)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["entry"], 0x0056F178)
        self.assertEqual(records[0]["body_max_inclusive"], 0x0056F239)
        self.assertEqual(records[0]["references"], [
            {"from": 0x00400010, "type": "UNCONDITIONAL_CALL"}
        ])
        self.assertTrue(records[0]["decompilation"].endswith("}\n"))


    def test_parse_rejects_duplicate_entries(self):
        item = """FUNCTION 0056f178 0056f178 0056f239 FUN_0056f178
DECOMPILE_BEGIN
int f(void) { return 0; }
DECOMPILE_END
"""
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.parse_log(item + item)


    def test_command_map_is_exact_and_unique(self):
        self.assertEqual(len(MODULE.COMMAND_HANDLERS), 66)
        self.assertEqual(len({item[0] for item in MODULE.COMMAND_HANDLERS}), 66)
        self.assertEqual(len({item[1] for item in MODULE.COMMAND_HANDLERS}), 66)
        self.assertEqual(MODULE.COMMAND_HANDLERS[0], (0x01, 0x0056FC0C))
        self.assertEqual(MODULE.COMMAND_HANDLERS[-1], (0xF3, 0x00577AFC))


if __name__ == "__main__":
    unittest.main()
