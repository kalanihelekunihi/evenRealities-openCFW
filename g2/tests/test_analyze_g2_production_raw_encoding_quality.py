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
            "production_routed_sources_with_directives": 32,
            "routed_source_bytes_in_affected_sources": 11498,
            "directive_bytes": 1858,
            "raw_instruction_transcription_bytes": 1830,
            "semantic_literal_bytes": 28,
            "source_owned_bytes_currently_overstated": 1830,
            "fully_raw_byte_body_bytes": 0,
            "public_raw_executable_transcript_files": 131,
            "public_unrouted_raw_instruction_transcript_files": 102,
            "public_unrouted_raw_instruction_transcript_bytes": 584954,
            "public_unrouted_raw_instruction_overlay_referenced_files": 102,
            "public_unrouted_raw_instruction_overlay_referenced_bytes": 584954,
            "public_unrouted_raw_instruction_unreferenced_files": 0,
            "public_unrouted_raw_instruction_unreferenced_bytes": 0,
            "removed_public_transcript_files": 4,
            "removed_public_transcript_executable_bytes": 21146,
            "untracked_overlay_source_inputs": 0,
        })

    def test_every_directive_byte_has_one_semantic_disposition(self) -> None:
        self.assertEqual(len(self.result["rows"]), 32)
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
            "runtime_bl006_spot_trim_span_427e54.c": 12,
            "runtime_thread_pointer_422874.c": 4,
        })

    def test_raw_instruction_transcripts_are_not_source_ownership_debt(self) -> None:
        raw = {
            Path(row["source"]).name: row["raw_instruction_transcription_bytes"]
            for row in self.result["rows"]
            if row["raw_instruction_transcription_bytes"]
        }
        self.assertEqual(raw, {
            "runtime_liblc3_am142_0x59aa84.c": 518,
            "runtime_liblc3_am142_0x59c800.c": 8,
            "runtime_liblc3_am142_0x59c820.c": 8,
            "runtime_liblc3_am142_0x59c83e.c": 4,
            "runtime_liblc3_am142_0x59c876.c": 20,
            "runtime_liblc3_am142_0x59c1c4.c": 4,
            "runtime_liblc3_am142_0x59c204.c": 224,
            "runtime_liblc3_am142_0x59c7ac.c": 16,
            "runtime_liblc3_am142_0x59b5c4.c": 20,
            "runtime_liblc3_am142_0x59c980.c": 10,
            "runtime_liblc3_am142_0x59ca2c.c": 22,
            "runtime_liblc3_am142_0x59b6d0.c": 4,
            "runtime_liblc3_am142_0x59b4b8.c": 28,
            "runtime_liblc3_am142_0x59b714.c": 10,
            "runtime_liblc3_am142_0x59b76c.c": 24,
            "runtime_liblc3_am142_0x59b80c.c": 4,
            "runtime_liblc3_am142_0x59b852.c": 124,
            "runtime_liblc3_am142_0x59ba96.c": 14,
            "runtime_liblc3_am142_0x59bae4.c": 364,
            "runtime_liblc3_am142_0x59cafc.c": 8,
            "runtime_liblc3_am142_0x59cb42.c": 30,
            "runtime_liblc3_am142_0x59cc40.c": 20,
            "runtime_liblc3_am142_0x59ccdc.c": 10,
            "runtime_liblc3_am142_0x59cd86.c": 12,
            "runtime_liblc3_am142_0x59ce1e.c": 38,
            "runtime_liblc3_am142_0x59cf1a.c": 142,
            "runtime_liblc3_am142_0x59d3b2.c": 26,
            "runtime_liblc3_am142_0x59d380.c": 14,
            "runtime_liblc3_am142_0x59d8f0.c": 104,
        })
        self.assertFalse(self.result["source_ownership_suitable"])

    def test_tracked_unrouted_raw_instruction_sources_are_pinned(self) -> None:
        debt = self.result["public_unrouted_raw_instruction_sources"]
        self.assertEqual(len(debt), 102)
        self.assertEqual(
            sum(row["inst_directive_bytes"] for row in debt), 584954)
        self.assertTrue(all(row["overlay_referenced"] for row in debt))
        self.assertEqual(debt[0]["source"],
                         "components/apollo_main/core_overlay/runtime_liblc3_am023_helpers.c")
        self.assertEqual(debt[-1]["source"],
                         "components/apollo_main/core_overlay/runtime_liblc3_am183_helpers.c")

    def test_overlay_source_inputs_must_be_tracked(self) -> None:
        untracked = self.result["untracked_overlay_source_inputs"]
        self.assertEqual(untracked, [])

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

    def test_retired_public_transcripts_are_digest_only_boundaries(self) -> None:
        self.assertTrue(self.result["public_source_scope_clean"])
        self.assertEqual(
            len(self.result["removed_public_transcript_boundaries"]), 4)
        for row in self.result["removed_public_transcript_boundaries"]:
            path = ROOT / row["path"]
            if "replaced_by_structured_production_c" in row["disposition"]:
                self.assertTrue(path.is_file())
                self.assertEqual(
                    sum(MODULE._directive_bytes(path.read_text()).values()), 0)
            else:
                self.assertFalse(path.exists())
                self.assertIn("absent_from_public_source", row["disposition"])

    def test_audit_is_software_only_and_does_not_mutate_production(self) -> None:
        self.assertEqual(self.result["hardware_validation"],
                         "blocked by unavailable physical evidence")
        self.assertEqual(self.result["production_files_modified"], [])
        self.assertFalse(self.result["source_ownership_suitable"])

    def test_designated_initializers_are_not_mistaken_for_directives(self) -> None:
        # `{.word = value}` and `object.word = value` are C99 designated
        # initializers / member access, not GNU-assembler `.word` directives.
        # A real directive is never followed by `=`; only by its operand list.
        empty = {name: 0 for name in MODULE.WIDTH}
        self.assertEqual(MODULE._directive_bytes(
            "typedef union { uint32_t word; } r;\n"
            "void f(void) { r v = {.word = 1}; v.word = 2; (void)v.word; }\n"
        ), empty)
        expected = dict(empty)
        expected["word"] = 4
        self.assertEqual(MODULE._directive_bytes(
            '__asm__(".word 0x1234\\n");\n'
        ), expected)


if __name__ == "__main__":
    unittest.main()
