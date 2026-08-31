#!/usr/bin/env python3
"""Regression tests for the Apollo liblc3 placement/routing blocker audit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
TOOL = G2 / "tools/analyze_g2_liblc3_encoder_placement.py"


def load_tool():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_liblc3_encoder_placement_test", TOOL
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Liblc3EncoderPlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_tool()
        cls.report = cls.module.run_audit()

    def test_authenticated_stock_calls_are_exact(self) -> None:
        stock = self.report["official_stock"]
        self.assertEqual(stock["direct_call_count"], 5)
        self.assertEqual(
            [(row["address"], row["stock_symbol"], row["stock_target"])
             for row in stock["direct_calls"]],
            [
                (0x0057A938, "lc3_setup_encoder", 0x00591374),
                (0x0057A9C2, "lc3_frame_samples", 0x00590E64),
                (0x0057A9CC, "lc3_frame_bytes", 0x00590F78),
                (0x0057AA9E, "lc3_setup_encoder", 0x00591374),
                (0x0057AB14, "lc3_encode", 0x0059138A),
            ],
        )
        self.assertEqual(stock["stock_ltpf_call"]["address"], 0x0059145C)
        self.assertEqual(stock["stock_ltpf_call"]["target"], 0x00438FB8)

    def test_current_capacity_proves_no_move_impossible(self) -> None:
        placement = self.report["placement"]
        self.assertEqual(placement["append_headroom"], 71100)
        self.assertEqual(placement["required_aligned_span"], 128752)
        self.assertEqual(placement["append_only_shortfall"], 57652)
        self.assertEqual(placement["optimistic_known_capacity"], 93968)
        self.assertEqual(placement["optimistic_known_capacity_shortfall"], 34784)
        self.assertTrue(placement["branch_range_sufficient"])
        self.assertFalse(
            self.report["routing"][
                "production_feasible_without_moving_other_components"]
        )

    def test_relocation_and_abi_gates_remain_fail_closed(self) -> None:
        relocations = self.report["relocations"]
        self.assertEqual((relocations["total"], relocations["internal"],
                          relocations["external"]), (567, 400, 167))
        self.assertEqual(len(relocations["retained_imports"]), 12)
        self.assertEqual(relocations["runtime_import_bindings"], {})
        self.assertFalse(relocations["writable_data_policy_proven"])
        self.assertIsNone(
            self.report["routing"]["bounded_provider_direct_patch_mapping"]
        )
        self.assertEqual(len(self.report["software_blockers"]), 6)
        self.assertFalse(self.report["hardware_operations"])

    def test_generated_flash_plan_is_never_placement_authority(self) -> None:
        plan = self.report["generated_flash_plan"]
        self.assertFalse(plan["placement_authority"])
        if plan["present"]:
            self.assertLess(
                plan["headroom_to_update_record"],
                self.report["placement"]["required_aligned_span"],
            )

    def test_capacity_tamper_is_rejected(self) -> None:
        proposal = json.loads(self.module.PROPOSAL.read_text(encoding="utf-8"))
        proposal["capacity_proof"]["append_only_shortfall"] -= 1
        with tempfile.TemporaryDirectory(prefix="liblc3-placement-tamper-") as d:
            path = Path(d) / "proposal.json"
            path.write_text(json.dumps(proposal), encoding="utf-8")
            original = self.module.PROPOSAL
            self.module.PROPOSAL = path
            try:
                with self.assertRaisesRegex(
                        self.module.PlacementError,
                        "capacity upper-bound proof drift"):
                    self.module.run_audit()
            finally:
                self.module.PROPOSAL = original

    def test_cli_output_is_deterministic_json(self) -> None:
        first = subprocess.run(
            [sys.executable, str(TOOL)], cwd=G2,
            check=True, capture_output=True, text=True,
        ).stdout
        second = subprocess.run(
            [sys.executable, str(TOOL)], cwd=G2,
            check=True, capture_output=True, text=True,
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(
            json.loads(first)["status"],
            "liblc3-encoder-placement-routing-blocked",
        )


if __name__ == "__main__":
    unittest.main()
