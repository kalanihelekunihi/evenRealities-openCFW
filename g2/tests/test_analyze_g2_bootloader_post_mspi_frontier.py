#!/usr/bin/env python3

from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_bootloader_post_mspi_frontier.py"
CENSUS = ROOT / "tools/manifests/g2-bootloader-post-mspi-frontier.tsv"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_interrupt_power_426536.S"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("post_mspi_frontier", ANALYZER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load post-MSPI analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PostMspiFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.result = cls.module.audit()

    def test_exhaustive_partition_has_no_unclassified_bytes(self) -> None:
        classification = self.result["classification"]
        self.assertTrue(classification["exhaustive"])
        self.assertEqual(classification["row_count"], 253)
        self.assertEqual(classification["unclassified_bytes"], 0)
        self.assertEqual(
            sum(item["bytes"] for item in classification["by_disposition"].values()),
            57_153,
        )

    def test_exact_candidate_queue_is_bounded_not_silently_source_owned(self) -> None:
        classes = self.result["classification"]["by_disposition"]
        self.assertEqual(
            classes["cross_image_exact_source_candidate"],
            {"spans": 58, "bytes": 4_550},
        )
        self.assertEqual(classes["typed_unresolved_executable"]["bytes"], 19_534)
        self.assertEqual(classes["typed_nonentry_mixed_or_data"]["bytes"], 31_127)

    def test_two_ambiq_functions_are_exact_production_source(self) -> None:
        admission = self.result["admission"]
        self.assertTrue(admission["production_routed"])
        self.assertEqual(admission["license"], "BSD-3-Clause")
        self.assertEqual(admission["source_owned_bytes"], 1_726)
        functions = list(admission["functions"].values())
        self.assertEqual([item["bytes"] for item in functions], [712, 1_014])
        self.assertEqual([item["address_coupled_difference_bytes"] for item in functions], [20, 29])
        self.assertEqual([len(item["provider_edges"]) for item in functions], [8, 12])

    def test_production_source_is_reviewable_mnemonic_assembly(self) -> None:
        source = SOURCE.read_text()
        self.assertNotIn(".byte", source)
        self.assertNotIn(".short", source)
        self.assertNotIn(".word", source)
        self.assertIn(".syntax unified", source)
        self.assertIn("ABI r0=pHandle", source)
        self.assertEqual(
            self.result["admission"]["upstream_commit"],
            "5efc0228528a8adce5eae0d226fac85d2551eb3b",
        )

    def test_literal_pools_remain_typed_official_data(self) -> None:
        rows = list(csv.DictReader(CENSUS.read_text().splitlines(), delimiter="\t"))
        pools = [row for row in rows if row["kind"] == "literal_pool"]
        self.assertEqual([(row["start"], row["end"], int(row["size"])) for row in pools], [
            ("0x004267fe", "0x00426808", 10),
            ("0x00426bfe", "0x00426c10", 18),
        ])
        self.assertTrue(all(row["disposition"] == "retained_typed_data" for row in pools))

    def test_both_reviewed_compilers_emit_the_same_bodies(self) -> None:
        self.assertTrue(self.result["profiles"]["apple-clang"].startswith("Apple clang version 21.0.0"))
        self.assertEqual(self.result["profiles"]["linux-clang"], "Homebrew clang version 22.1.8")

    def test_live_boot_accounting_conserves_the_stock_owned_domain(self) -> None:
        component = self.result["boot_component"]
        self.assertEqual(component["source_owned_bytes"], 27_819)
        self.assertEqual(component["opaque_base_bytes"], 119_477)
        self.assertEqual(component["source_owned_bytes"] + component["opaque_base_bytes"], 147_296)

    def test_cli_is_machine_readable_and_software_only(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["hardware_validation"], "deferred by project direction")
        self.assertEqual(result["hardware_operations"], [])
        self.assertNotIn("flashing", result)


if __name__ == "__main__":
    unittest.main()
