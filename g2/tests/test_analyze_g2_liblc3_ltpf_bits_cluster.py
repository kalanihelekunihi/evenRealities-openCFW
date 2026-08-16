#!/usr/bin/env python3
"""Guard the liblc3 ltpf/bits 0x43xxxx cluster census."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_liblc3_ltpf_bits_cluster.py"
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
        "analyze_g2_liblc3_ltpf_bits_cluster", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def copy_snapshot_sources(target: Path) -> None:
    (target / "src").mkdir(parents=True)
    shutil.copy(SNAPSHOT / "SNAPSHOT.sha256", target)
    sibling = load_analyzer()._load_sibling()
    for name in sibling.TABLE_SOURCES:
        shutil.copy(SNAPSHOT / "src" / name, target / "src" / name)


class LtpfBitsClusterUnitTests(unittest.TestCase):
    """Corpus-independent checks of the rule tables and reconciliation."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_closed_class_sets(self) -> None:
        analyzer = self.analyzer
        for entry, (status, module, evidence, confidence) in (
            analyzer.EXPECTED_ATTRIBUTION.items()
        ):
            self.assertIn(status, analyzer.STATUSES)
            if module is not None:
                self.assertIn(module, analyzer.MODULES)
                self.assertEqual(status, "module")
            else:
                self.assertNotEqual(status, "module")
            self.assertIn(evidence, analyzer.EVIDENCE_CLASSES)
            self.assertIn(confidence, analyzer.CONFIDENCE_ORDER)
            if status == "module":
                self.assertNotEqual(confidence, "none")
            if status == "investigation-required":
                self.assertEqual((module, evidence, confidence), (None, "none", "none"))

    def test_expectation_tables_are_total_and_consistent(self) -> None:
        analyzer = self.analyzer
        pinned = analyzer.EXPECTED_ATTRIBUTION
        # Every seed is pinned with the same module and a caller set.
        for entry, module, _name, _detail in analyzer.EXPECTED_SEEDS:
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][1], module)
            self.assertIn(entry, analyzer.EXPECTED_SEED_CALLERS)
            self.assertTrue(analyzer.EXPECTED_SEED_CALLERS[entry])
        # Seed entries are unique.
        seeds = [entry for entry, _m, _n, _d in analyzer.EXPECTED_SEEDS]
        self.assertEqual(len(seeds), len(set(seeds)))
        # Every resample-table target is pinned at high confidence, and the
        # two non-corpus entries are pinned as table targets.
        targets = [entry for entry, _slot, _name in analyzer.EXPECTED_RESAMPLE_TABLE]
        self.assertEqual(len(targets), 7)
        for entry in set(targets):
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][1], "ltpf")
            self.assertEqual(pinned[entry][2], "dispatch-table-entry")
            self.assertEqual(pinned[entry][3], "high")
        for entry in analyzer.EXPECTED_RESAMPLE_NON_CORPUS:
            self.assertIn(entry, targets)
        # Slots follow the v1.1.3 LC3_SRATE enum order; the 48K body serves
        # both 48K slots.
        slots = [slot for _entry, slot, _name in analyzer.EXPECTED_RESAMPLE_TABLE]
        self.assertEqual(
            slots,
            [
                "LC3_SRATE_8K",
                "LC3_SRATE_16K",
                "LC3_SRATE_24K",
                "LC3_SRATE_32K",
                "LC3_SRATE_48K",
                "LC3_SRATE_48K_HR",
                "LC3_SRATE_96K_HR",
            ],
        )
        # Every table-evidence entry is pinned with the same module.
        for entry, (module, keys, _label) in analyzer.EXPECTED_TABLE_EVIDENCE.items():
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][1], module)
            self.assertEqual(pinned[entry][3], "high")
            for key in keys:
                self.assertTrue(key.startswith("ltpf.c:"))
        # Every indirect entry is pinned with the same module and callers.
        for entry, module, callers, _text in analyzer.EXPECTED_INDIRECT:
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][1], module)
            self.assertTrue(callers)
        # Shared-runtime helpers are pinned without a module.
        for entry, callers, _text in analyzer.EXPECTED_SHARED_RUNTIME:
            self.assertIn(entry, pinned)
            self.assertEqual(pinned[entry][0], "shared-runtime")
            self.assertIsNone(pinned[entry][1])
            self.assertTrue(callers)
        # The investigation row is pinned and closed.
        for entry in analyzer.EXPECTED_INVESTIGATION:
            self.assertEqual(
                pinned[entry], ("investigation-required", None, "none", "none")
            )

    def test_scope_partition_is_disjoint_and_total(self) -> None:
        analyzer = self.analyzer
        closure = set(analyzer.EXPECTED_CLOSURE)
        extension = set(analyzer.EXPECTED_CLOSURE_EXTENSION)
        table = {e for e, _s, _n in analyzer.EXPECTED_RESAMPLE_TABLE}
        callee = set(analyzer.EXPECTED_TABLE_CALLEE)
        self.assertFalse(closure & extension)
        self.assertFalse(closure & table)
        self.assertFalse(closure & callee)
        self.assertFalse(extension & table)
        self.assertFalse(extension & callee)
        self.assertFalse(table & callee)
        scope = closure | extension | table | callee
        self.assertEqual(len(scope), analyzer.EXPECTED_SCOPE_ROWS)
        self.assertEqual(set(analyzer.EXPECTED_ATTRIBUTION), scope)
        corpus = scope - set(analyzer.EXPECTED_RESAMPLE_NON_CORPUS)
        self.assertEqual(len(corpus), analyzer.EXPECTED_SCOPE_CORPUS_ROWS)

    def test_reconciliation_constants_are_arithmetically_closed(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(len(analyzer.EXPECTED_ATTRIBUTION), 26)
        self.assertEqual(
            analyzer.EXPECTED_ATTRIBUTED_ROWS
            + analyzer.EXPECTED_SHARED_RUNTIME_ROWS
            + analyzer.EXPECTED_INVESTIGATION_ROWS,
            analyzer.EXPECTED_SCOPE_ROWS,
        )
        self.assertEqual(
            analyzer.EXPECTED_ATTRIBUTED_OFFICIAL_BYTES
            + analyzer.EXPECTED_SHARED_RUNTIME_OFFICIAL_BYTES
            + analyzer.EXPECTED_INVESTIGATION_OFFICIAL_BYTES,
            5_118,
        )
        module_rows = sum(r for r, _c, _b in analyzer.EXPECTED_MODULE_SUMMARY.values())
        module_bytes = sum(b for _r, _c, b in analyzer.EXPECTED_MODULE_SUMMARY.values())
        self.assertEqual(module_rows, analyzer.EXPECTED_ATTRIBUTED_ROWS)
        self.assertEqual(module_bytes, analyzer.EXPECTED_ATTRIBUTED_OFFICIAL_BYTES)
        # Island composition is closed.
        self.assertEqual(
            analyzer.EXPECTED_ISLAND_PARENT_ROWS
            + analyzer.EXPECTED_ISLAND_PATH_ANCHORED,
            analyzer.EXPECTED_ISLAND_FUNCTIONS,
        )
        self.assertEqual(
            sum(analyzer.EXPECTED_ISLAND_PARENT_BUCKETS.values()),
            analyzer.EXPECTED_ISLAND_PARENT_ROWS,
        )
        self.assertEqual(
            analyzer.EXPECTED_ISLAND_PARENT_BUCKETS[
                "investigation-required-no-evidence"
            ]
            - analyzer.EXPECTED_SCOPE_CORPUS_ROWS,
            analyzer.EXPECTED_ISLAND_FRONTIER_REMAINDER,
        )

    def test_snapshot_table_parser_census(self) -> None:
        analyzer = self.analyzer
        tables = analyzer.parse_tables(SNAPSHOT)
        self.assertEqual(len(tables, ), analyzer.EXPECTED_TABLES_PARSED)
        # The ltpf resample/interpolation needles used by this census.
        self.assertEqual(len(tables["ltpf.c:h4_q15"]), 32)
        self.assertEqual(len(tables["ltpf.c:h_8k_12k8_q15"]), 160)
        self.assertEqual(len(tables["ltpf.c:h_32k_12k8_q15"]), 160)
        self.assertEqual(len(tables["ltpf.c:h_24k_12k8_q15"]), 480)
        self.assertEqual(len(tables["ltpf.c:h_96k_12k8_q15"]), 480)
        # The pinned evidence keys all parse as ltpf-private tables.
        sibling = analyzer._load_sibling()
        for _entry, (_module, keys, _label) in analyzer.EXPECTED_TABLE_EVIDENCE.items():
            for key in keys:
                self.assertIn(key, tables)
                self.assertEqual(sibling.table_module(key), "ltpf")

    def test_snapshot_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_snapshot_sources(root)
            target = root / "src" / "ltpf.c"
            data = bytearray(target.read_bytes())
            data[-1] ^= 0xFF
            target.write_bytes(bytes(data))
            with self.assertRaises(analyzer.CensusError):
                analyzer.parse_tables(root)

    def test_snapshot_missing_file_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            copy_snapshot_sources(root)
            (root / "src" / "bits.c").unlink()
            with self.assertRaises(analyzer.CensusError):
                analyzer.parse_tables(root)


@unittest.skipUnless(
    CORPUS.is_dir() and PLAN.is_file() and REPORT.is_file(),
    "authenticated corpus/current build unavailable",
)
class LtpfBitsClusterAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_reconciliation_is_pinned(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["island_functions"], 197)
        self.assertEqual(reconciliation["island_parent_rows"], 159)
        self.assertEqual(reconciliation["island_path_anchored"], 38)
        self.assertEqual(reconciliation["scope_rows"], 26)
        self.assertEqual(reconciliation["scope_corpus_rows"], 24)
        self.assertEqual(reconciliation["attributed_rows"], 22)
        self.assertEqual(reconciliation["attributed_official_bytes"], 5_108)
        self.assertEqual(reconciliation["shared_runtime_rows"], 3)
        self.assertEqual(reconciliation["shared_runtime_official_bytes"], 0)
        self.assertEqual(reconciliation["investigation_rows"], 1)
        self.assertEqual(reconciliation["investigation_official_bytes"], 10)
        self.assertEqual(reconciliation["island_frontier_remainder"], 44)
        self.assertEqual(reconciliation["snapshot_tables_parsed"], 88)
        self.assertEqual(reconciliation["snapshot_tables_located"], 84)
        self.assertEqual(reconciliation["resample_table_address"], "0x00439680")
        self.assertEqual(
            reconciliation["resample_table_non_corpus"],
            ["0x00438400", "0x00438604"],
        )

    def test_module_summary_is_pinned(self) -> None:
        actual = {
            row["module"]: (
                row["rows"],
                row["corpus_functions"],
                row["official_opaque_bytes"],
            )
            for row in self.report["module_summary"]
        }
        self.assertEqual(actual, self.analyzer.EXPECTED_MODULE_SUMMARY)

    def test_island_composition_is_pinned(self) -> None:
        composition = self.report["island_composition"]
        self.assertEqual(composition["cluster_scope_corpus"], 24)
        self.assertEqual(composition["path_anchored"], 38)
        self.assertEqual(
            composition["parent_buckets"],
            {
                "lvgl": 79,
                "investigation-required-no-evidence": 68,
                "easylogger": 7,
                "first-party": 5,
            },
        )

    def test_rows_match_pinned_attribution(self) -> None:
        by_entry = {row["entry"]: row for row in self.report["functions"]}
        self.assertEqual(len(by_entry), 26)
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
            row
            for row in self.report["functions"]
            if row["status"] == "investigation-required"
        ]
        self.assertEqual(len(investigation), 1)
        for row in investigation:
            self.assertEqual(row["module"], "")
            self.assertEqual(row["attribution"], "")
            self.assertEqual(row["evidence"], "none")
            self.assertTrue(row["detail"])

    def test_spot_attributions(self) -> None:
        by_entry = {row["entry"]: row for row in self.report["functions"]}
        self.assertEqual(by_entry[0x00438FB8]["attribution"], "lc3_ltpf_analyse")
        self.assertEqual(by_entry[0x004396C2]["attribution"], "lc3_ltpf_put_data")
        self.assertEqual(by_entry[0x00439868]["attribution"], "lc3_setup_bits")
        self.assertEqual(by_entry[0x004399E4]["attribution"], "lc3_flush_bits")
        self.assertEqual(
            by_entry[0x00439B12]["attribution"], "lc3_put_bits_generic"
        )
        self.assertEqual(by_entry[0x00439710]["attribution"], "IAR memmove")
        self.assertEqual(by_entry[0x00439710]["status"], "shared-runtime")
        self.assertEqual(by_entry[0x00438504]["attribution"], "resample_32k_12k8")
        self.assertEqual(by_entry[0x00438504]["evidence"], "dispatch-table-entry")
        self.assertIn("ltpf.c:h_32k_12k8_q15", by_entry[0x00438504]["detail"])
        self.assertEqual(by_entry[0x00438924]["evidence"], "upstream-table-match")
        self.assertIn("ltpf.c:h4_q15", by_entry[0x00438924]["detail"])
        self.assertEqual(by_entry[0x00438400]["parent_bucket"], "not-in-ghidra-corpus")
        self.assertEqual(by_entry[0x00438400]["official_opaque_bytes"], 0)
        self.assertTrue(
            by_entry[0x00439B54]["attribution"].startswith("lc3_ac_write_renorm")
        )
        self.assertEqual(by_entry[0x004396B8]["status"], "investigation-required")

    def test_checked_in_manifests_match_regeneration(self) -> None:
        self.assertEqual(
            self.analyzer.map_tsv(self.report).encode(),
            (MANIFESTS / "g2-liblc3-ltpf-bits-cluster-map.tsv").read_bytes(),
        )
        self.assertEqual(
            self.analyzer.summary_json(self.report).encode(),
            (MANIFESTS / "g2-liblc3-ltpf-bits-cluster-summary.json").read_bytes(),
        )

    def test_seed_order_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_SEEDS
        mutated = (original[2], original[1], original[0]) + original[3:]
        analyzer.EXPECTED_SEEDS = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_SEEDS = original

    def test_attribution_pin_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = dict(analyzer.EXPECTED_ATTRIBUTION)
        analyzer.EXPECTED_ATTRIBUTION[0x00439868] = (
            "module",
            "ltpf",
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
        del analyzer.EXPECTED_TABLE_EVIDENCE[0x00438504]
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_TABLE_EVIDENCE.clear()
            analyzer.EXPECTED_TABLE_EVIDENCE.update(original)

    def test_caller_set_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_INDIRECT
        mutated = tuple(
            (entry, module, (0x00438FB8,), text) if entry == 0x00438BF0 else row
            for row in original
            for entry, module, _callers, text in [row]
        )
        analyzer.EXPECTED_INDIRECT = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_INDIRECT = original


if __name__ == "__main__":
    unittest.main()
