import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_callback_facades.py"
S = importlib.util.spec_from_file_location("g2_callback_facades", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2CallbackFacadesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_parallel_complete_objects(self):
        self.assertEqual(set(self.report["modules"]), {"charge", "msg_notif"})
        for module in self.report["modules"].values():
            self.assertEqual(
                (module["linked_functions"], module["ghidra_discovered_functions"],
                 module["restored_functions"], module["body_bytes"],
                 module["physical_bytes"], module["reachable_instructions"],
                 module["direct_body_calls"], module["direct_bl_entry_sites"]),
                (5, 2, 3, 190, 224, 78, 15, 7),
            )

    def test_callback_lists_and_types(self):
        charge = self.report["modules"]["charge"]
        msg = self.report["modules"]["msg_notif"]
        self.assertEqual((charge["callback_list_address"], charge["callback_type"]), (0x20073F78, "BAT_INFO"))
        self.assertEqual((msg["callback_list_address"], msg["callback_type"]), (0x20073F84, "MSG_COUNT"))

    def test_no_hidden_rtos_or_third_party_definition(self):
        a = self.report["aggregate"]
        self.assertEqual((a["easylogger_calls"], a["generic_callback_manager_calls"], a["direct_cmsis_freertos_calls"]), (20, 10, 0))
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])
        self.assertFalse(a["new_version_discriminator"])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
