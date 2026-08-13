#!/usr/bin/env python3
"""Contracts for the reviewed Apollo source-path recovery."""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
CORPUS = Path(os.environ.get(
    "OPENCFW_APOLLO_GHIDRA_CORPUS",
    "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
))


def load_module():
    sys.path.insert(0, str(TOOLS))
    spec = importlib.util.spec_from_file_location(
        "recover_apollo_embedded_source_paths",
        TOOLS / "recover_apollo_embedded_source_paths.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApolloEmbeddedSourcePathRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not CORPUS.is_dir():
            raise unittest.SkipTest("authenticated Apollo Ghidra corpus unavailable")
        cls.module = load_module()
        cls.report = cls.module.recover(cls.module.baseline.DEFAULT_IMAGE, CORPUS)

    def test_closed_state_and_reference_census(self) -> None:
        self.assertEqual(len(self.report["paths"]), 43)
        self.assertEqual(
            self.report["recovery"]["state_counts"],
            {
                "baseline_function_anchored_paths": 314,
                "confirmed_path_only_data": 0,
                "missed_code_candidate": 41,
                "recovered_function": 2,
            },
        )
        self.assertEqual(self.report["recovery"]["literal_pointer_cells"], 46)
        self.assertEqual(self.report["recovery"]["raw_thumb_ldr_decode_sites"], 273)
        self.assertTrue(all(path["literal_reference_sites"] for path in self.report["paths"]))
        self.assertIn("only the eight", self.report["limitations"][0])

    def test_only_independently_evidenced_functions_are_recovered(self) -> None:
        recovered = {
            path["relative"]: path["recovered_functions"]
            for path in self.report["paths"]
            if path["state"] == "recovered_function"
        }
        self.assertEqual(
            {item["entry"] for items in recovered.values() for item in items},
            {0x43C400, 0x43C496, 0x43C5F6, 0x43C6CE, 0x52A474, 0x52A51A, 0x52A542, 0x52A574},
        )
        for items in recovered.values():
            for item in items:
                self.assertTrue(item["stored_thumb_pointer_cells"] or item["direct_call_sites"])
        self.assertNotIn(0x43C450, {item["entry"] for items in recovered.values() for item in items})

    def test_mutated_call_and_pointer_witnesses_fail_closed(self) -> None:
        blob = self.module.baseline.DEFAULT_IMAGE.read_bytes()
        self.assertEqual(self.module._thumb_bl_target(blob, 0x4B7F6A), 0x52A474)
        self.assertEqual(self.module._thumb_bl_target(blob, 0x52A59A), 0x52A51A)
        changed = bytearray(blob)
        changed[0x52A59A - self.module.baseline.LOAD_BASE] ^= 1
        self.assertNotEqual(self.module._thumb_bl_target(bytes(changed), 0x52A59A), 0x52A51A)
        offset = 0x6A44B4 - self.module.baseline.LOAD_BASE
        self.assertEqual(int.from_bytes(blob[offset : offset + 4], "little"), 0x43C401)

    def test_literal_decoder_rejects_data_only_interpretation(self) -> None:
        blob = self.module.baseline.DEFAULT_IMAGE.read_bytes()
        self.assertEqual(
            self.module.literal_references(blob, 0x52A630),
            [0x52A5DA],
        )
        aging_sites = self.module.literal_references(blob, 0x43C760)
        self.assertEqual(len(aging_sites), 8)
        self.assertIn(0x43C41C, aging_sites)


if __name__ == "__main__":
    unittest.main()
