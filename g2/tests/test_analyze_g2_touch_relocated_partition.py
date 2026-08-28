# SPDX-License-Identifier: MIT
"""Tests for relocation-corrected G2 touch CFG/data partitioning."""

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/analyze_g2_touch_relocated_partition.py"
S = importlib.util.spec_from_file_location("g2_touch_relocated_partition", P)
M = importlib.util.module_from_spec(S)
sys.modules[S.name] = M
S.loader.exec_module(M)


class TouchRelocatedPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = M.analyze()
        cls.functions = {row["entry"]: row for row in cls.result["function_rows"]}
        cls.vectors = {row["payload_entry"]: row
                       for row in cls.result["vector_rows"]}

    def test_link_base_has_independent_shipped_anchors(self):
        relocation = self.result["relocation"]
        self.assertEqual(relocation["linked_flash_base"], 0x3300)
        self.assertEqual(relocation["payload_linked_end"], 0xB980)
        self.assertEqual(
            {(row["linked_address"], row["payload_offset"])
             for row in relocation["anchors"]},
            {(0xAA5C, 0x775C), (0xB0C4, 0x7DC4)},
        )
        self.assertIn("not payload offsets", relocation["correction"])

    def test_three_vectors_are_relocated_and_bounded(self):
        self.assertEqual(set(self.vectors), {0x135C, 0x135E, 0x1374})
        expected = {
            0x135C: (0x465D, "shared_default_handler", 2,
                     "575fc8fa9e92ffe7d57a6aef6f1168f39da04f07d6bcd5b5e17883bff7b33165"),
            0x135E: (0x465F, "hardfault_halt_handler", 8,
                     "76df2f1edb1a47699b952e59c124b1c2bc8f442272c16a4192c8adb94de54f3a"),
            0x1374: (0x4675, "reset_startup_handler", 104,
                     "db0963144ca483b44bfb640b4a31207f3d90b3cb1cfbc342d19f6217f47cfb2a"),
        }
        for entry, (raw, name, size, digest) in expected.items():
            row = self.vectors[entry]
            self.assertEqual((row["raw_vector"], row["name"], row["bytes"],
                              row["sha256"]), (raw, name, size, digest))
            self.assertEqual((raw & ~1) - M.LINK_BASE, entry)
            self.assertIn("source still required", row["source_disposition"])

    def test_linked_tables_are_shipped_not_external_resident(self):
        rows = self.result["linked_reference_rows"]
        self.assertTrue(all(row["availability"] ==
                            "shipped_payload_after_relocation" for row in rows))
        self.assertEqual(
            {(row["linked_address"], row["payload_offset"])
             for row in rows},
            {(0xAA5C, 0x775C), (0xB0C4, 0x7DC4),
             (0xB0E8, 0x7DE8), (0xB374, 0x8074),
             (0xB4FC, 0x81FC), (0xB51C, 0x821C)},
        )

    def test_function_entry_expansion_and_origins_are_pinned(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["function_entries"], 286)
        self.assertEqual(metrics["entry_origins"], {
            "authenticated_evidence": 16,
            "direct_bl_closure": 252,
            "linked_flash_pointer": 15,
            "relocated_vector": 3,
        })
        self.assertEqual(len(self.functions), 286)
        self.assertTrue({0x02E4, 0x0324, 0x0648, 0x1368,
                         0x1480, 0x1510, 0x3480, 0x72F4} <= self.functions.keys())

    def test_source_and_provider_claims_stay_conservative(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["function_dispositions"], {
            "external_eula_clean_room_required": 20,
            "project_fail_closed_contract": 8,
            "project_source_candidate": 10,
            "semantic_source_unclassified": 223,
            "typed_startup_source_required": 3,
            "unsupported_intentional_noop": 1,
            "upstream_apache_provider": 14,
            "upstream_runtime_provider": 7,
        })
        self.assertEqual(metrics["concrete_source_function_count"], 10)
        self.assertEqual(metrics["typed_external_functions_not_counted_as_source"],
                         52)
        for entry in (0x135C, 0x135E, 0x1374):
            self.assertEqual(self.functions[entry]["disposition"],
                             "typed_startup_source_required")

    def test_code_pool_partition_is_exhaustive_and_deduplicated(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["code_span_bytes"], 30364)
        self.assertEqual(metrics["literal_targets"], 472)
        self.assertEqual(metrics["linked_pointer_seed_entries"], 15)
        self.assertEqual(metrics["code_partition"], {
            "cfg_instruction_candidate": 26892,
            "cfg_literal_overlap_ambiguous": 72,
            "referenced_literal_data": 1816,
            "still_unclassified": 1584,
        })
        self.assertEqual(sum(metrics["code_partition"].values()), 30364)
        self.assertEqual(sum(row["bytes"] for row in self.result["partition_rows"]),
                         30364)
        self.assertIn("not a source", self.result["partition_rows"][0]["note"])

    def test_prior_24048_byte_remainder_is_exactly_repartitioned(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["prior_remainder_bytes"], 24048)
        self.assertEqual(metrics["prior_remainder_partition"], {
            "new_cfg_instruction_candidate": 20580,
            "new_cfg_literal_overlap_ambiguous": 68,
            "new_referenced_literal_data": 1816,
            "still_unclassified": 1584,
        })
        self.assertEqual(sum(metrics["prior_remainder_partition"].values()),
                         24048)

    def test_digests_and_software_only_mode_are_pinned(self):
        metrics = self.result["metrics"]
        self.assertEqual(metrics["function_digest"],
                         "601c283cbcd191ef603f92b59f555c5ba1b78c4de72c0f75ebaa83182e50866c")
        self.assertEqual(metrics["partition_digest"],
                         "0b9c47aa5bcb65d74cb4985342f39d54a192450e26b8dbdb07f200c215a25b75")
        self.assertIn("no hardware", self.result["analysis_mode"])
        self.assertTrue(any("1,584" in item for item in self.result["limitations"]))

    def test_manifests_are_deterministic(self):
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
                    "g2-touch-relocated-functions.tsv",
                    "g2-touch-relocated-code-partition.tsv",
                    "g2-touch-relocated-vectors.tsv",
                    "g2-touch-relocated-linked-references.tsv",
                    "g2-touch-relocated-partition-summary.json",
                })
        finally:
            M.MANIFEST_DIR = old


if __name__ == "__main__":
    unittest.main()
