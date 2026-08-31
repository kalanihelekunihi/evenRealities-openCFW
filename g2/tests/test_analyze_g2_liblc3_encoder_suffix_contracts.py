#!/usr/bin/env python3
"""Focused tests for the Apollo-main LC3 suffix strict-contract audit."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_liblc3_encoder_suffix_contracts.py"
MANIFEST = (
    G2
    / "components/apollo_main/liblc3_encoder/suffix_strict_contracts.json"
)

SPEC = importlib.util.spec_from_file_location(
    "analyze_g2_liblc3_encoder_suffix_contracts_test", ANALYZER
)
assert SPEC is not None and SPEC.loader is not None
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def apple_clang() -> str:
    try:
        path = subprocess.check_output(
            ["xcrun", "--find", "clang"], text=True
        ).strip()
        version = subprocess.check_output(
            [path, "--version"], text=True
        ).splitlines()[0]
    except (OSError, subprocess.CalledProcessError) as error:
        raise unittest.SkipTest("canonical Apple clang is unavailable") from error
    if not version.startswith("Apple clang version 21.0.0"):
        raise unittest.SkipTest(f"unreviewed Apple clang: {version}")
    return path


class SuffixStrictContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = apple_clang()
        cls.report = audit.analyze(MANIFEST, clang=cls.clang)

    def test_all_seven_contracts_authenticate_but_routing_stays_blocked(self) -> None:
        report = self.report
        self.assertEqual(
            report["status"],
            "all-seven-suffix-strict-contracts-authenticated",
        )
        self.assertEqual(report["summary"]["function_count"], 7)
        self.assertEqual(report["summary"]["function_bytes"], 8910)
        self.assertEqual(report["summary"]["relocation_count"], 44)
        self.assertEqual(report["summary"]["strict_authenticated_count"], 7)
        self.assertEqual(report["summary"]["strict_authenticated_bytes"], 8910)
        self.assertIsNone(report["summary"]["blocked_function"])
        self.assertEqual(report["summary"]["blocked_bytes"], 0)
        self.assertFalse(
            report["capacity"]["production_rebalancing_feasible_now"]
        )

    def test_every_elf_table_replays_without_hidden_executable_materialization(self) -> None:
        for function in self.report["functions"]:
            self.assertTrue(function["strict_elf_replay_current"])
            self.assertTrue(function["strict_elf_replay_proposed"])
            self.assertTrue(function["promotion_applied"])
        hidden = self.report["unrelocated_executable_materializations"]
        self.assertEqual(hidden, [])
        engine = self.report["functions"][-1]
        self.assertEqual(engine["relocation_count"], 12)
        self.assertTrue(engine["strict_contract_authenticated"])

    def test_ingress_is_exact_and_false_decodes_are_classified(self) -> None:
        ingress = self.report["ingress"]
        self.assertEqual(ingress["exact_entry_branch_count"], 6)
        self.assertEqual(ingress["exact_entry_call_count"], 3)
        self.assertEqual(ingress["exact_entry_jump_count"], 3)
        self.assertEqual(ingress["false_interior_decode_count"], 4)
        self.assertEqual(ingress["raw_entry_pointer_count"], 0)

    def test_cli_output_is_byte_deterministic(self) -> None:
        command = [
            sys.executable,
            str(ANALYZER),
            "--manifest",
            str(MANIFEST),
            "--clang",
            self.clang,
        ]
        first = subprocess.run(command, check=True, capture_output=True)
        second = subprocess.run(command, check=True, capture_output=True)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(
            json.loads(first.stdout)["summary"], self.report["summary"]
        )

    def test_manifest_cannot_demote_the_authenticated_engine_contract(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        manifest["functions"][-1]["strict_contract_feasible"] = False
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "manifest.json"
            candidate.write_text(
                json.dumps(manifest, sort_keys=True), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                audit.ContractError, "strict feasibility classification drift"
            ):
                audit.analyze(candidate, clang=self.clang)


if __name__ == "__main__":
    unittest.main()
