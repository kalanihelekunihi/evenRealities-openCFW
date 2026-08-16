#!/usr/bin/env python3
"""Guard the G2 Cordio link-layer-island census of the 0x5Dxxxx sea."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_cordio_ll_sea_census.py"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)
PARENT_TSV = ROOT / "tools/manifests/g2-apollo-unanchored-census-functions.tsv"
LVGL_TSV = ROOT / "tools/manifests/g2-lvgl-vendor-fork-census.tsv"
MANIFESTS_DIR = ROOT / "tools/manifests"
MANIFEST_TSV = MANIFESTS_DIR / "g2-cordio-ll-sea-census.tsv"
MANIFEST_JSON = MANIFESTS_DIR / "g2-cordio-ll-sea-census-summary.json"
HCI_DEFS = ROOT / "third_party/cordio/wsf/include/hci_defs.h"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_cordio_ll_sea_census", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SeaCensusUnitTests(unittest.TestCase):
    """Corpus-independent checks of the census rule tables and parsers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_evidence_and_confidence_tables_are_closed(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(
            set(analyzer.EVIDENCE_CLASSES), set(analyzer.CONFIDENCE_BY_EVIDENCE)
        )
        self.assertEqual(len(analyzer.EVIDENCE_CLASSES), 7)
        for confidence in analyzer.CONFIDENCE_BY_EVIDENCE.values():
            self.assertIn(confidence, ("medium", "low", "none"))
        self.assertEqual(
            analyzer.CONFIDENCE_BY_EVIDENCE["cordio-anchor-callee"], "medium"
        )
        self.assertEqual(
            analyzer.CONFIDENCE_BY_EVIDENCE["cordio-medium-callee"], "medium"
        )
        self.assertEqual(analyzer.CONFIDENCE_BY_EVIDENCE["none"], "none")

    def test_seed_sets_are_disjoint_and_in_the_sea_window(self) -> None:
        analyzer = self.analyzer
        anchor = set(analyzer.EXPECTED_ANCHOR_CALLEES)
        medium = set(analyzer.EXPECTED_MEDIUM_CALLEES)
        callers = set(analyzer.EXPECTED_ISLAND_CALLERS)
        self.assertFalse(anchor & medium)
        self.assertFalse(anchor & callers)
        self.assertFalse(medium & callers)
        for entry in anchor | medium | callers:
            self.assertGreaterEqual(entry, analyzer.SEA_BASE)
            self.assertLess(entry, analyzer.SEA_END)
        self.assertEqual(len(anchor), 8)
        self.assertEqual(len(medium), 4)
        self.assertEqual(len(callers), 1)
        # The seeds themselves are not sea members: the anchor is
        # path-anchored and the medium seed is parent-bucketed cordio.
        self.assertNotIn(analyzer.ANCHOR_ENTRY, anchor | medium | callers)
        self.assertNotIn(analyzer.MEDIUM_ENTRY, anchor | medium | callers)

    def test_frozen_census_is_internally_consistent(self) -> None:
        analyzer = self.analyzer
        evidence = analyzer.EXPECTED_EVIDENCE_CENSUS
        self.assertEqual(sum(c["functions"] for c in evidence.values()), 300)
        self.assertEqual(
            sum(c["official_opaque_bytes"] for c in evidence.values()),
            analyzer.EXPECTED_SEA_OFFICIAL_BYTES,
        )
        attributed = sum(
            c["functions"] for name, c in evidence.items() if name != "none"
        )
        self.assertEqual(attributed, analyzer.EXPECTED_CLOSURE_FUNCTIONS)
        self.assertEqual(
            sum(analyzer.EXPECTED_HOP_CENSUS.values()),
            analyzer.EXPECTED_CLOSURE_FUNCTIONS,
        )
        self.assertEqual(analyzer.EXPECTED_HOP_CENSUS[1], 8 + 4 + 1)
        self.assertEqual(
            evidence["none"]["functions"], analyzer.EXPECTED_INVESTIGATION_FUNCTIONS
        )
        self.assertEqual(
            evidence["none"]["official_opaque_bytes"],
            analyzer.EXPECTED_INVESTIGATION_OFFICIAL_BYTES,
        )
        self.assertEqual(
            analyzer.EXPECTED_INVESTIGATION_FUNCTIONS
            + analyzer.EXPECTED_CLOSURE_FUNCTIONS,
            analyzer.EXPECTED_SEA_FUNCTIONS,
        )
        # Hop-labelled classes carry the matching hop digit.
        for name in evidence:
            if name.startswith("cordio-closure-hop-"):
                hop = int(name.rsplit("-", 1)[1])
                self.assertEqual(
                    evidence[name]["functions"], analyzer.EXPECTED_HOP_CENSUS[hop]
                )

    def test_hci_opcode_parser_reads_vendored_header(self) -> None:
        opcodes = self.analyzer.parse_hci_opcodes(HCI_DEFS)
        self.assertEqual(len(opcodes), 140)
        # HCI_OPCODE_DISCONNECT = (OGF_LINK_CONTROL << 10) | OCF_DISCONNECT.
        self.assertIn(0x0406, opcodes)
        # HCI_OPCODE_LE_SET_SCAN_ENABLE = (OGF_LE << 10) | 0x000C; the sea's
        # documented false positives alias this value as a data offset.
        self.assertIn(0x200C, opcodes)

    def test_hci_opcode_parser_fails_closed_on_header_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / HCI_DEFS.name
            text = HCI_DEFS.read_text(encoding="utf-8")
            dropped = text.replace(
                "#define HCI_OCF_DISCONNECT", "#define HCI_OCF_DISCONNECT_GONE", 1
            )
            self.assertNotEqual(dropped, text)
            target.write_text(dropped, encoding="utf-8")
            with self.assertRaises(self.analyzer.SeaCensusError):
                self.analyzer.parse_hci_opcodes(target)

    def test_hci_opcode_parser_fails_closed_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(self.analyzer.SeaCensusError):
                self.analyzer.parse_hci_opcodes(Path(directory) / "absent.h")

    def test_parent_census_loader_reads_checked_in_manifest(self) -> None:
        rows = self.analyzer.load_parent_census(PARENT_TSV)
        self.assertEqual(len(rows), 5_610)
        sea = [
            row
            for row in rows.values()
            if row["bucket"] == "investigation-required-no-evidence"
            and 0x5D0000 <= int(row["entry"], 16) < 0x5E0000
        ]
        self.assertEqual(len(sea), 300)
        self.assertEqual(
            sum(int(row["official_opaque_bytes"]) for row in sea), 52_866
        )

    def test_parent_census_loader_fails_closed_on_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            lines = PARENT_TSV.read_text(encoding="utf-8").splitlines()
            target.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
            with self.assertRaises(self.analyzer.SeaCensusError):
                self.analyzer.load_parent_census(target)

    def test_parent_census_loader_fails_closed_on_duplicate_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            lines = PARENT_TSV.read_text(encoding="utf-8").splitlines()
            data_row = next(
                line
                for line in lines
                if line and not line.startswith("#") and not line.startswith("entry\t")
            )
            target.write_text("\n".join(lines + [data_row]) + "\n", encoding="utf-8")
            with self.assertRaises(self.analyzer.SeaCensusError):
                self.analyzer.load_parent_census(target)

    def test_parent_census_loader_fails_closed_on_schema_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            text = PARENT_TSV.read_text(encoding="utf-8").replace(
                "official_opaque_bytes", "opaque_bytes", 1
            )
            target.write_text(text, encoding="utf-8")
            with self.assertRaises(self.analyzer.SeaCensusError):
                self.analyzer.load_parent_census(target)

    def test_parent_census_loader_fails_closed_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(self.analyzer.SeaCensusError):
                self.analyzer.load_parent_census(Path(directory) / "absent.tsv")

    def test_lvgl_census_loader_reads_checked_in_manifest(self) -> None:
        rows = self.analyzer.load_lvgl_census(LVGL_TSV)
        self.assertEqual(len(rows), 1_484)
        sea = [row for row in rows.values() if row["scope"] == "sea-0x5d"]
        self.assertEqual(len(sea), 300)
        cordio_callers = [
            row for row in sea if "external callers: cordio" in (row["detail"] or "")
        ]
        self.assertEqual(len(cordio_callers), 12)

    def test_lvgl_census_loader_fails_closed_on_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / LVGL_TSV.name
            lines = LVGL_TSV.read_text(encoding="utf-8").splitlines()
            target.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
            with self.assertRaises(self.analyzer.SeaCensusError):
                self.analyzer.load_lvgl_census(target)


@unittest.skipUnless(CORPUS.is_dir(), "authenticated Ghidra corpus unavailable")
class SeaCensusAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_sea_reconciles_with_parent_census(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["sea_functions"], 300)
        self.assertEqual(reconciliation["sea_official_bytes"], 52_866)
        self.assertEqual(reconciliation["sea_largest_entry"], "0x005D4ED0")
        self.assertEqual(reconciliation["sea_largest_envelope_bytes"], 7_880)
        self.assertEqual(reconciliation["attributed_functions"], 102)
        self.assertEqual(reconciliation["attributed_official_bytes"], 19_222)
        self.assertEqual(reconciliation["investigation_functions"], 198)
        self.assertEqual(reconciliation["investigation_official_bytes"], 33_644)

    def test_seed_block_is_pinned(self) -> None:
        self.assertEqual(
            self.report["seeds"],
            {
                "anchor_entry": "0x005D2BAE",
                "anchor_path": "third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c",
                "anchor_evidence": "string",
                "medium_entry": "0x005D2E0C",
                "medium_parent_evidence": "call-topology-single-family",
            },
        )

    def test_evidence_census_is_pinned(self) -> None:
        self.assertEqual(
            self.report["reconciliation"]["evidence_classes"],
            self.analyzer.EXPECTED_EVIDENCE_CENSUS,
        )

    def test_hop_census_is_pinned(self) -> None:
        self.assertEqual(
            self.report["reconciliation"]["hop_census"],
            {str(k): v for k, v in self.analyzer.EXPECTED_HOP_CENSUS.items()},
        )

    def test_evidence_confidence_and_hop_are_closed(self) -> None:
        analyzer = self.analyzer
        for record in self.report["functions"]:
            self.assertIn(record["evidence"], analyzer.EVIDENCE_CLASSES)
            self.assertEqual(
                record["confidence"],
                analyzer.CONFIDENCE_BY_EVIDENCE[record["evidence"]],
            )
            if record["evidence"] == "none":
                self.assertEqual(record["bucket"], "investigation-required")
                self.assertIsNone(record["hop"])
                self.assertTrue(record["detail"])
            else:
                self.assertEqual(record["bucket"], "cordio-ll-island")
                self.assertIsInstance(record["hop"], int)
                if record["evidence"].startswith("cordio-closure-hop-"):
                    self.assertEqual(
                        record["hop"], int(record["evidence"].rsplit("-", 1)[1])
                    )
                else:
                    self.assertEqual(record["hop"], 1)

    def test_documented_crosscheck_pins(self) -> None:
        reconciliation = self.report["reconciliation"]
        # Sea-level external topology.
        self.assertEqual(
            reconciliation["sea_external_callers"],
            [f"0x{c:08X}" for c in self.analyzer.EXPECTED_SEA_EXTERNAL_CALLERS],
        )
        self.assertEqual(
            reconciliation["sea_first_party_callees"],
            [f"0x{t:08X}" for t in self.analyzer.EXPECTED_SEA_FIRST_PARTY_CALLEES],
        )
        # HCI opcode negative result and the documented alias rows.
        self.assertEqual(reconciliation["hci_opcodes_parsed"], 140)
        self.assertEqual(reconciliation["hci_opcode_comparison_hits"], 0)
        self.assertEqual(
            reconciliation["opcode_alias_rows"],
            ["0x005DD584", "0x005DD780", "0x005DD832"],
        )
        # Caller-side closure neighbours.
        self.assertEqual(
            reconciliation["component_adjacent"],
            [f"0x{e:08X}" for e in self.analyzer.EXPECTED_COMPONENT_ADJACENT],
        )

    def test_island_members_are_exactly_the_seed_closure(self) -> None:
        analyzer = self.analyzer
        island = {
            record["entry"]: record
            for record in self.report["functions"]
            if record["bucket"] == "cordio-ll-island"
        }
        self.assertEqual(len(island), 102)
        for entry in analyzer.EXPECTED_ANCHOR_CALLEES:
            self.assertEqual(island[entry]["evidence"], "cordio-anchor-callee")
            self.assertEqual(island[entry]["confidence"], "medium")
        for entry in analyzer.EXPECTED_MEDIUM_CALLEES:
            self.assertEqual(island[entry]["evidence"], "cordio-medium-callee")
            self.assertEqual(island[entry]["confidence"], "medium")
        for entry in analyzer.EXPECTED_ISLAND_CALLERS:
            self.assertEqual(island[entry]["evidence"], "cordio-island-caller")
            self.assertEqual(island[entry]["confidence"], "low")
        # The sea's largest member is the medium seed's callee.
        self.assertEqual(island[0x005D4ED0]["evidence"], "cordio-medium-callee")
        self.assertEqual(island[0x005D4ED0]["envelope_bytes"], 7_880)

    def test_checked_in_manifests_match_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / MANIFEST_TSV.name).write_text(
                self.analyzer.census_tsv(self.report), encoding="utf-8"
            )
            (root / MANIFEST_JSON.name).write_text(
                self.analyzer.summary_json(self.report), encoding="utf-8"
            )
            for name in (MANIFEST_TSV.name, MANIFEST_JSON.name):
                self.assertEqual(
                    (root / name).read_bytes(),
                    (MANIFESTS_DIR / name).read_bytes(),
                    f"checked-in manifest drifted: {name}",
                )

    def test_frozen_constant_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_EVIDENCE_CENSUS
        mutated = {name: dict(stats) for name, stats in original.items()}
        mutated["none"] = {
            "functions": original["none"]["functions"] + 1,
            "official_opaque_bytes": original["none"]["official_opaque_bytes"],
        }
        analyzer.EXPECTED_EVIDENCE_CENSUS = mutated
        try:
            with self.assertRaises(analyzer.SeaCensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_EVIDENCE_CENSUS = original

    def test_parent_census_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            shutil.copy(PARENT_TSV, target)
            # Mutate a sea row: 0x005D008E is the first sea member.
            text = target.read_text(encoding="utf-8").replace(
                "0x005D008E\t0x005D008E\t0x005D018A\t252\t252\t"
                "investigation-required-no-evidence\tnone\tnone\t",
                "0x005D008E\t0x005D008E\t0x005D018A\t252\t252\t"
                "first-party\tcall-topology-single-family\tmedium\t",
                1,
            )
            target.write_text(text, encoding="utf-8")
            with self.assertRaises(analyzer.SeaCensusError):
                analyzer.analyze(CORPUS, parent_census=target)

    def test_lvgl_census_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / LVGL_TSV.name
            shutil.copy(LVGL_TSV, target)
            text = target.read_text(encoding="utf-8").replace(
                "external callers: cordio", "external callers: lvgl", 1
            )
            target.write_text(text, encoding="utf-8")
            with self.assertRaises(analyzer.SeaCensusError):
                analyzer.analyze(CORPUS, lvgl_census=target)


if __name__ == "__main__":
    unittest.main()
