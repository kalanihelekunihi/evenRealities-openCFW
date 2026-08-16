#!/usr/bin/env python3
"""Guard the FreeType engine census of the 0x51/0x52xxxx frontier."""

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
PLAN = ROOT / "build/source/flash-plan.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFESTS = ROOT / "tools/manifests"
SNAPSHOT = ROOT / "third_party/freetype"

EXPECTED_TIER_COUNTS = {
    # evidence: (functions, official_opaque_bytes)
    "documented-api-anchor": (7, 1_518),
    "documented-interior-pin": (1, 288),
    "ps-property-string-signature": (2, 346),
    "base-call-graph-direct": (17, 1_294),
    "base-call-graph-indirect": (56, 4_428),
    "none": (261, 68_088),
}


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_freetype_engine_census", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def synthetic_functions() -> dict[int, dict]:
    """Small closed call-graph world for closure-rule unit tests."""

    def row(calls):
        return {
            "calls": set(calls),
            "dat_refs": set(),
            "tokens": set(),
            "body_start": 0,
            "body_end_exclusive": 0,
        }

    return {
        0x1000: row([0x2000]),  # seed anchor
        0x2000: row([0x3000, 0x9000]),  # direct callee; 0x9000 allowlisted
        0x3000: row([0x4000]),  # pure community internal
        0x4000: row([]),  # leaf called by community
        0x5000: row([0x4000]),  # caller of a community leaf -> joins indirect
        0x6000: row([0x7000]),  # blocked: 0x7000 calls a stranger
        0x7000: row([0xAAAA]),
        0x8000: row([0xBBBB]),  # neutral passthrough target (runtime-only)
        0x8100: row([0x8000, 0x2000]),  # joins through the neutral 0x8000
        0xBBBB: row([]),
    }


