# SPDX-License-Identifier: MIT
"""Fail-closed tests for production raw-encoding source ownership."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_production_raw_encoding_quality.py"
SPEC = importlib.util.spec_from_file_location("g2_raw_encoding_quality", ANALYZER)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ProductionRawEncodingQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.analyze()

    def test_exact_production_census_and_totals(self) -> None:
        self.assertTrue(self.result["classification_complete"])
        self.assertEqual(self.result["metrics"], {
            "production_routed_sources_with_directives": 2,
            "routed_source_bytes_in_affected_sources": 128,
            "directive_bytes": 16,
            "raw_instruction_transcription_bytes": 0,
            "semantic_literal_bytes": 16,
            "source_owned_bytes_currently_overstated": 0,
            "fully_raw_byte_body_bytes": 0,
            "public_raw_executable_transcript_files": 0,
            "removed_public_transcript_files": 2,
            "removed_public_transcript_executable_bytes": 4930,
        })

    def test_every_directive_byte_has_one_semantic_disposition(self) -> None:
        self.assertEqual(len(self.result["rows"]), 2)
        for row in self.result["rows"]:
            self.assertEqual(
                row["directive_bytes"],
                row["raw_instruction_transcription_bytes"] +
                row["semantic_literal_bytes"],
            )
            self.assertLessEqual(row["directive_bytes"],
                                 row["routed_source_bytes"])
            self.assertTrue(row["remediation"])

    def test_literal_constants_are_not_condemned_as_instructions(self) -> None:
        literals = {Path(row["source"]).name: row["semantic_literal_bytes"]
                    for row in self.result["rows"]
                    if row["semantic_literal_bytes"]}
        self.assertEqual(literals, {
            "duration_delay.c": 12,
            "runtime_thread_pointer_422874.c": 4,
        })

    def test_unclassified_new_directive_fails_closed(self) -> None:
        original = Path.read_text
        target = ROOT / "components/apollo_main/core_overlay/format_span.c"

        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path == target:
                return text + '\n__asm__(".byte 0x00\\n");\n'
            return text

        with mock.patch.object(Path, "read_text", changed):
            with self.assertRaises(MODULE.AuditError):
                MODULE.analyze()

    def test_deleted_public_transcripts_are_digest_only_boundaries(self) -> None:
        self.assertTrue(self.result["public_source_scope_clean"])
        self.assertEqual(
            len(self.result["removed_public_transcript_boundaries"]), 2)
        for row in self.result["removed_public_transcript_boundaries"]:
            self.assertFalse((ROOT / row["path"]).exists())
            self.assertIn("absent_from_public_source", row["disposition"])

    def test_audit_is_software_only_and_does_not_mutate_production(self) -> None:
        self.assertEqual(self.result["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.result["production_files_modified"], [])
        self.assertTrue(self.result["source_ownership_suitable"])


if __name__ == "__main__":
    unittest.main()
