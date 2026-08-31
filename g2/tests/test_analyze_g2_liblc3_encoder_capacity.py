#!/usr/bin/env python3
"""Regression tests for the Apollo liblc3 capacity-rebalancing audit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
TOOL = G2 / "tools/analyze_g2_liblc3_encoder_capacity.py"
MANIFEST = (
    G2
    / "components/apollo_main/liblc3_encoder/capacity_rebalancing_proposal.json"
)


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_liblc3_encoder_capacity_test", TOOL
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Liblc3EncoderCapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_tool()
        cls.report = cls.module.analyze()

    def test_conditional_capacity_arithmetic_is_exact(self) -> None:
        capacity = self.report["capacity"]
        self.assertEqual(capacity["eligible_slot_count"], 609)
        self.assertEqual(capacity["selected_count"], 82)
        self.assertEqual(capacity["selected_closure_bytes"], 30598)
        self.assertEqual(capacity["selected_slot_bytes"], 61648)
        self.assertEqual(capacity["predecessor_savings"], 30484)
        self.assertEqual(capacity["conditional_repack_savings"], 30676)
        self.assertEqual(capacity["conditional_overlay_size"], 331596)
        encoder = self.report["encoder"]
        self.assertEqual(encoder["conditional_margin_before_update"], 172)
        self.assertEqual(encoder["conditional_encoder_end_exclusive"], 0x007FDF54)
        self.assertFalse(encoder["placement_authorized"])

    def test_relocation_and_ingress_closure_is_quantified(self) -> None:
        relocations = self.report["relocations"]
        self.assertEqual(relocations["all_relocated_leaf_relocations"], 5677)
        self.assertEqual(relocations["movable_target_relocations"], 2406)
        self.assertEqual(relocations["movable_fixed_target_relocations"], 596)
        self.assertEqual(relocations["incoming_selected_relocations"], 102)
        self.assertEqual(relocations["selected_outgoing_relocations"], 850)
        self.assertLess(
            relocations["maximum_thumb_branch_displacement"], 1 << 24
        )
        ingress = self.report["ingress"]
        self.assertEqual((ingress["branch_count"], ingress["raw_pointer_count"]),
                         (146, 0))

    def test_suffix_is_strict_but_repack_integration_stays_fail_closed(self) -> None:
        contracts = self.report["strict_contracts"]
        self.assertFalse(contracts["production_full_repack_allowed"])
        self.assertEqual(contracts["full_repack_moved_non_strict_leaves"], 206)
        self.assertEqual(contracts["minimum_suffix_contract_blocker_bytes"], 0)
        self.assertEqual(contracts["minimum_suffix_contract_blocker_relocations"], 0)
        self.assertEqual(contracts["minimum_suffix_contract_blockers"], [])
        self.assertFalse(
            self.report["outcome"]["production_rebalancing_feasible_now"]
        )
        self.assertFalse(self.report["evidence_boundary"]["image_bytes_modified"])

    def test_pt_and_existing_liblc3_reservations_are_preserved(self) -> None:
        self.assertEqual(
            [(row["owner"], row["capacity"], row["used"])
             for row in self.report["protected_intervals"]],
            [
                ("liblc3_ltpf_text", 5626, 5596),
                ("liblc3_ltpf_rodata", 4414, 1980),
                ("pt_protocol", 35524, 22696),
                ("main_update_record", 16, 16),
            ],
        )
        pt = self.report["pt_source_uart"]
        self.assertTrue(pt["provider_interval_unchanged"])
        self.assertTrue(pt["receipt_refresh_required"])
        self.assertEqual(pt["new_call_sites"], [0x007CF14C, 0x007CF188])

    def test_shorter_selection_is_rejected(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["selected_functions"].pop()
        with tempfile.TemporaryDirectory(prefix="liblc3-capacity-tamper-") as d:
            path = Path(d) / "proposal.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                self.module.CapacityError,
                "selected prefix is not the minimal candidate prefix",
            ):
                self.module.analyze(path)

    def test_cli_output_is_deterministic_json(self) -> None:
        first = subprocess.run(
            [sys.executable, str(TOOL)],
            cwd=G2,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        second = subprocess.run(
            [sys.executable, str(TOOL)],
            cwd=G2,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(
            json.loads(first)["status"],
            "conditional-capacity-proven-production-rebalance-blocked",
        )


if __name__ == "__main__":
    unittest.main()
