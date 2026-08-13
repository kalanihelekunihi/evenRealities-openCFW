import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "tools/analyze_g2_uart_sync.py"
S = importlib.util.spec_from_file_location("g2_uart_sync", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class G2UartSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = M.analyze()

    def test_complete_object_surface(self):
        s = self.report["surface"]
        self.assertEqual(
            (
                s["linked_functions"], s["ghidra_discovered_functions"],
                s["restored_functions"], s["path_anchored_functions"],
                s["raw_path_references"], s["raw_path_referencing_functions"],
                s["body_bytes"], s["physical_bytes"], s["outer_pool_bytes"],
                s["reachable_instructions"],
            ),
            (5, 5, 3, 2, 6, 2, 758, 872, 114, 297),
        )
        self.assertEqual(
            (
                s["direct_body_calls"], s["internal_direct_body_calls"],
                s["external_direct_body_calls"], s["indirect_body_calls"],
                s["direct_bl_entry_sites"], s["stored_entry_pointers"],
            ),
            (63, 1, 62, 1, 4, 2),
        )

    def test_event_and_stream_contract(self):
        b = self.report["behavior"]
        self.assertEqual(b["receive_stream_capacity_bytes"], 24576)
        self.assertEqual(
            (b["worker_event_mask"], b["receive_event_bit"], b["send_event_bit"], b["tick_event_bit"]),
            (7, 1, 2, 4),
        )
        self.assertTrue(b["event_wait_no_auto_clear"])
        self.assertEqual(b["event_wait_timeout"], 0xFFFFFFFF)
        self.assertEqual(
            (b["receive_chunk_bytes"], b["receive_dispatch_iteration_limit"], b["receive_dispatch_byte_threshold"]),
            (1024, 32, 32767),
        )
        self.assertEqual(b["product_mode_handshake_read_bytes"], 10)
        self.assertEqual(b["dynamic_initializer_pointer_slot"], "0x20000658")

    def test_dependency_provenance_and_provider_accounting(self):
        p = self.report["provider_boundary"]
        self.assertEqual(
            (
                p["easylogger_and_compact_calls"], p["cmsis_freertos_calls"],
                p["iar_dlib_calls"], p["g2_stream_calls"],
                p["g2_uart_adapter_calls"], p["tinyframe_and_sync_framework_calls"],
                p["g2_subsystem_policy_calls"], p["bounded_indirect_initializer_calls"],
            ),
            (30, 8, 1, 4, 5, 4, 10, 1),
        )
        self.assertEqual(
            p["cmsis_freertos_commit"],
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        )
        self.assertEqual(
            p["tinyframe_selected_commit"],
            "eb75483e035916ef9f3e9fce0d2ae389cb09785f",
        )
        self.assertEqual(
            p["ambiqsuite_apollo510_commit"],
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        )
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])

    def test_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
