# SPDX-License-Identifier: MIT
"""Tests for the authenticated G2 touch shipped-prefix function map."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_prefix_function_map.py"
S = importlib.util.spec_from_file_location("g2_touch_prefix_function_map", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchPrefixFunctionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.rows = {row["entry"]: row for row in cls.result["rows"]}

    def test_authenticated_identity_and_software_only_mode(self):
        self.assertEqual(
            self.result["identity"]["sha256"],
            "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d",
        )
        self.assertEqual(self.result["identity"]["payload_end"], 0x8680)
        self.assertIn("no hardware", self.result["analysis_mode"])

    def test_pinned_map_metrics(self):
        self.assertEqual(self.result["metrics"], {
            "function_count": 63,
            "evidence_named_functions": 16,
            "vector_seed_functions": 3,
            "unresolved_shipped_functions": 44,
            "instruction_instances": 3171,
            "function_instruction_bytes": 6620,
            "unique_instruction_bytes": 6316,
            "shared_instruction_bytes": 162,
            "maximum_owners_per_byte": 3,
            "code_span_bytes": 30364,
            "code_bytes_not_in_reachable_map": 24048,
            "indirect_call_sites": 9,
            "indirect_jump_exits": 0,
            "row_digest": "335e09b1d61057a49e69d4f58f9e9117f4e8db4f475068f76ba3f544919a5e7a",
        })

    def test_exact_evidence_function_spans(self):
        expected = {
            0x02F4: ("sensor_read_mux", 38, [(0x02F4, 0x031A)]),
            0x0378: ("i2c_slave_init", 98, [(0x0378, 0x03DA)]),
            0x0824: ("report_builder", 316, [(0x0824, 0x0960)]),
            0x0BE0: ("logger_stub", 8, [(0x0BE0, 0x0BE8)]),
            0x36C4: ("msc_sensing_loop", 168, [(0x36C4, 0x376C)]),
            0x4B14: ("NVIC_SystemReset", 18, [(0x4B14, 0x4B26)]),
            0x67D8: ("i2c_tx_descriptor_arm", 24, [(0x67D8, 0x67F0)]),
            0x67F0: ("i2c_rx_descriptor_arm", 22, [(0x67F0, 0x6806)]),
            0x6806: ("i2c_rx_position_get", 4, [(0x6806, 0x680A)]),
        }
        for entry, (name, size, spans) in expected.items():
            row = self.rows[entry]
            self.assertEqual(row["name"], name)
            self.assertEqual(row["classification"], "evidence_named")
            self.assertEqual(row["instruction_bytes"], size)
            self.assertEqual(
                [(span["start"], span["end"]) for span in row["spans"]],
                spans,
            )

    def test_case_entries_are_not_false_function_rows(self):
        cases = {item["entry"] for item in self.result["case_anchors"]}
        self.assertEqual(cases, set(M.COMMAND_CASE_ENTRIES))
        self.assertTrue(cases.isdisjoint(self.rows))
        self.assertTrue(all(item["parent_function"] == 0x0400
                            for item in self.result["case_anchors"]))

    def test_fixed_point_bl_closure(self):
        entries = set(self.rows)
        for row in self.result["rows"]:
            self.assertTrue(set(row["direct_callees"]) <= entries)
        self.assertEqual(self.rows[0x65F4]["classification"],
                         "unresolved_shipped_prefix")
        self.assertTrue(any(source.startswith("bl@")
                            for source in self.rows[0x65F4]["discovery_sources"]))
        self.assertFalse(self.result["method"]["raw_halfword_bl_sweep_used_as_seed"])

    def test_shared_suffix_accounting_is_deduplicated(self):
        metrics = self.result["metrics"]
        self.assertGreater(metrics["function_instruction_bytes"],
                           metrics["unique_instruction_bytes"])
        self.assertEqual(metrics["shared_instruction_bytes"], 162)
        for entry in (0x465C, 0x465E, 0x4674):
            self.assertEqual(self.rows[entry]["instruction_bytes"], 142)

    def test_resident_and_dfu_are_external_unavailable_abi(self):
        self.assertTrue(all(entry < 0x8680 for entry in self.rows))
        self.assertTrue(all(item["availability"] == "external_unavailable_abi"
                            for item in self.result["resident_abi"]))
        exact = {item["address"] for item in self.result["resident_abi"]
                 if item["address"] is not None}
        self.assertTrue({0xB0C4, 0xB4FC, 0xB51C, 0xB374, 0xB0E8} <= exact)
        dfu = [item for item in self.result["resident_abi"]
               if "DFU implementation" in item["role"]]
        self.assertEqual(len(dfu), 1)
        self.assertIsNone(dfu[0]["address"])

    def test_license_disposition_does_not_relicense_vendor_blob(self):
        licensing = self.result["licensing"]
        self.assertEqual(licensing["analyzer_and_manifests"], "MIT")
        self.assertIn("not relicensed", licensing["official_blob"])
        self.assertIn("provider licenses", licensing["historical_function_sources"])

    def test_manifest_writes_are_deterministic(self):
        old = M.MANIFEST_DIR
        try:
            with tempfile.TemporaryDirectory() as raw:
                M.MANIFEST_DIR = Path(raw)
                first = M.write_manifests(self.result)
                first_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in first}
                second = M.write_manifests(M.analyze())
                second_hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in second}
                self.assertEqual(first_hashes, second_hashes)
                self.assertEqual(set(first_hashes), {
                    "g2-touch-prefix-function-map.tsv",
                    "g2-touch-prefix-evidence-anchors.tsv",
                    "g2-touch-prefix-external-abi.tsv",
                    "g2-touch-prefix-function-map-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old

    def test_tamper_fails_closed(self):
        tampered = bytearray(M.BLOB.read_bytes())
        tampered[M.RECORD_OFFSET + 0x36C4] ^= 1
        with self.assertRaisesRegex(M.AuditError, "SHA-256"):
            M.analyze(bytes(tampered))


if __name__ == "__main__":
    unittest.main()
