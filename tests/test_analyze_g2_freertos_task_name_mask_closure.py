#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = (
    ROOT / "tools" / "analyze_g2_freertos_task_name_mask_closure.py"
)


def load_analyzer():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_freertos_task_name_mask_closure",
        ANALYZER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load task-name/mask-closure analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeRTOSTaskNameMaskClosureAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.result = cls.analyzer.run_audit()

    def test_all_three_entries_and_caller_topologies_are_exact(self) -> None:
        functions = self.result["functions"]
        self.assertEqual(
            (
                functions["pcTaskGetName"]["start"],
                functions["pcTaskGetName"]["end_exclusive"],
                functions["pcTaskGetName"]["size"],
            ),
            (0x00454F16, 0x00454F38, 34),
        )
        self.assertEqual(
            (
                functions["ulSetInterruptMask"]["start"],
                functions["ulSetInterruptMask"]["end_exclusive"],
                functions["ulSetInterruptMask"]["size"],
            ),
            (0x005FA0A4, 0x005FA0BA, 22),
        )
        self.assertEqual(
            (
                functions["vClearInterruptMask"]["start"],
                functions["vClearInterruptMask"]["end_exclusive"],
                functions["vClearInterruptMask"]["size"],
            ),
            (0x005FA0BA, 0x005FA0C8, 14),
        )
        expected = {
            "pcTaskGetName": (
                1,
                "6b6b656546449e21e970d725927d278f"
                "881d1c0bf448fd732bf3759f73366ee4",
            ),
            "ulSetInterruptMask": (
                181,
                "f0187e62c4c399694d4fdd8e64a2e238"
                "724f6fb0ec89a6520c3020156eb9c106",
            ),
            "vClearInterruptMask": (
                12,
                "5047082ba3888cae8330f9276620611cd"
                "f412c86fee71d1cd0ffc97447fd2746",
            ),
        }
        for name, (count, digest) in expected.items():
            with self.subTest(name=name):
                references = self.result["references"][name]
                self.assertEqual(references["direct_bl_count"], count)
                self.assertEqual(
                    references["direct_bl_callsite_sha256"],
                    digest,
                )
                self.assertEqual(references["direct_bw"], [])
                self.assertEqual(
                    references["external_interior_wide"],
                    [],
                )
                self.assertEqual(
                    references["external_entry_or_interior_narrow"],
                    [],
                )
                self.assertEqual(
                    references[
                        "naturally_aligned_entry_or_interior_words"
                    ],
                    [],
                )

    def test_vclear_unaligned_match_is_a_two_word_overlap(self) -> None:
        classification = self.result["raw_window_classification"][
            "vClearInterruptMask"
        ]
        self.assertEqual(classification["address"], 0x0062FCDF)
        self.assertEqual(classification["apparent_value"], 0x005FA0BA)
        self.assertEqual(classification["address_mod_4"], 3)
        self.assertEqual(classification["address_mod_2"], 1)
        self.assertEqual(
            classification["context_hex"],
            "e6db03802f301dbaa05f0001df401fb4",
        )
        self.assertEqual(
            classification["aligned_words"],
            [
                {"address": 0x0062FCDC, "value": 0xBA1D302F},
                {"address": 0x0062FCE0, "value": 0x01005FA0},
            ],
        )
        self.assertIn("false positive", classification["classification"])
        self.assertEqual(
            self.result["references"]["vClearInterruptMask"][
                "raw_entry_or_interior_windows"
            ],
            [
                {
                    "address": 0x0062FCDF,
                    "value": 0x005FA0BA,
                    "canonical": 0x005FA0BA,
                }
            ],
        )

    def test_smallest_atomic_promotion_and_redirects_are_explicit(
        self,
    ) -> None:
        readiness = self.result["production_readiness"]
        self.assertEqual(
            readiness["smallest_safe_atomic_promotion"],
            ["pcTaskGetName", "ulSetInterruptMask"],
        )
        self.assertFalse(
            readiness["vClearInterruptMask_required_in_same_increment"]
        )
        self.assertEqual(
            readiness["exact_redirects"][0]["stock_span"],
            [0x00454F16, 0x00454F38],
        )
        self.assertEqual(
            readiness["exact_redirects"][0]["preserve_existing_callers"],
            [0x0044AAEE],
        )
        self.assertEqual(
            readiness["exact_redirects"][1]["stock_span"],
            [0x005FA0A4, 0x005FA0BA],
        )
        self.assertEqual(
            len(
                readiness["exact_redirects"][1][
                    "preserve_existing_callers"
                ]
            ),
            181,
        )
        constraints = " ".join(
            readiness["address_preservation_constraints"]
        )
        self.assertIn("0x005FA0BA", constraints)
        self.assertIn("0x20074A20", constraints)
        self.assertEqual(
            readiness["optional_broader_redirect"]["entry_offsets"],
            {"ulSetInterruptMask": 0, "vClearInterruptMask": 22},
        )

    def test_json_cli_is_read_only_and_mutation_is_rejected(self) -> None:
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
        self.assertTrue(result["read_only"])
        self.assertEqual(
            result["production_readiness"][
                "smallest_safe_atomic_promotion"
            ],
            ["pcTaskGetName", "ulSetInterruptMask"],
        )

        package = bytearray(self.analyzer.DEFAULT_IMAGE.read_bytes())
        offset = (
            self.analyzer.PACKAGE_PREAMBLE_SIZE
            + self.analyzer.CLEAR_START
            - self.analyzer.APPLICATION_BASE
        )
        package[offset] ^= 1
        with tempfile.TemporaryDirectory() as temporary:
            mutated = Path(temporary) / "mutated.bin"
            mutated.write_bytes(package)
            with self.assertRaisesRegex(
                self.analyzer.AuditError,
                "package SHA-256 drift",
            ):
                self.analyzer.run_audit(mutated)


if __name__ == "__main__":
    unittest.main()
