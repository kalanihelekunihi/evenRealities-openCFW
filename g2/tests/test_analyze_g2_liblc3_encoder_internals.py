#!/usr/bin/env python3
"""Guard the liblc3 encoder-internals census."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_liblc3_encoder_internals.py"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)
PLAN = ROOT / "build/source/flash-plan.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFESTS = ROOT / "tools/manifests"
SNAPSHOT = ROOT / "third_party/liblc3"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_liblc3_encoder_internals", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def copy_snapshot_sources(target: Path) -> None:
    (target / "src").mkdir(parents=True)
    shutil.copy(SNAPSHOT / "SNAPSHOT.sha256", target)
    for name in load_analyzer().TABLE_SOURCES:
        shutil.copy(SNAPSHOT / "src" / name, target / "src" / name)


class EncoderInternalsUnitTests(unittest.TestCase):
    """Corpus-independent checks of the rule tables, parsers, and matchers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_closed_class_sets(self) -> None:
        analyzer = self.analyzer
        valid_status = {"module", "cluster", "investigation-required"}
        for entry, (status, module, evidence, confidence) in (
            analyzer.EXPECTED_ATTRIBUTION.items()
        ):
            self.assertIn(status, valid_status)
            if module is not None:
                self.assertIn(module, analyzer.MODULES)
                self.assertEqual(status, "module")
            else:
                self.assertEqual(status, "cluster")
            self.assertIn(evidence, analyzer.EVIDENCE_CLASSES)
            self.assertIn(confidence, analyzer.CONFIDENCE_ORDER[:-1])

    def test_expectation_tables_are_total_and_consistent(self) -> None:
        analyzer = self.analyzer
        pinned = analyzer.EXPECTED_ATTRIBUTION
        # Every dispatch callee except out-of-scope lc3_tns_analyze is pinned.
        for entry, module, _name in analyzer.EXPECTED_DISPATCH:
            if entry == 0x0059AA84:
                self.assertNotIn(entry, pinned)
                continue
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][1], module)
        # Every indirect/lc3-internal entry is pinned with the same module.
        for entry, module, callers, _text in (
            analyzer.EXPECTED_INDIRECT + analyzer.EXPECTED_LC3_INTERNALS
        ):
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][1], module)
            self.assertTrue(callers)
        # Every table-evidence entry is pinned at high confidence.
        for entry, (module, keys, _label) in analyzer.EXPECTED_TABLE_EVIDENCE.items():
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][1], module)
            self.assertEqual(pinned[entry][2], "upstream-table-match")
            self.assertEqual(pinned[entry][3], "high")
            for key in keys:
                self.assertEqual(analyzer.table_module(key), module)
        # Dispatch entries are unique and ordered.
        entries = [entry for entry, _m, _n in analyzer.EXPECTED_DISPATCH]
        self.assertEqual(len(entries), len(set(entries)))

    def test_reconciliation_constants_are_arithmetically_closed(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(len(analyzer.EXPECTED_ATTRIBUTION), 41)
        self.assertEqual(
            analyzer.EXPECTED_ATTRIBUTED_FUNCTIONS
            + analyzer.EXPECTED_INVESTIGATION_FUNCTIONS,
            analyzer.EXPECTED_SCOPE_FUNCTIONS,
        )
        self.assertEqual(
            analyzer.EXPECTED_ATTRIBUTED_OFFICIAL_BYTES
            + analyzer.EXPECTED_INVESTIGATION_OFFICIAL_BYTES,
            analyzer.EXPECTED_FRONTIER_OFFICIAL_BYTES
            + analyzer.EXPECTED_LIBLC3_BUCKET_OFFICIAL_BYTES,
        )
        # The cluster-only row (module None) is outside the module roll-up.
        module_functions = sum(
            functions for functions, _bytes in analyzer.EXPECTED_MODULE_SUMMARY.values()
        )
        module_bytes = sum(
            bytes_ for _functions, bytes_ in analyzer.EXPECTED_MODULE_SUMMARY.values()
        )
        self.assertEqual(module_functions, analyzer.EXPECTED_ATTRIBUTED_FUNCTIONS - 1)
        self.assertEqual(module_bytes, analyzer.EXPECTED_ATTRIBUTED_OFFICIAL_BYTES - 12)

    def test_snapshot_table_parser_census(self) -> None:
        tables = self.analyzer.parse_snapshot_tables(SNAPSHOT)
        self.assertEqual(len(tables), self.analyzer.EXPECTED_TABLES_PARSED)
        self.assertEqual(len(tables["sns.c:dct16_m"]), 1024)
        self.assertEqual(len(tables["tables.c:lc3_sns_lfcb"]), 1024)
        self.assertEqual(len(tables["tables.c:lc3_spectrum_lookup"]), 4096)
        # Rules are total over the parsed census: every key classifies to a
        # module or to shared without raising.
        for key in tables:
            self.analyzer.table_module(key)

    def test_table_module_rules(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(analyzer.table_module("sns.c:dct16_m"), "sns")
        self.assertEqual(analyzer.table_module("tables.c:lc3_sns_hfcb"), "sns")
        self.assertEqual(analyzer.table_module("tables.c:lc3_tns_order_bits"), "tns")
        self.assertEqual(analyzer.table_module("tables.c:lc3_spectrum_bits"), "spec")
        self.assertEqual(analyzer.table_module("tables.c:mdct_win_10m_48k"), "mdct")
        self.assertEqual(analyzer.table_module("ltpf.c:h_48k_12k8_q15"), "ltpf")
        self.assertIsNone(analyzer.table_module("tables.c:band_lim_10m_8k"))
        self.assertIsNone(analyzer.table_module("tables.c:lc3_num_bands"))

    def test_array_body_grammar(self) -> None:
        analyzer = self.analyzer
        floats = analyzer._parse_array_body("float", "{ 1.0f, -2.5e-01, 0x0 }")
        self.assertIsNone(floats)  # hex token rejected in a float array
        floats = analyzer._parse_array_body("float", "{ 1.0f, -2.5e-01 }")
        self.assertEqual(floats, __import__("struct").pack("<2f", 1.0, -0.25))
        ints = analyzer._parse_array_body("uint16_t", "{ 1, 0x20, 3 }")
        self.assertEqual(ints, __import__("struct").pack("<3H", 1, 0x20, 3))
        # Expressions and identifiers are rejected by construction.
        self.assertIsNone(analyzer._parse_array_body("int", "{ 8915 / 4096 }"))
        self.assertIsNone(analyzer._parse_array_body("int", "{ LC3_NS(2500, 8000) }"))
        self.assertIsNone(analyzer._parse_array_body("int", ""))

    def test_locate_tables_requires_unique_match(self) -> None:
        analyzer = self.analyzer
        needle = bytes(range(32))
        blob = b"\xAA" * 16 + needle + b"\xBB" * 16
        located = analyzer.locate_tables(blob, 0x1000, {"mod:x": needle})
        self.assertEqual(located, {"mod:x": 0x1000 + 16})
        duplicated = analyzer.locate_tables(
            blob + needle, 0x1000, {"mod:x": needle}
        )
        self.assertEqual(duplicated, {})
        missing = analyzer.locate_tables(b"\x00" * 64, 0x1000, {"mod:x": needle})
        self.assertEqual(missing, {})

    def test_extract_table_evidence_follows_pointer_cells(self) -> None:
        analyzer = self.analyzer
        table = bytes(range(64))
        blob = bytearray(512)
        blob[100:164] = table  # table at load_base + 100
        # literal-pool cell at offset 200 holds a pointer into the table
        blob[200:204] = (1000 + 108).to_bytes(4, "little")
        spans = [(1000 + 100, 1000 + 164, "sns.c:t", "sns")]
        functions = {1: {"dat_refs": {1000 + 200, 1000 + 300}}}
        private, shared = analyzer.extract_table_evidence(
            1, functions, spans, bytes(blob), 1000
        )
        self.assertEqual(private, {"sns.c:t"})
        self.assertEqual(shared, set())

    def test_snapshot_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_snapshot_sources(root)
            target = root / "src" / "sns.c"
            data = bytearray(target.read_bytes())
            data[-1] ^= 0xFF
            target.write_bytes(bytes(data))
            with self.assertRaises(analyzer.CensusError):
                analyzer.parse_snapshot_tables(root)

    def test_snapshot_missing_file_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_snapshot_sources(root)
            (root / "src" / "spec.c").unlink()
            with self.assertRaises(analyzer.CensusError):
                analyzer.parse_snapshot_tables(root)


@unittest.skipUnless(
    CORPUS.is_dir() and PLAN.is_file() and REPORT.is_file(),
    "authenticated corpus/current build unavailable",
)
class EncoderInternalsAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_reconciliation_is_pinned(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["frontier_functions"], 62)
        self.assertEqual(reconciliation["frontier_official_bytes"], 17_874)
        self.assertEqual(reconciliation["liblc3_bucket_functions"], 10)
        self.assertEqual(reconciliation["liblc3_bucket_official_bytes"], 1_694)
        self.assertEqual(reconciliation["scope_functions"], 72)
        self.assertEqual(reconciliation["attributed_functions"], 41)
        self.assertEqual(reconciliation["attributed_official_bytes"], 16_128)
        self.assertEqual(reconciliation["investigation_functions"], 31)
        self.assertEqual(reconciliation["investigation_official_bytes"], 3_440)
        self.assertEqual(reconciliation["external_observations"], 8)
        self.assertEqual(reconciliation["snapshot_tables_parsed"], 88)
        self.assertEqual(reconciliation["snapshot_tables_located"], 84)

    def test_module_summary_is_pinned(self) -> None:
        actual = {
            row["module"]: (row["functions"], row["official_opaque_bytes"])
            for row in self.report["module_summary"]
        }
        self.assertEqual(actual, self.analyzer.EXPECTED_MODULE_SUMMARY)

    def test_rows_match_pinned_attribution(self) -> None:
        by_entry = {row["entry"]: row for row in self.report["functions"]}
        self.assertEqual(len(by_entry), 72)
        for entry, (status, module, evidence, confidence) in (
            self.analyzer.EXPECTED_ATTRIBUTION.items()
        ):
            row = by_entry[entry]
            self.assertEqual(
                (row["status"], row["module"] or None, row["evidence"], row["confidence"]),
                (status, module, evidence, confidence),
                f"0x{entry:08X}",
            )
        investigation = [
            row for row in self.report["functions"] if row["status"] == "investigation-required"
        ]
        self.assertEqual(len(investigation), 31)
        for row in investigation:
            self.assertEqual(row["module"], "")
            self.assertEqual(row["attribution"], "")
            self.assertEqual(row["evidence"], "none")
            self.assertTrue(row["detail"])

    def test_spot_attributions(self) -> None:
        by_entry = {row["entry"]: row for row in self.report["functions"]}
        self.assertEqual(by_entry[0x0059138A]["attribution"], "lc3_encode")
        self.assertEqual(by_entry[0x00590F84]["attribution"], "load_s16")
        self.assertEqual(by_entry[0x005911B0]["attribution"], "load_float")
        self.assertEqual(
            by_entry[0x00599714]["evidence"], "upstream-table-match"
        )
        self.assertIn("tables.c:lc3_sns_hfcb", by_entry[0x00599714]["detail"])
        self.assertEqual(by_entry[0x00598284]["attribution"], "lc3_attdet_run")
        self.assertEqual(by_entry[0x0059B6A0]["status"], "cluster")
        self.assertEqual(by_entry[0x00590F68]["attribution"], "lc3_hr_frame_bytes")

    def test_external_observations_are_pinned(self) -> None:
        observations = {
            row["entry"]: row for row in self.report["external_observations"]
        }
        self.assertEqual(len(observations), 8)
        tns = observations[0x0059AA84]
        self.assertEqual(tns["module"], "tns")
        self.assertEqual(tns["attribution"], "lc3_tns_analyze")
        self.assertEqual(tns["parent_bucket"], "first-party")
        setup = observations[0x0059123A]
        self.assertEqual(setup["attribution"], "lc3_hr_setup_encoder")
        self.assertEqual(setup["evidence"], "documented-internal-tail")
        self.assertEqual(observations[0x00438FB8]["module"], "ltpf")
        self.assertIsNone(observations[0x00439710]["module"])

    def test_checked_in_manifests_match_regeneration(self) -> None:
        self.assertEqual(
            self.analyzer.map_tsv(self.report).encode(),
            (MANIFESTS / "g2-liblc3-encoder-internals-map.tsv").read_bytes(),
        )
        self.assertEqual(
            self.analyzer.summary_json(self.report).encode(),
            (MANIFESTS / "g2-liblc3-encoder-internals-summary.json").read_bytes(),
        )

    def test_dispatch_order_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_DISPATCH
        mutated = (original[1], original[0]) + original[2:]
        analyzer.EXPECTED_DISPATCH = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_DISPATCH = original

    def test_attribution_pin_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = dict(analyzer.EXPECTED_ATTRIBUTION)
        analyzer.EXPECTED_ATTRIBUTION[0x00598284] = (
            "module",
            "mdct",
            "dispatch-graph-direct",
            "medium",
        )
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_ATTRIBUTION.clear()
            analyzer.EXPECTED_ATTRIBUTION.update(original)

    def test_table_evidence_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = dict(analyzer.EXPECTED_TABLE_EVIDENCE)
        del analyzer.EXPECTED_TABLE_EVIDENCE[0x00599290]
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_TABLE_EVIDENCE.clear()
            analyzer.EXPECTED_TABLE_EVIDENCE.update(original)


if __name__ == "__main__":
    unittest.main()
