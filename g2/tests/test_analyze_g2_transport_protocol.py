#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_transport_protocol.py"


class TransportProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("g2_transport_protocol", ANALYZER)
        assert spec is not None and spec.loader is not None
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)
        cls.report = cls.module.analyze()

    def test_closed_object(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["linked_functions"], 13)
        self.assertEqual(surface["path_anchored_functions"], 7)
        self.assertEqual(surface["additional_recovered_functions"], 6)
        self.assertEqual(surface["recursive_decode_recoveries"], 1)
        self.assertEqual(surface["body_bytes"], 4_134)
        self.assertEqual(surface["literal_pool_bytes"], 302)
        self.assertEqual(surface["physical_bytes"], 4_436)
        self.assertEqual(surface["stored_entry_pointers"], 2)
        self.assertEqual(surface["strict_interior_raw_bl_decodes"], 0)
        self.assertEqual(surface["unrecovered_direct_object_targets"], 0)

    def test_protocol_behavior_and_crc_boundary(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["magic"], "0xAA")
        self.assertEqual(behavior["header_bytes"], 8)
        self.assertEqual(behavior["maximum_payload_bytes"], 4_096)
        self.assertEqual(behavior["receive_contexts"], 4)
        self.assertEqual(behavior["receive_timeout_ms"], 1_500)
        self.assertIn("CCITT-FALSE", behavior["crc"])
        self.assertEqual(
            behavior["crc_call_sites"],
            ["0x004b91d8", "0x004b9486", "0x004b97b0"],
        )

    def test_provider_seams_and_tinyframe_exclusion(self) -> None:
        boundary = self.report["provider_boundary"]
        self.assertEqual(boundary["direct_external_targets"], 18)
        self.assertEqual(boundary["provider_rows"], 8)
        self.assertEqual(boundary["cmsis_freertos"]["version"], "v10.5.1")
        self.assertEqual(
            boundary["cmsis_freertos"]["commit"],
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        )
        self.assertEqual(boundary["tinyframe"]["direct_calls"], 0)
        self.assertEqual(boundary["tinyframe"]["stored_pointers"], 0)
        self.assertEqual(self.report["identity"]["embedded_third_party_definitions"], [])
        production = self.report["production"]
        self.assertTrue(production["production_routed"])
        self.assertEqual(production["ownership_bytes"], 4_134)
        self.assertEqual(production["source_functions"], 13)
        self.assertEqual(production["compiled_text_bytes"], 2_538)
        self.assertEqual(production["alignment_bytes"], 14)
        self.assertEqual(production["strict_relocations"], 55)
        self.assertFalse(production["software_functional_gap"])
        self.assertEqual(production["hardware_validation"], "deferred by project direction")


if __name__ == "__main__":
    unittest.main()
