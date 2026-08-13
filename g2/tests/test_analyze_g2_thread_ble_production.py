import unittest

from tools import analyze_g2_thread_ble_production as analyzer


class G2ThreadBleProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = analyzer.analyze()

    def test_object_is_physically_closed(self):
        surface = self.report["surface"]
        self.assertEqual(
            (surface["linked_functions"], surface["body_bytes"], surface["physical_bytes"]),
            (14, 2140, 2368),
        )
        self.assertEqual(
            (surface["ghidra_discovered_functions"], surface["restored_non_anchor_functions"]),
            (11, 8),
        )

    def test_whole_image_ingress_is_closed(self):
        surface = self.report["surface"]
        self.assertEqual(
            (surface["direct_bl_entry_sites"], surface["stored_function_pointers"]),
            (11, 1),
        )
        self.assertEqual(
            (surface["indirect_body_calls"], surface["strict_interior_ingress"], surface["wide_branch_entry_targets"]),
            (0, 0, 0),
        )
        self.assertEqual(
            (surface["excluded_unaligned_entry_lookalikes"], surface["excluded_unaligned_interior_lookalikes"]),
            (1, 1),
        )

    def test_exact_upstream_provider_boundary(self):
        providers = self.report["provider_boundary"]
        self.assertEqual(
            (
                providers["easylogger_calls"],
                providers["cmsis_freertos_calls"],
                providers["freertos_assert_calls"],
                providers["runtime_calls"],
                providers["first_party_calls"],
            ),
            (106, 15, 3, 5, 6),
        )
        self.assertIsNone(providers["historical_product_thread_commit"])

    def test_thread_resources_and_protocol_are_pinned(self):
        thread = self.report["thread"]
        self.assertEqual(thread["entry"], 0x005382E4)
        self.assertEqual(thread["queue_depth"], 3)
        self.assertEqual(thread["memory_pool_blocks"], 3)
        self.assertEqual(thread["memory_pool_block_bytes"], 0x104)
        self.assertEqual(self.report["protocol"]["header"], [0x5A, 0xA5, 0x7F])

    def test_unimplemented_object_is_not_production_routed(self):
        self.assertFalse(self.report["production"]["production_routed"])


if __name__ == "__main__":
    unittest.main()