class FreeTypeCensusUnitTests(unittest.TestCase):
    """Corpus-independent checks of the census rule tables and algorithms."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_evidence_classes_are_closed_and_cover_attribution(self) -> None:
        analyzer = self.analyzer
        for entry, (status, module, evidence, confidence) in (
            analyzer.EXPECTED_ATTRIBUTION.items()
        ):
            self.assertIn(status, analyzer.STATUSES)
            self.assertIn(module, analyzer.MODULES)
            self.assertIn(evidence, analyzer.EVIDENCE_CLASSES)
            self.assertIn(confidence, analyzer.CONFIDENCE_ORDER)
        covered = {row[2] for row in analyzer.EXPECTED_ATTRIBUTION.values()}
        self.assertEqual(
            covered, set(analyzer.EVIDENCE_CLASSES) - {"none"}
        )

    def test_attribution_census_is_pinned(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(
            len(analyzer.EXPECTED_ATTRIBUTION),
            analyzer.EXPECTED_ATTRIBUTED_FUNCTIONS,
        )
        by_evidence = {}
        for _status, _module, evidence, _confidence in (
            analyzer.EXPECTED_ATTRIBUTION.values()
        ):
            by_evidence[evidence] = by_evidence.get(evidence, 0) + 1
        self.assertEqual(by_evidence["documented-api-anchor"], 7)
        self.assertEqual(by_evidence["documented-interior-pin"], 1)
        self.assertEqual(by_evidence["ps-property-string-signature"], 2)
        self.assertEqual(by_evidence["base-call-graph-direct"], 17)
        self.assertEqual(by_evidence["base-call-graph-indirect"], 56)

    def test_documented_anchors_are_well_formed(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(len(analyzer.DOCUMENTED_ANCHORS), 7)
        for entry, anchor in analyzer.DOCUMENTED_ANCHORS.items():
            self.assertGreaterEqual(entry, analyzer.FRONTIER_BASE)
            self.assertLess(entry, analyzer.FRONTIER_END)
            self.assertTrue(anchor["name"])
            self.assertTrue(anchor["source"].startswith("docs/research/"))
            checks = (
                "body" in anchor,
                "contains" in anchor,
                "calls" in anchor,
                "called_by" in anchor,
                "refs_word" in anchor,
            )
            self.assertTrue(any(checks), anchor["name"])
        # The byte-exact FT_Done_Face envelope is pinned by span.
        self.assertEqual(
            analyzer.DOCUMENTED_ANCHORS[0x00526814]["body"],
            (0x00526814, 0x0052687E),
        )

    def test_ps_property_sets_pin_the_2_9_1_asymmetry(self) -> None:
        analyzer = self.analyzer
        set_names = set(analyzer.EXPECTED_PS_PROPERTY_SET_NAMES)
        get_names = set(analyzer.EXPECTED_PS_PROPERTY_GET_NAMES)
        self.assertEqual(len(analyzer.EXPECTED_PS_PROPERTY_SET_NAMES), 4)
        self.assertEqual(len(analyzer.EXPECTED_PS_PROPERTY_GET_NAMES), 3)
        self.assertEqual(set_names - get_names, {"random-seed"})
        self.assertLess(get_names, set_names)

    def test_external_allowlist_is_outside_scope_and_documented(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(len(analyzer.EXTERNAL_ALLOWLIST), 14)
        for entry, identity in analyzer.EXTERNAL_ALLOWLIST.items():
            self.assertTrue(identity)
            in_region = analyzer.FRONTIER_BASE <= entry < analyzer.FRONTIER_END
            self.assertFalse(
                in_region and entry not in analyzer.EXPECTED_ATTRIBUTION,
                f"allowlist entry 0x{entry:08X} collides with the frontier",
            )
        # The three documented ftsystem externals are all present.
        for entry in analyzer.EXTERNAL_FTSYSTEM:
            self.assertIn(entry, analyzer.EXTERNAL_ALLOWLIST)

    def test_rejected_envelopes_stay_out_of_scope(self) -> None:
        analyzer = self.analyzer
        for entry in analyzer.REGION_REJECTED_ENVELOPES:
            self.assertNotIn(entry, analyzer.EXPECTED_ATTRIBUTION)
            self.assertGreaterEqual(entry, analyzer.FRONTIER_BASE)
            self.assertLess(entry, analyzer.FRONTIER_END)

    def test_located_tables_cover_three_driver_modules(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(len(analyzer.EXPECTED_LOCATED_TABLES), 7)
        modules = {
            key.split(":")[0].split("/")[1]
            for key in analyzer.EXPECTED_LOCATED_TABLES
        }
        self.assertEqual(modules, {"cff", "psaux", "psnames"})
        for address in analyzer.EXPECTED_LOCATED_TABLES.values():
            self.assertGreaterEqual(address, 0x00530000)

    def test_member_hypotheses_reference_real_attributions(self) -> None:
        analyzer = self.analyzer
        for entry, hypothesis in analyzer.MEMBER_HYPOTHESES.items():
            self.assertIn(entry, analyzer.EXPECTED_ATTRIBUTION)
            self.assertTrue(hypothesis.endswith(")") or "candidate" in hypothesis)
            status = analyzer.EXPECTED_ATTRIBUTION[entry][0]
            self.assertEqual(status, "cluster")

    def test_ps_property_name_parser_on_synthetic_source(self) -> None:
        analyzer = self.analyzer
        source = (
            "  ps_property_set( FT_Module module, const char* property_name )"
            " { if ( !ft_strcmp( property_name, \"alpha\" ) ) return 0;"
            "   else if ( !ft_strcmp( property_name, \"beta\" ) ) return 0; }"
            "  ps_property_get( FT_Module module, const char* property_name )"
            " { if ( !ft_strcmp( property_name, \"alpha\" ) ) return 0; }"
        )
        names = analyzer.PS_PROPERTY_NAME_RE.findall(source)
        self.assertEqual(names, ["alpha", "beta", "alpha"])

    def test_table_parser_rejects_non_scalar_arrays(self) -> None:
        analyzer = self.analyzer
        self.assertIsNone(analyzer._parse_array_body("FT_UShort", " 1, FOO, 3 "))
        self.assertIsNone(analyzer._parse_array_body("FT_UShort", " "))
        data = analyzer._parse_array_body("FT_UShort", " 1, 0x2, 3u ")
        self.assertEqual(data, b"\x01\x00\x02\x00\x03\x00")

    def test_string_cell_targets_find_bodies_and_cells(self) -> None:
        analyzer = self.analyzer
        blob = bytearray(256)
        blob[0x40:0x46] = b"warp\x00"
        import struct as _struct

        _struct.pack_into("<I", blob, 0x80, 0x1000 + 0x40)
        targets = analyzer.string_cell_targets(bytes(blob), 0x1000, ("warp",))
        self.assertEqual(targets[0x1040], "warp")
        self.assertEqual(targets[0x1080], "warp")

    def test_community_closure_on_synthetic_graph(self) -> None:
        analyzer = self.analyzer
        functions = synthetic_functions()
        callers = analyzer.caller_map(functions)
        scope = {0x2000, 0x3000, 0x4000, 0x5000, 0x6000, 0x8100}
        community = analyzer.grow_community(
            {0x1000}, scope, functions, callers, {0x9000}
        )
        # 0x1000 is a seed outside the scope; in-scope members join only
        # through admissible edges.
        self.assertEqual(
            community, {0x1000, 0x2000, 0x3000, 0x4000, 0x5000, 0x8100}
        )
        # 0x6000 stays out: its callee 0x7000 reaches a stranger.

    def test_community_closure_rejects_stranger_chains(self) -> None:
        analyzer = self.analyzer
        functions = synthetic_functions()
        functions[0x7000] = {
            "calls": {0x1000},  # now 0x7000 reaches the seed: chain unblocks
            "dat_refs": set(),
            "tokens": set(),
            "body_start": 0,
            "body_end_exclusive": 0,
        }
        callers = analyzer.caller_map(functions)
        scope = {0x2000, 0x3000, 0x4000, 0x5000, 0x6000, 0x7000}
        community = analyzer.grow_community(
            {0x1000}, scope, functions, callers, {0x9000}
        )
        self.assertIn(0x6000, community)
        self.assertIn(0x7000, community)

    def test_table_module_pin_uses_provenance_count(self) -> None:
        analyzer = self.analyzer
        provenance = SNAPSHOT / "PROVENANCE.json"
        if not provenance.is_file():
            self.skipTest("snapshot provenance unavailable")
        import json

        files = json.loads(provenance.read_text(encoding="utf-8"))["files"]
        self.assertEqual(len(files), 297)
        for name in analyzer.TABLE_SOURCES + (analyzer.PSPROP_SOURCE,):
            self.assertIn(name, {row["local_path"] for row in files})


@unittest.skipUnless(
    CORPUS.is_dir() and PLAN.is_file() and REPORT.is_file(),
    "authenticated corpus/current build unavailable",
)
class FreeTypeCensusAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_scope_reconciles_with_parent_census(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["frontier_functions"], 342)
        self.assertEqual(reconciliation["frontier_official_bytes"], 75_016)
        self.assertEqual(reconciliation["frontier_51_functions"], 87)
        self.assertEqual(reconciliation["frontier_51_official_bytes"], 36_812)
        self.assertEqual(reconciliation["frontier_52_functions"], 255)
        self.assertEqual(reconciliation["frontier_52_official_bytes"], 38_204)
        self.assertEqual(reconciliation["freetype_bucket_functions"], 2)
        self.assertEqual(reconciliation["freetype_bucket_official_bytes"], 946)
        self.assertEqual(reconciliation["scope_functions"], 344)

    def test_attribution_and_investigation_reconcile(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["attributed_functions"], 83)
        self.assertEqual(reconciliation["attributed_official_bytes"], 7_874)
        self.assertEqual(reconciliation["investigation_functions"], 261)
        self.assertEqual(reconciliation["investigation_official_bytes"], 68_088)
        self.assertEqual(7_874 + 68_088, 75_016 + 946)
        rows = self.report["functions"]
        self.assertEqual(len(rows), 344)
        self.assertEqual(
            sum(row["official_opaque_bytes"] for row in rows), 75_962
        )

    def test_tier_census_is_pinned(self) -> None:
        actual = {}
        for row in self.report["functions"]:
            functions, official = actual.get(row["evidence"], (0, 0))
            actual[row["evidence"]] = (
                functions + 1,
                official + row["official_opaque_bytes"],
            )
        self.assertEqual(actual, EXPECTED_TIER_COUNTS)

    def test_module_summary_is_pinned(self) -> None:
        self.assertEqual(
            self.report["module_summary"],
            [{"module": "base", "functions": 83, "official_opaque_bytes": 7_874}],
        )

    def test_anchor_rows_are_pinned(self) -> None:
        by_entry = {row["entry"]: row for row in self.report["functions"]}
        record = by_entry[0x00526814]
        self.assertEqual(record["status"], "module")
        self.assertEqual(record["module"], "base")
        self.assertEqual(record["attribution"], "FT_Done_Face")
        self.assertEqual(record["evidence"], "documented-api-anchor")
        self.assertEqual(record["confidence"], "high")
        self.assertEqual(record["scope"], "freetype-bucket")
        self.assertEqual(
            (record["body_start"], record["body_end_exclusive"]),
            (0x00526814, 0x0052687E),
        )
        open_face = by_entry[0x005264A6]
        self.assertEqual(open_face["attribution"], "FT_Open_Face")
        self.assertEqual(open_face["scope"], "freetype-bucket")
        static_open = by_entry[0x005259BE]
        self.assertEqual(static_open["evidence"], "documented-interior-pin")
        self.assertEqual(
            by_entry[0x00527F0A]["attribution"], "ps_property_set (ftpsprop.c)"
        )
        self.assertEqual(
            by_entry[0x00527FF2]["attribution"], "ps_property_get (ftpsprop.c)"
        )

    def test_every_row_has_closed_enums_and_total_coverage(self) -> None:
        analyzer = self.analyzer
        for row in self.report["functions"]:
            self.assertIn(row["status"], analyzer.STATUSES)
            self.assertIn(row["evidence"], analyzer.EVIDENCE_CLASSES)
            self.assertIn(row["confidence"], analyzer.CONFIDENCE_ORDER)
            self.assertIn(row["scope"], ("frontier", "freetype-bucket"))
            if row["status"] == "investigation-required":
                self.assertEqual(row["module"], "")
                self.assertEqual(row["evidence"], "none")
            else:
                self.assertEqual(row["module"], "base")

    def test_snapshot_table_census_is_pinned(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["snapshot_tables_parsed"], 8)
        self.assertEqual(reconciliation["snapshot_tables_located"], 7)

    def test_external_observations_are_pinned(self) -> None:
        observations = self.report["external_observations"]
        self.assertEqual(len(observations), 4)
        by_entry = {row["entry"]: row for row in observations}
        stream_new = by_entry[0x00524F96]
        self.assertEqual(stream_new["parent_bucket"], "lvgl")
        self.assertEqual(stream_new["evidence"], "anchor-callee-external")
        # FT_Stream_Open is path-anchored (am_ftsystem.c retains __FILE__);
        # FT_New_Memory/FT_Done_Memory are unanchored no-evidence functions.
        self.assertEqual(by_entry[0x005675E8]["parent_bucket"], "path-anchored")
        for entry in (0x005676A0, 0x005676C6):
            self.assertEqual(by_entry[entry]["confidence"], "high")
            self.assertEqual(
                by_entry[entry]["parent_bucket"],
                "investigation-required-no-evidence",
            )
        self.assertEqual(by_entry[0x005675E8]["confidence"], "high")

    def test_checked_in_manifests_match_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "g2-freetype-engine-census.tsv").write_text(
                self.analyzer.map_tsv(self.report), encoding="utf-8"
            )
            (root / "g2-freetype-engine-census-summary.json").write_text(
                self.analyzer.summary_json(self.report), encoding="utf-8"
            )
            for name in (
                "g2-freetype-engine-census.tsv",
                "g2-freetype-engine-census-summary.json",
            ):
                self.assertEqual(
                    (root / name).read_bytes(),
                    (MANIFESTS / name).read_bytes(),
                    f"checked-in manifest drifted: {name}",
                )

    def test_attribution_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_ATTRIBUTION
        mutated = dict(original)
        entry = sorted(mutated)[0]
        status, module, evidence, _confidence = mutated[entry]
        mutated[entry] = (status, module, evidence, "low")
        analyzer.EXPECTED_ATTRIBUTION = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_ATTRIBUTION = original

    def test_anchor_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.DOCUMENTED_ANCHORS
        mutated = dict(original)
        anchor = dict(mutated[0x00526814])
        anchor["body"] = (0x00526814, 0x00526880)
        mutated[0x00526814] = anchor
        analyzer.DOCUMENTED_ANCHORS = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.DOCUMENTED_ANCHORS = original

    def test_ps_property_set_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_PS_PROPERTY_SET_NAMES
        analyzer.EXPECTED_PS_PROPERTY_SET_NAMES = original + ("bogus",)
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_PS_PROPERTY_SET_NAMES = original

    def test_located_table_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_LOCATED_TABLES
        mutated = dict(original)
        key = sorted(mutated)[0]
        mutated[key] = mutated[key] + 4
        analyzer.EXPECTED_LOCATED_TABLES = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_LOCATED_TABLES = original

    def test_allowlist_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXTERNAL_ALLOWLIST
        mutated = dict(original)
        mutated[0x00439712] = mutated.pop(0x00439710)
        analyzer.EXTERNAL_ALLOWLIST = mutated
        try:
            with self.assertRaises(analyzer.CensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXTERNAL_ALLOWLIST = original


if __name__ == "__main__":
    unittest.main()
