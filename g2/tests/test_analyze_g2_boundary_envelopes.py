#!/usr/bin/env python3
"""Guard the Apollo boundary-role and oversized-envelope audit."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_boundary_envelopes.py"
CENSUS_ANALYZER = ROOT / "tools" / "analyze_g2_apollo_unanchored_census.py"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)
PLAN = ROOT / "build/source/flash-plan.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFESTS = ROOT / "tools/manifests"

MIXED_TSV = "g2-mixed-boundary-map.tsv"
ENVELOPE_TSV = "g2-oversized-envelope-regions.tsv"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_boundary_envelopes", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def synthetic_image(size: int = 4096) -> tuple[bytes, int, int]:
    """(blob, load_base, image_end) for corpus-independent classifier tests."""

    return bytes(size), 0, size


def bl_instruction() -> bytes:
    """A Thumb-2 BL with offset 0 (target = own address + 4)."""

    return b"\x00\xf0\x00\xf8"


class BoundaryRuleUnitTests(unittest.TestCase):
    """Corpus-independent checks of the closed rule tables and validators."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_role_table_matches_seam_census_exactly(self) -> None:
        analyzer = self.analyzer
        seams = {
            tuple(sorted(seam.split("|"))) for seam in analyzer.EXPECTED_SEAM_CENSUS
        }
        self.assertEqual(seams, set(analyzer.BOUNDARY_ROLES))
        for key, role in analyzer.BOUNDARY_ROLES.items():
            self.assertEqual(tuple(sorted(key)), key)
            self.assertTrue(role["role"])
            self.assertTrue(role["label"])
            self.assertTrue(role["flow"])

    def test_boundary_role_fails_closed_on_unknown_seam(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(
            analyzer.boundary_role(("first-party", "lvgl"))["role"],
            "g2-lvgl-ui-adapter",
        )
        with self.assertRaises(analyzer.BoundaryError):
            analyzer.boundary_role(("freetype", "lvgl"))

    def test_seam_census_validator(self) -> None:
        analyzer = self.analyzer
        analyzer.validate_seam_census(dict(analyzer.EXPECTED_SEAM_CENSUS))
        with self.assertRaises(analyzer.BoundaryError):
            analyzer.validate_seam_census({"first-party|lvgl": 19})
        with self.assertRaises(analyzer.BoundaryError):
            analyzer.validate_seam_census(
                {**analyzer.EXPECTED_SEAM_CENSUS, "freetype|lvgl": 1}
            )

    def test_mixed_bucket_constants_reconcile(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(analyzer.EXPECTED_MIXED_FUNCTION_COUNT, 38)
        self.assertEqual(sum(analyzer.EXPECTED_SEAM_CENSUS.values()), 38)
        self.assertEqual(analyzer.EXPECTED_MIXED_ENVELOPE_BYTES, 9_380)
        self.assertEqual(analyzer.EXPECTED_MIXED_OFFICIAL_BYTES, 9_032)

    def test_envelope_region_pins_are_total(self) -> None:
        analyzer = self.analyzer
        spec = importlib.util.spec_from_file_location("census_mod", CENSUS_ANALYZER)
        census = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = census
        spec.loader.exec_module(census)
        self.assertEqual(
            tuple(sorted(analyzer.EXPECTED_ENVELOPE_REGIONS)),
            census.EXPECTED_OVERSIZED_ENTRIES,
        )
        for entry, expected in analyzer.EXPECTED_ENVELOPE_REGIONS.items():
            span = expected["body_end_exclusive"] - expected["body_start"]
            self.assertGreater(span, 16_384)
            self.assertEqual(sum(expected["classes"].values()), span)
            for name in expected["classes"]:
                self.assertIn(name, analyzer.REGION_CLASSES)

    def test_envelope_partition_validator_fails_closed(self) -> None:
        analyzer = self.analyzer
        expected = analyzer.EXPECTED_ENVELOPE_REGIONS[0x00513E2E]
        analyzer.validate_envelope_partition(
            0x00513E2E,
            expected["body_start"],
            expected["body_end_exclusive"],
            dict(expected["classes"]),
        )
        with self.assertRaises(analyzer.BoundaryError):
            analyzer.validate_envelope_partition(
                0x00513E2E,
                expected["body_start"],
                expected["body_end_exclusive"],
                {**expected["classes"], "rodata-table": 511},
            )
        with self.assertRaises(analyzer.BoundaryError):
            analyzer.validate_envelope_partition(
                0x00513E2E,
                expected["body_start"] + 2,
                expected["body_end_exclusive"],
                dict(expected["classes"]),
            )
        with self.assertRaises(analyzer.BoundaryError):
            analyzer.validate_envelope_partition(
                0x00FFFFFF,
                expected["body_start"],
                expected["body_end_exclusive"],
                dict(expected["classes"]),
            )
        with self.assertRaises(analyzer.BoundaryError):
            analyzer.validate_envelope_partition(
                0x00513E2E,
                expected["body_start"],
                expected["body_end_exclusive"],
                {**expected["classes"], "bogus-class": 0},
            )

    def test_classify_piece_zero_fill_and_alignment_gap(self) -> None:
        analyzer = self.analyzer
        blob, base, end = synthetic_image()
        self.assertEqual(
            analyzer.classify_piece(blob, 0, 512, base, end), ("zero-fill", "high")
        )
        self.assertEqual(
            analyzer.classify_piece(blob, 0, 12, base, end), ("alignment-gap", "low")
        )

    def test_classify_piece_ascii_strings(self) -> None:
        analyzer = self.analyzer
        blob = b"Hello, G2 display! " * 32
        self.assertEqual(
            analyzer.classify_piece(blob, 0, len(blob), 0, len(blob)),
            ("ascii-strings", "high"),
        )

    def test_classify_piece_thumb_code(self) -> None:
        analyzer = self.analyzer
        blob = bl_instruction() * 128  # 512 bytes of dense in-image BLs
        self.assertEqual(
            analyzer.classify_piece(blob, 0, len(blob), 0, len(blob)),
            ("thumb-code-candidate", "high"),
        )

    def test_classify_piece_mixed_code_data(self) -> None:
        analyzer = self.analyzer
        blob = bytearray(b"\xaa" * 1024)
        blob[100:104] = bl_instruction()
        blob[200:204] = bl_instruction()
        self.assertEqual(
            analyzer.classify_piece(bytes(blob), 0, len(blob), 0, len(blob)),
            ("mixed-code-data", "medium"),
        )

    def test_classify_piece_opaque_blob_and_rodata(self) -> None:
        analyzer = self.analyzer
        blob = bytes(range(256)) * 4  # 1024 bytes, 256 distinct values
        self.assertEqual(
            analyzer.classify_piece(blob, 0, len(blob), 0, len(blob)),
            ("opaque-blob", "medium"),
        )
        table = b"\x01\x02\x04\x08" * 64  # low entropy, no code evidence
        self.assertEqual(
            analyzer.classify_piece(table, 0, len(table), 0, len(table)),
            ("rodata-table", "low"),
        )

    def test_classify_span_is_byte_exact_and_carves_tables(self) -> None:
        analyzer = self.analyzer
        base = 0x1000
        blob = bytearray(8192)
        # 64-byte span at base: [+0,+16) accepted code, [+16,+32) pointer
        # run (4 words with an odd majority -> thumb-jump-table),
        # [+32,+64) zero fill.  load_base 0x1000 keeps NUL words from
        # aliasing as image pointers.
        for index, word in enumerate(
            (base + 0x101, base + 0x205, base + 0x309, base + 0x400)
        ):
            blob[16 + index * 4 : 20 + index * 4] = word.to_bytes(4, "little")
        rows = analyzer.classify_span(
            bytes(blob), base, base + 64, [(base, base + 16)], base, base + len(blob)
        )
        self.assertEqual(sum(b - a for a, b, _c, _k in rows), 64)
        classes = [(a - base, b - base, c) for a, b, c, _k in rows]
        self.assertEqual(
            classes,
            [
                (0, 16, "accepted-function-code"),
                (16, 32, "thumb-jump-table"),
                (32, 64, "zero-fill"),
            ],
        )

    def test_classify_span_carves_even_pointer_table(self) -> None:
        analyzer = self.analyzer
        base = 0x1000
        blob = bytearray(b"\xaa" * 8192)
        for index, word in enumerate(
            (base + 0x100, base + 0x204, base + 0x308, 0x20000100)
        ):
            blob[32 + index * 4 : 36 + index * 4] = word.to_bytes(4, "little")
        rows = analyzer.classify_span(
            bytes(blob), base, base + 64, [], base, base + len(blob)
        )
        table = [row for row in rows if row[2] == "pointer-table"]
        self.assertEqual(len(table), 1)
        self.assertEqual((table[0][0], table[0][1]), (base + 32, base + 48))
        self.assertEqual(sum(b - a for a, b, _c, _k in rows), 64)


@unittest.skipUnless(
    CORPUS.is_dir() and PLAN.is_file() and REPORT.is_file(),
    "authenticated corpus/current build unavailable",
)
class BoundaryAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_frontier_reconciliation_is_pinned(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["mixed_functions"], 38)
        self.assertEqual(reconciliation["mixed_envelope_bytes"], 9_380)
        self.assertEqual(reconciliation["mixed_official_opaque_bytes"], 9_032)
        self.assertEqual(reconciliation["oversized_envelopes"], 8)
        self.assertEqual(
            reconciliation["seam_census"], self.analyzer.EXPECTED_SEAM_CENSUS
        )

    def test_every_mixed_function_has_total_role_assignment(self) -> None:
        analyzer = self.analyzer
        rows = self.report["boundary_functions"]
        self.assertEqual(len(rows), 38)
        roles = {role["role"] for role in analyzer.BOUNDARY_ROLES.values()}
        confidence = {"medium": 0, "low": 0}
        for row in rows:
            self.assertIn(row["boundary_role"], roles)
            self.assertIn(row["confidence"], confidence)
            confidence[row["confidence"]] += 1
            seam_families = set(row["seam"].split("|"))
            edge_families = {edge["family"] for edge in row["outbound_edges"]}
            self.assertEqual(seam_families, edge_families)
            self.assertTrue(row["outbound_edges"])
            if row["confidence"] == "medium":
                self.assertTrue(row["inbound_seed_callers"])
            else:
                self.assertFalse(row["inbound_seed_callers"])
        self.assertEqual(confidence, {"medium": 15, "low": 23})

    def test_named_boundary_functions_are_pinned(self) -> None:
        by_entry = {row["entry"]: row for row in self.report["boundary_functions"]}
        # LVGL display-port sync callback, already source-owned (0 official bytes).
        record = by_entry[0x004736F4]
        self.assertEqual(record["boundary_role"], "g2-lvgl-ui-adapter")
        self.assertEqual(record["official_opaque_bytes"], 0)
        self.assertEqual(record["confidence"], "low")
        # Cordio-invoked AmbiqSuite port callback.
        record = by_entry[0x00536426]
        self.assertEqual(record["boundary_role"], "ambiq-cordio-port-shim")
        self.assertEqual(record["inbound_seed_callers"], {"cordio": 3})
        # Application callback reached from the AmbiqSuite port layer.
        record = by_entry[0x004B42F0]
        self.assertEqual(record["boundary_role"], "g2-cordio-application-callback")
        self.assertEqual(record["inbound_seed_callers"], {"ambiqsuite": 1})
        # nanopb glue adjacent to the CMSIS-FreeRTOS wrapper.
        record = by_entry[0x00584C98]
        self.assertEqual(record["boundary_role"], "g2-nanopb-rtos-glue")

    def test_envelope_region_partitions_are_pinned(self) -> None:
        rows = self.report["envelope_regions"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            expected = self.analyzer.EXPECTED_ENVELOPE_REGIONS[row["entry"]]
            self.assertEqual(row["region_classes"], expected["classes"])
            self.assertEqual(
                sum(row["region_classes"].values()), row["span_bytes"]
            )
            self.assertEqual(
                row["accepted_function_code_bytes"] + row["interstitial_bytes"],
                row["span_bytes"],
            )
            self.assertIn(
                row["dominant_interstitial_class"],
                self.analyzer.REGION_CLASSES,
            )
            self.assertNotEqual(
                row["dominant_interstitial_class"], "accepted-function-code"
            )
        by_entry = {row["entry"]: row for row in rows}
        self.assertEqual(
            by_entry[0x00513E2E]["dominant_interstitial_class"], "rodata-table"
        )
        self.assertEqual(
            by_entry[0x005FA120]["dominant_interstitial_class"],
            "thumb-code-candidate",
        )
        # The 0x005FA120 span alone covers the union of all eight spans.
        self.assertEqual(
            (
                by_entry[0x005FA120]["body_start"],
                by_entry[0x005FA120]["body_end_exclusive"],
            ),
            (
                min(row["body_start"] for row in rows),
                max(row["body_end_exclusive"] for row in rows),
            ),
        )

    def test_checked_in_manifests_match_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / MIXED_TSV).write_text(
                self.analyzer.mixed_boundary_tsv(self.report), encoding="utf-8"
            )
            (root / ENVELOPE_TSV).write_text(
                self.analyzer.envelope_regions_tsv(self.report), encoding="utf-8"
            )
            for name in (MIXED_TSV, ENVELOPE_TSV):
                self.assertEqual(
                    (root / name).read_bytes(),
                    (MANIFESTS / name).read_bytes(),
                    f"checked-in manifest drifted: {name}",
                )

    def test_seam_census_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_SEAM_CENSUS
        analyzer.EXPECTED_SEAM_CENSUS = {**original, "first-party|lvgl": 19}
        try:
            with self.assertRaises(analyzer.BoundaryError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_SEAM_CENSUS = original


if __name__ == "__main__":
    unittest.main()
