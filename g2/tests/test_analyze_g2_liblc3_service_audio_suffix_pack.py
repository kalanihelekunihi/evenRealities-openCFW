#!/usr/bin/env python3
"""Focused tests for the Apollo LC3 minimal strict-suffix packing audit."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
TOOL = G2 / "tools/analyze_g2_liblc3_service_audio_suffix_pack.py"
MANIFEST = (
    G2 / "components/apollo_main/liblc3_encoder/"
    "service_audio_suffix_pack_proposal.json"
)


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_liblc3_service_audio_suffix_pack_test", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Liblc3ServiceAudioSuffixPackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_tool()
        cls.report = cls.module.analyze()

    def test_minimal_strict_suffix_closes_capacity(self) -> None:
        capacity = self.report["capacity"]
        self.assertEqual((capacity["suffix_count"], capacity["suffix_span"]),
                         (84, 9252))
        self.assertEqual(capacity["suffix_payload_bytes"], 9174)
        self.assertEqual(capacity["new_core_end_exclusive"], 0x007EA620)
        self.assertEqual(capacity["lc3_end_exclusive"], 0x007FDFA0)
        self.assertEqual(capacity["margin_before_update_record"], 96)

    def test_seven_host_tails_are_aligned_and_nonoverlapping(self) -> None:
        slots = self.report["host_slots"]
        self.assertEqual(len(slots), 7)
        intervals = []
        items = []
        for slot in slots:
            self.assertLessEqual(slot["cursor"], slot["end_exclusive"])
            for item in slot["items"]:
                self.assertEqual(item["start"] % item["alignment"], 0)
                self.assertGreaterEqual(item["start"], slot["start"])
                self.assertLessEqual(item["start"] + item["size"],
                                     slot["end_exclusive"])
                intervals.append((item["start"], item["start"] + item["size"]))
                items.append(item["function"])
        self.assertEqual(len(items), len(set(items)))
        self.assertEqual(len(items), 84)
        intervals.sort()
        self.assertTrue(all(left[1] <= right[0]
                            for left, right in zip(intervals, intervals[1:])))

    def test_all_suffix_relocations_and_ingress_are_closed(self) -> None:
        replay = self.report["suffix_relocation_replay"]
        self.assertTrue(replay["all_84_leaves_strict"])
        self.assertTrue(replay["identity_replay_verified"])
        self.assertEqual(replay["relocation_count"], 288)
        ingress = self.report["ingress"]
        self.assertEqual(
            (ingress["exact_entry_branch_count"],
             ingress["stock_entry_redirect_count"],
             ingress["suffix_internal_branch_count"],
             ingress["raw_pointer_count"]),
            (127, 84, 43, 0),
        )

    def test_lc3_final_routing_remains_fail_closed(self) -> None:
        placement = self.report["lc3_placement"]
        self.assertEqual(placement["runtime_import_count"], 11)
        self.assertEqual(placement["input_relocations"], 485)
        self.assertEqual((placement["table_initializers"],
                          placement["table_code_references"]), (78, 6))
        self.assertFalse(placement["final_lc3_relocation_replay"])
        self.assertFalse(placement["placement_authorized"])
        self.assertFalse(self.report["routing"]["service_audio_routed"])
        self.assertFalse(self.report["evidence_boundary"][
            "firmware_image_emitted"])
        adapter = self.report["adapter_state"]
        self.assertEqual((adapter["slot_count"], adapter["slot_bytes"],
                          adapter["total_bytes"]), (4, 2628, 10512))
        self.assertTrue(adapter["alignment_and_nonoverlap_verified"])

    def test_hostile_insufficient_or_misaligned_pack_is_rejected(self) -> None:
        leaves = [{"function": "large", "size": 8, "alignment": 8}]
        bins = [{"host_function": "tiny", "start": 3,
                 "end_exclusive": 10, "cursor": 3, "items": []}]
        with self.assertRaisesRegex(self.module.SuffixPackError,
                                    "does not fit authenticated host tails"):
            self.module.pack_suffix(leaves, bins)

    def test_hostile_production_authority_is_rejected(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["routing"]["production_placement"] = True
        with tempfile.TemporaryDirectory(prefix="liblc3-suffix-tamper-") as temp:
            path = Path(temp) / "proposal.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                    self.module.SuffixPackError,
                    "gained production authority"):
                self.module.analyze(path)


if __name__ == "__main__":
    unittest.main()
