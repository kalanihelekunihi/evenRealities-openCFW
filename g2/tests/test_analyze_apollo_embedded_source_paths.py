#!/usr/bin/env python3
"""Guard the authenticated Apollo embedded source-path census."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_apollo_embedded_source_paths.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_apollo_embedded_source_paths", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloEmbeddedSourcePathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_image_and_closed_path_census_are_pinned(self) -> None:
        self.assertEqual(self.report["image"]["size"], 3_523_396)
        self.assertEqual(
            self.report["image"]["sha256"],
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        )
        census = self.report["path_census"]
        self.assertEqual(census["total_unique_paths"], 357)
        self.assertEqual(census["root_counts"], self.analyzer.EXPECTED_ROOT_COUNTS)
        self.assertEqual(
            census["third_party_counts"],
            self.analyzer.EXPECTED_THIRD_PARTY_COUNTS,
        )
        self.assertEqual(census["third_party_unique_paths"], 123)
        self.assertEqual(census["first_party_or_project_paths"], 234)

    def test_every_path_has_a_run_address_and_pointer_evidence(self) -> None:
        paths = self.report["paths"]
        self.assertEqual(len({record["path"] for record in paths}), 357)
        self.assertTrue(all(record["path"].endswith(".c") for record in paths))
        self.assertTrue(all(record["run"] > self.analyzer.LOAD_BASE for record in paths))
        self.assertTrue(all(record["pointer_cells"] for record in paths))
        by_relative = {record["relative"]: record for record in paths}
        self.assertIn(r"third_party\TinyFrame\TinyFrame.c", by_relative)
        self.assertIn(r"third_party\ringBuffer\ringbuffer.c", by_relative)
        self.assertIn(r"kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c", by_relative)

    def test_path_mutation_fails_closed(self) -> None:
        blob = bytearray(self.analyzer.DEFAULT_IMAGE.read_bytes())
        first = blob.index(self.analyzer.WORKSPACE_PREFIX)
        blob[first + len(self.analyzer.WORKSPACE_PREFIX)] ^= 1
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.extract_paths(bytes(blob))

    def test_synthetic_function_correlation_uses_string_and_pointer_symbols(self) -> None:
        records = [
            {
                "run": 0x006C_AD04,
                "root": "third_party",
                "third_party_dependency": "lvgl_v9.3",
                "pointer_cells": [0x005C_2140],
            },
            {
                "run": 0x006F_E474,
                "root": "third_party",
                "third_party_dependency": "TinyFrame",
                "pointer_cells": [0x0049_1EE4],
            },
        ]
        lines = [
            "OPENCFW_FUNCTION_BEGIN entry=005c16d8 body_start=005c16d8 body_end=005c173d",
            "FUN(3,PTR_s_path_005c2140);",
            "OPENCFW_FUNCTION_END entry=005c16d8",
            "OPENCFW_FUNCTION_BEGIN entry=005c173e body_start=005c173e body_end=005c1785",
            "FUN(0x006cad04);",
            "OPENCFW_FUNCTION_END entry=005c173e",
        ]
        original_count = self.analyzer.EXPECTED_FUNCTION_COUNT
        self.analyzer.EXPECTED_FUNCTION_COUNT = 2
        try:
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as directory:
                log = Path(directory) / "apollo-00.log"
                log.write_text("\n".join(lines), encoding="utf-8")
                result = self.analyzer.correlate_functions(records, [log])
        finally:
            self.analyzer.EXPECTED_FUNCTION_COUNT = original_count
        self.assertEqual(result["functions_with_path_references"], 2)
        self.assertEqual(result["functions_without_path_references"], 0)
        self.assertEqual(result["first_party_or_project_anchored_functions"], 0)
        self.assertEqual(result["third_party_anchored_functions"], 2)
        self.assertEqual(result["cross_root_anchored_functions"], 0)
        self.assertEqual(result["paths_with_function_references"], 1)
        self.assertEqual(result["paths_without_function_references"], 1)
        self.assertEqual(result["third_party_function_counts"]["lvgl_v9.3"], 2)
        self.assertEqual(records[0]["function_references"][0]["evidence"], ["pointer_cell"])
        self.assertEqual(records[0]["function_references"][1]["evidence"], ["string"])
        self.assertEqual(records[1]["function_references"], [])

    def test_cli_text_and_json_modes(self) -> None:
        text = subprocess.run(
            [sys.executable, str(ANALYZER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("retained paths: 357", text)
        self.assertIn("lvgl_v9.3=78", text)
        parsed = json.loads(
            subprocess.run(
                [sys.executable, str(ANALYZER), "--json"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        self.assertEqual(parsed["path_census"]["third_party_unique_paths"], 123)


if __name__ == "__main__":
    unittest.main()
