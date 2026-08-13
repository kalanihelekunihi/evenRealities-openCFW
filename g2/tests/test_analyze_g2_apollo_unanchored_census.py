#!/usr/bin/env python3
"""Guard the Apollo unanchored-function provenance census."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_apollo_unanchored_census.py"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)
PLAN = ROOT / "build/source/flash-plan.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFESTS = ROOT / "tools/manifests"

EXPECTED_BUCKETS = {
    # bucket: (functions, accepted_envelope_bytes, official_opaque_bytes)
    "lvgl": (1054, 103190, 97430),
    "cordio": (383, 28254, 27356),
    "ambiqsuite": (141, 10154, 10154),
    "ambiqsuite-ancc": (11, 888, 888),
    "cmsis-freertos": (60, 4568, 816),
    "cjson": (21, 2572, 2572),
    "iar-dlib": (12, 7496, 7462),
    "littlefs": (99, 7258, 7042),
    "tlsf": (23, 1122, 632),
    "tinyframe": (11, 366, 338),
    "easylogger": (7, 666, 0),
    "nanopb": (72, 8418, 816),
    "lz4": (3, 1220, 1190),
    "freetype": (2, 946, 946),
    "liblc3": (10, 1694, 1694),
    "first-party": (1782, 226536, 216564),
    "rejected-oversized-envelope": (8, 0, 0),
    "investigation-required-mixed": (38, 9380, 9032),
    "investigation-required-no-evidence": (1873, 312598, 290704),
}


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_apollo_unanchored_census", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class UnanchoredCensusUnitTests(unittest.TestCase):
    """Corpus-independent checks of the census rule tables and parsers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_every_bucket_key_has_provider_metadata(self) -> None:
        families = self.analyzer.PROVIDER_FAMILIES
        for key in EXPECTED_BUCKETS:
            self.assertIn(key, families)
            self.assertTrue(families[key]["label"])
            self.assertTrue(families[key]["ownership"])
        for key, meta in families.items():
            self.assertIn("label", meta)
            self.assertIn("ownership", meta)

    def test_manifest_family_rules_are_total(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(analyzer._manifest_family("packetcraft-cordio-att-main"), "cordio")
        self.assertEqual(analyzer._manifest_family("ambiq-cordio-hci-evt"), "ambiqsuite")
        self.assertEqual(analyzer._manifest_family("ambiqsuite-cordio-wsf-os"), "ambiqsuite")
        self.assertEqual(analyzer._manifest_family("ambiqsuite-ancc-profile"), "ambiqsuite-ancc")
        self.assertEqual(analyzer._manifest_family("cordio-wstr"), "cordio")
        self.assertEqual(analyzer._manifest_family("cmsis-freertos-v10.5.1-linked"), "cmsis-freertos")
        self.assertEqual(analyzer._manifest_family("g2-json-parser"), "cjson")
        self.assertEqual(analyzer._manifest_family("g2-iar-float-exponent"), "iar-dlib")
        self.assertEqual(
            analyzer._manifest_family("g2-freertos-plus-cli-filesystem"),
            "freertos-plus-cli",
        )
        # g2-lvgl-font-manager is the first-party app\gui\common glue object,
        # not LVGL itself.
        self.assertEqual(analyzer._manifest_family("g2-lvgl-font-manager"), "first-party")
        self.assertEqual(analyzer._manifest_family("g2-dashboard"), "first-party")
        with self.assertRaises(analyzer.CensusError):
            analyzer._manifest_family("unknown-vendor-module")

    def test_oversized_envelope_census_is_pinned(self) -> None:
        entries = self.analyzer.EXPECTED_OVERSIZED_ENTRIES
        self.assertEqual(len(entries), 8)
        self.assertEqual(tuple(sorted(entries)), entries)
        self.assertIn(0x005FA120, entries)

    def test_dlib_signature_strings_are_annex_k_unique(self) -> None:
        strings = self.analyzer.DLIB_SIGNATURE_STRINGS
        self.assertEqual(len(strings), 10)
        self.assertTrue(any("printf_s" in value for value in strings))
        self.assertTrue(any("scanf_s" in value for value in strings))
        self.assertTrue(any("constraint handler" in value for value in strings))

    def test_documented_family_evidence_is_well_formed(self) -> None:
        for evidence in self.analyzer.DOCUMENTED_FAMILY_EVIDENCE:
            self.assertIn(evidence["family"], self.analyzer.PROVIDER_FAMILIES)
            self.assertIn(evidence["kind"], ("span", "entries"))
            self.assertTrue(evidence["source"].startswith("docs/"))
            if evidence["kind"] == "span":
                self.assertLess(evidence["start"], evidence["end_exclusive"])
            else:
                self.assertTrue(evidence["entries"])

    def test_manifest_loader_fails_closed_on_unknown_stem(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = sorted(path.name for path in MANIFESTS.glob("*-function-map.tsv"))
            # Rebuild a synthetic directory with the expected file count but
            # one stem that has no provider-family rule.
            for index, name in enumerate(names):
                target = root / (name if index else "zz9-unknown-module-function-map.tsv")
                target.write_text(
                    "stock_start\tstock_end_exclusive\n0x00438000\t0x00438010\n",
                    encoding="utf-8",
                )
            with self.assertRaises(analyzer.CensusError):
                analyzer.load_manifest_function_maps(root)

    def test_manifest_loader_fails_closed_on_file_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(self.analyzer.CensusError):
                self.analyzer.load_manifest_function_maps(Path(directory))

    def test_manifest_loader_fails_closed_on_unknown_schema(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = sorted(path.name for path in MANIFESTS.glob("*-function-map.tsv"))
            for index, name in enumerate(names):
                header = (
                    "bogus_column\tanother\n1\t2\n"
                    if index == 0
                    else "stock_start\tstock_end_exclusive\n0x00438000\t0x00438010\n"
                )
                (root / name).write_text(header, encoding="utf-8")
            with self.assertRaises(analyzer.CensusError):
                analyzer.load_manifest_function_maps(root)

    def test_liblc3_entry_map_is_authenticated(self) -> None:
        entries = self.analyzer.load_liblc3_entries(MANIFESTS)
        self.assertEqual(
            tuple(sorted(entries)), self.analyzer.EXPECTED_LIBLC3_PUBLIC_ENTRIES
        )
        self.assertEqual(entries[0x0059138A], "lc3_encode")

    def test_liblc3_entry_map_fails_closed_on_mutation(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy(MANIFESTS / "g2-liblc3-public-entry-map.tsv", root)
            target = root / "g2-liblc3-public-entry-map.tsv"
            text = target.read_text(encoding="utf-8").replace(
                "lc3_encode\t0x0059138A\t", "lc3_encode\t0x0059138C\t", 1
            )
            target.write_text(text, encoding="utf-8")
            with self.assertRaises(analyzer.CensusError):
                analyzer.load_liblc3_entries(root)


@unittest.skipUnless(
    CORPUS.is_dir() and PLAN.is_file() and REPORT.is_file(),
    "authenticated corpus/current build unavailable",
)
class UnanchoredCensusAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_unanchored_set_reconciles_with_embedded_path_census(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["corpus_functions"], 7_370)
        self.assertEqual(reconciliation["path_anchored_functions"], 1_760)
        self.assertEqual(reconciliation["unanchored_functions"], 5_610)
        self.assertEqual(reconciliation["oversized_rejected_envelopes"], 8)

    def test_byte_accounting_reconciles_with_origin_accounting(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["unanchored_official_opaque_bytes"], 675_636)
        self.assertEqual(
            reconciliation["origin_accounting_unanchored_bytes"], 675_636
        )
        total = sum(bucket["official_opaque_bytes"] for bucket in self.report["buckets"])
        self.assertEqual(total, 675_636)
        functions = sum(bucket["functions"] for bucket in self.report["buckets"])
        self.assertEqual(functions, 5_610)

    def test_bucket_census_is_pinned(self) -> None:
        actual = {
            bucket["bucket"]: (
                bucket["functions"],
                bucket["accepted_envelope_bytes"],
                bucket["official_opaque_bytes"],
            )
            for bucket in self.report["buckets"]
        }
        self.assertEqual(actual, EXPECTED_BUCKETS)

    def test_evidence_and_confidence_classes_are_closed(self) -> None:
        valid_evidence = {
            "analyzer-artifact",
            "closed-module-manifest",
            "documented-family-evidence",
            "library-string-signature",
            "call-topology-single-family",
            "link-order-sandwich",
            "call-topology-mixed",
            "none",
        }
        valid_confidence = {"high", "medium", "low", "none"}
        for record in self.report["functions"]:
            self.assertIn(record["evidence"], valid_evidence)
            self.assertIn(record["confidence"], valid_confidence)
            self.assertIsNotNone(record["bucket"])

    def test_documented_family_functions_are_pinned(self) -> None:
        by_entry = {record["entry"]: record for record in self.report["functions"]}
        # Exact FT_Done_Face span from the FreeType recovery audit.
        record = by_entry[0x00526814]
        self.assertEqual(record["bucket"], "freetype")
        self.assertEqual(record["evidence"], "documented-family-evidence")
        self.assertEqual(record["confidence"], "high")
        self.assertEqual(
            (record["body_start"], record["body_end_exclusive"]),
            (0x00526814, 0x0052687E),
        )
        # LZ4 decoder trio from the upstream inventory.
        for entry in (0x0054EE90, 0x0054EF08, 0x0054F338):
            self.assertEqual(by_entry[entry]["bucket"], "lz4")
            self.assertEqual(by_entry[entry]["confidence"], "high")
        # liblc3 public entries from the entry-map manifest.
        for entry in (0x00590E64, 0x00590F78, 0x00591374, 0x0059138A):
            self.assertEqual(by_entry[entry]["bucket"], "liblc3")
        # IAR DLIB printf/scanf/constraint-handler cluster.
        self.assertEqual(by_entry[0x00481836]["bucket"], "iar-dlib")
        self.assertEqual(
            by_entry[0x00481836]["evidence"], "library-string-signature"
        )
        # nanopb runtime span member.
        self.assertEqual(by_entry[0x0048F3BE]["bucket"], "nanopb")

    def test_oversized_envelopes_are_not_family_classified(self) -> None:
        by_entry = {record["entry"]: record for record in self.report["functions"]}
        for entry in self.analyzer.EXPECTED_OVERSIZED_ENTRIES:
            self.assertEqual(
                by_entry[entry]["bucket"], "rejected-oversized-envelope"
            )
            self.assertEqual(by_entry[entry]["official_opaque_bytes"], 0)

    def test_checked_in_manifests_match_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "g2-apollo-unanchored-census-buckets.tsv").write_text(
                self.analyzer.buckets_tsv(self.report), encoding="utf-8"
            )
            (root / "g2-apollo-unanchored-census-functions.tsv").write_text(
                self.analyzer.functions_tsv(self.report), encoding="utf-8"
            )
            for name in (
                "g2-apollo-unanchored-census-buckets.tsv",
                "g2-apollo-unanchored-census-functions.tsv",
            ):
                self.assertEqual(
                    (root / name).read_bytes(),
                    (MANIFESTS / name).read_bytes(),
                    f"checked-in manifest drifted: {name}",
                )

    def test_documented_span_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.DOCUMENTED_FAMILY_EVIDENCE
        mutated = tuple(
            dict(evidence, start=0x00790000, end_exclusive=0x00790010)
            if evidence["family"] == "nanopb"
            else evidence
            for evidence in original
        )
        analyzer.DOCUMENTED_FAMILY_EVIDENCE = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.DOCUMENTED_FAMILY_EVIDENCE = original


if __name__ == "__main__":
    unittest.main()
