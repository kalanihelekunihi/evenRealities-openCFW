#!/usr/bin/env python3
"""Guard the FreeType 2.9.1 engine census."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_freetype_engine_census.py"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)
MANIFESTS = ROOT / "tools/manifests"
CENSUS_TSV = MANIFESTS / "g2-freetype-engine-census.tsv"
SUMMARY_JSON = MANIFESTS / "g2-freetype-engine-census-summary.json"
G2_FTMODULE = ROOT / "third_party/freetype/g2-config/freetype/config/ftmodule.h"
PROVENANCE = ROOT / "third_party/freetype/PROVENANCE.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_freetype_engine_census", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreetypeCensusUnitTests(unittest.TestCase):
    """Corpus-independent checks of the census rule tables and loaders."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_module_rules_are_total(self) -> None:
        analyzer = self.analyzer
        # Every ftmodule.h class has a module rule, and every rule names a
        # known FreeType source module.
        self.assertEqual(
            tuple(analyzer.FTMODULE_CLASS_MODULE), analyzer.EXPECTED_FTMODULE_CLASSES
        )
        for name in analyzer.EXPECTED_FTMODULE_CLASSES:
            self.assertIn(analyzer.FTMODULE_CLASS_MODULE[name], analyzer.MODULES)
        for module, meta in analyzer.MODULES.items():
            self.assertTrue(meta["label"])
            self.assertTrue(
                (analyzer.FREETYPE_SNAPSHOT / "src" / module).is_dir(),
                f"missing snapshot module directory: {module}",
            )
        for bucket in analyzer.CENSUS_BUCKETS:
            self.assertTrue(bucket)

    def test_g2_module_order_is_pinned(self) -> None:
        modules = self.analyzer.load_g2_modules()
        self.assertEqual(
            modules,
            (
                "autofit",
                "truetype",
                "cff",
                "psaux",
                "psnames",
                "pshinter",
                "sfnt",
                "smooth",
            ),
        )

    def test_g2_ftmodule_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "ftmodule.h"
            mutated.write_bytes(
                G2_FTMODULE.read_bytes().replace(b"psaux_module_class", b"psaxu_module_class")
            )
            with self.assertRaises(analyzer.CensusError):
                analyzer.load_g2_modules(mutated)

    def test_recovery_audit_anchors_are_well_formed(self) -> None:
        analyzer = self.analyzer
        entries = [row[0] for row in analyzer.RECOVERY_AUDIT_ANCHORS]
        self.assertEqual(len(entries), len(set(entries)))
        for entry, module, label, citation in analyzer.RECOVERY_AUDIT_ANCHORS:
            self.assertIn(module, analyzer.MODULES)
            self.assertTrue(label)
            self.assertTrue(citation.startswith("freetype-recovery-audit.md"))
        by_entry = dict((row[0], row) for row in analyzer.RECOVERY_AUDIT_ANCHORS)
        self.assertEqual(by_entry[0x00526814][1:3], ("base", "FT_Done_Face"))
        self.assertEqual(by_entry[0x005264A6][1:3], ("base", "FT_Open_Face"))

    def test_string_signature_pins_are_well_formed(self) -> None:
        analyzer = self.analyzer
        entries = [row[0] for row in analyzer.EXPECTED_STRING_SIGNATURES]
        self.assertEqual(len(entries), len(set(entries)))
        for entry, module, literals in analyzer.EXPECTED_STRING_SIGNATURES:
            self.assertIn(module, analyzer.MODULES)
            self.assertTrue(literals)
            self.assertEqual(tuple(sorted(literals)), tuple(literals))
            for literal in literals:
                self.assertGreaterEqual(
                    len(literal), analyzer.MIN_SIGNATURE_LITERAL
                )

    def test_service_pins_are_well_formed(self) -> None:
        analyzer = self.analyzer
        for _address, module, ids in analyzer.EXPECTED_SERVICE_TABLES:
            self.assertIn(module, analyzer.MODULES)
            self.assertTrue(ids)
        for entry, module, service_id in analyzer.EXPECTED_SERVICE_CALLBACKS:
            self.assertIn(module, analyzer.MODULES)
            table_ids = {
                id_
                for _address, table_module, ids in analyzer.EXPECTED_SERVICE_TABLES
                if table_module == module
                for id_ in ids
            }
            self.assertIn(service_id, table_ids)
        # The pinned callback set must be unique per entry.
        entries = [row[0] for row in analyzer.EXPECTED_SERVICE_CALLBACKS]
        self.assertEqual(len(entries), len(set(entries)))

    def test_census_pins_reconcile(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(
            analyzer.EXPECTED_FRONTIER_OFFICIAL_BYTES
            + analyzer.EXPECTED_PARENT_FREETYPE_BYTES,
            analyzer.EXPECTED_CENSUS_OFFICIAL_BYTES,
        )
        self.assertEqual(
            analyzer.EXPECTED_FRONTIER_FUNCTIONS
            + len(analyzer.EXPECTED_PARENT_FREETYPE_ENTRIES),
            analyzer.EXPECTED_CENSUS_FUNCTIONS,
        )
        self.assertEqual(
            sum(row[0] for row in analyzer.EXPECTED_BUCKET_CENSUS.values()),
            analyzer.EXPECTED_CENSUS_FUNCTIONS,
        )
        self.assertEqual(
            sum(row[1] for row in analyzer.EXPECTED_BUCKET_CENSUS.values()),
            analyzer.EXPECTED_CENSUS_OFFICIAL_BYTES,
        )
        self.assertEqual(
            sum(analyzer.EXPECTED_EVIDENCE_COUNTS.values()),
            analyzer.EXPECTED_CENSUS_FUNCTIONS,
        )
        self.assertEqual(len(analyzer.EXPECTED_OVERSIZED_ENTRIES), 8)

    def test_snapshot_provenance_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "PROVENANCE.json"
            mutated.write_bytes(
                PROVENANCE.read_bytes().replace(b'"sha256"', b'"sha255"', 1)
            )
            with self.assertRaises(analyzer.CensusError):
                analyzer.Snapshot(analyzer.FREETYPE_SNAPSHOT, mutated)

    def test_snapshot_read_requires_provenance_record(self) -> None:
        analyzer = self.analyzer
        snapshot = analyzer.Snapshot()
        with self.assertRaises(analyzer.CensusError):
            snapshot.read_text("src/base/not-a-file.c")
        # A recorded file verifies and reads.
        self.assertIn("FT_Done_Face", snapshot.read_text("include/freetype/freetype.h"))


@unittest.skipUnless(
    CORPUS.is_dir() and CENSUS_TSV.is_file() and SUMMARY_JSON.is_file(),
    "authenticated corpus/census manifests unavailable",
)
class FreetypeCensusAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_frontier_reconciliation_is_exact(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["parent_frontier_functions"], 342)
        self.assertEqual(reconciliation["parent_frontier_official_bytes"], 75_016)
        self.assertEqual(reconciliation["parent_freetype_bucket_functions"], 2)
        self.assertEqual(reconciliation["parent_freetype_bucket_official_bytes"], 946)
        self.assertEqual(reconciliation["census_functions"], 344)
        self.assertEqual(reconciliation["census_official_bytes"], 75_962)
        total = sum(bucket["functions"] for bucket in self.report["buckets"])
        self.assertEqual(total, 344)
        total_bytes = sum(bucket["official_opaque_bytes"] for bucket in self.report["buckets"])
        self.assertEqual(total_bytes, 75_962)

    def test_bucket_census_is_pinned(self) -> None:
        actual = {
            bucket["bucket"]: (bucket["functions"], bucket["official_opaque_bytes"])
            for bucket in self.report["buckets"]
        }
        self.assertEqual(actual, self.analyzer.EXPECTED_BUCKET_CENSUS)
        self.assertEqual(
            self.report["evidence_counts"], self.analyzer.EXPECTED_EVIDENCE_COUNTS
        )

    def test_evidence_and_confidence_classes_are_closed(self) -> None:
        valid_evidence = {
            "recovery-audit-anchor",
            "module-string-signature",
            "module-class-callback",
            "raster-funcs-callback",
            "service-record-callback",
            "call-topology-single-module",
            "call-topology-multi-module",
            "link-order-sandwich",
            "none",
        }
        valid_confidence = {"high", "medium", "low", "none"}
        valid_buckets = set(self.analyzer.CENSUS_BUCKETS)
        for record in self.report["functions"]:
            self.assertIn(record["bucket"], valid_buckets)
            self.assertIn(record["evidence"], valid_evidence)
            self.assertIn(record["confidence"], valid_confidence)

    def test_anchor_functions_are_pinned(self) -> None:
        by_entry = {record["entry"]: record for record in self.report["functions"]}
        record = by_entry[0x00526814]
        self.assertEqual(record["bucket"], "base")
        self.assertEqual(record["evidence"], "recovery-audit-anchor")
        self.assertEqual(record["confidence"], "high")
        self.assertEqual(
            (record["body_start"], record["body_end_exclusive"]),
            (0x00526814, 0x0052687E),
        )
        record = by_entry[0x005264A6]
        self.assertEqual(record["bucket"], "base")
        self.assertEqual(record["evidence"], "recovery-audit-anchor")
        # String-signature members: ps_property_set/ps_property_get stay base
        # even though the cff properties service record points at them.
        for entry in (0x00527F0A, 0x00527FF2):
            self.assertEqual(by_entry[entry]["bucket"], "base")
            self.assertEqual(
                by_entry[entry]["evidence"], "module-string-signature"
            )
        # The two resolved seed conflicts are exactly those two functions.
        conflicts = self.report["resolved_seed_conflicts"]
        self.assertEqual(
            sorted(row["entry"] for row in conflicts),
            ["0x00527F0A", "0x00527FF2"],
        )
        self.assertTrue(all(row["kept_module"] == "base" for row in conflicts))

    def test_unattributed_frontier_is_explicit(self) -> None:
        records = self.report["functions"]
        un = [record for record in records if record["bucket"] == "investigation-required"]
        self.assertEqual(len(un), 216)
        self.assertEqual(sum(record["official_opaque_bytes"] for record in un), 59_392)
        # Every 0x51xxxx function stays investigation-required.
        low = [record for record in un if record["entry"] < 0x00520000]
        self.assertEqual(len(low), 87)
        self.assertEqual(sum(record["official_opaque_bytes"] for record in low), 36_812)
        # The peripheral-register candidate is not FreeType-claimed.
        by_entry = {record["entry"]: record for record in records}
        self.assertEqual(
            by_entry[0x005202EC]["bucket"], "investigation-required"
        )

    def test_checked_in_manifests_match_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / CENSUS_TSV.name).write_text(
                self.analyzer.functions_tsv(self.report), encoding="utf-8"
            )
            (root / SUMMARY_JSON.name).write_text(
                self.analyzer.summary_json(self.report), encoding="utf-8"
            )
            for path in (CENSUS_TSV, SUMMARY_JSON):
                self.assertEqual(
                    (root / path.name).read_bytes(),
                    path.read_bytes(),
                    f"checked-in manifest drifted: {path.name}",
                )

    def test_anchor_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.RECOVERY_AUDIT_ANCHORS
        mutated = tuple(
            (0x005242FE, module, label, citation) if entry == 0x005242FC else (entry, module, label, citation)
            for entry, module, label, citation in original
        )
        analyzer.RECOVERY_AUDIT_ANCHORS = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.RECOVERY_AUDIT_ANCHORS = original

    def test_string_signature_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_STRING_SIGNATURES
        analyzer.EXPECTED_STRING_SIGNATURES = original[1:]
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_STRING_SIGNATURES = original

    def test_bucket_census_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_BUCKET_CENSUS
        analyzer.EXPECTED_BUCKET_CENSUS = dict(original, base=(129, 16_570))
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_BUCKET_CENSUS = original


if __name__ == "__main__":
    unittest.main()
