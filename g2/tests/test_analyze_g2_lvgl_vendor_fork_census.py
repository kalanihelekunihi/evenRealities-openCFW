#!/usr/bin/env python3
"""Guard the G2 LVGL vendor-fork object census."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_lvgl_vendor_fork_census.py"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)
PARENT_TSV = ROOT / "tools/manifests/g2-apollo-unanchored-census-functions.tsv"
MANIFESTS_DIR = ROOT / "tools/manifests"
MANIFEST_TSV = MANIFESTS_DIR / "g2-lvgl-vendor-fork-census.tsv"
MANIFEST_JSON = MANIFESTS_DIR / "g2-lvgl-vendor-fork-census-summary.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_lvgl_vendor_fork_census", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class VendorForkCensusUnitTests(unittest.TestCase):
    """Corpus-independent checks of the census rule tables and parsers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_module_rules_are_total_over_representative_paths(self) -> None:
        module = self.analyzer.lvgl_module
        prefix = "third_party\\lvgl_v9.3\\"
        cases = {
            "LVGL\\src\\core\\lv_obj_style.c": "lvgl-core",
            "LVGL\\src\\lv_init.c": "lvgl-core",
            "LVGL\\src\\display\\lv_display.c": "lvgl-display",
            "LVGL\\src\\draw\\lv_draw.c": "lvgl-draw",
            "LVGL\\src\\draw\\ambiq\\lv_draw_ambiq.c": "ambiq-draw-backend",
            "LVGL\\src\\font\\lv_font.c": "lvgl-font",
            "LVGL\\src\\layouts\\flex\\lv_flex.c": "lvgl-layouts",
            "LVGL\\src\\libs\\bin_decoder\\lv_bin_decoder.c": "lvgl-bin-decoder",
            "LVGL\\src\\libs\\bmp\\lv_bmp.c": "lvgl-bmp-decoder",
            "LVGL\\src\\libs\\freetype\\lv_freetype.c": "lvgl-freetype-wrapper",
            "LVGL\\src\\libs\\fsdrv\\lv_fs_littlefs.c": "lvgl-fsdrv",
            "LVGL\\src\\misc\\cache\\lv_cache.c": "lvgl-cache",
            "LVGL\\src\\misc\\lv_timer.c": "lvgl-misc",
            "LVGL\\src\\osal\\lv_freertos.c": "lvgl-osal-freertos",
            "LVGL\\src\\stdlib\\lv_mem.c": "lvgl-stdlib",
            "LVGL\\src\\widgets\\label\\lv_label.c": "lvgl-widgets",
            "lvgl_ambiq_porting\\lv_ambiq_display.c": "ambiq-display-port",
            "lvgl_ambiq_demo\\lvgl_ttf\\src\\am_ftsystem.c": "ambiq-freetype-system",
        }
        for relative, expected in cases.items():
            name, source_file = module(prefix + relative)
            self.assertEqual(name, expected, relative)
            self.assertEqual(source_file, relative.replace("\\", "/"))
        with self.assertRaises(self.analyzer.VendorForkCensusError):
            module(prefix + "LVGL\\src\\gpu\\lv_draw_nema.c")
        with self.assertRaises(self.analyzer.VendorForkCensusError):
            module("third_party\\littlefs\\lfs.c")

    def test_evidence_and_confidence_tables_are_closed(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(
            set(analyzer.EVIDENCE_CLASSES), set(analyzer.CONFIDENCE_BY_EVIDENCE)
        )
        self.assertEqual(len(analyzer.EVIDENCE_CLASSES), 8)
        for confidence in analyzer.CONFIDENCE_BY_EVIDENCE.values():
            self.assertIn(confidence, ("medium", "low", "none"))

    def test_scope_rules(self) -> None:
        scope = self.analyzer._scope_of
        base = {
            "entry": "0x00500000",
            "bucket": "lvgl",
            "evidence": "call-topology-single-family",
        }
        self.assertEqual(scope(base), "lvgl-topology")
        self.assertEqual(
            scope(dict(base, evidence="link-order-sandwich")), "lvgl-sandwich"
        )
        noev = dict(base, bucket="investigation-required-no-evidence", evidence="none")
        self.assertEqual(scope(dict(noev, entry="0x005D4ED0")), "sea-0x5d")
        self.assertEqual(scope(dict(noev, entry="0x005A0000")), "sea-0x5a")
        self.assertIsNone(scope(dict(noev, entry="0x005E0000")))
        self.assertIsNone(scope(dict(noev, entry="0x005CFFFF")))
        self.assertIsNone(scope(dict(base, bucket="first-party")))
        self.assertIsNone(scope(dict(base, evidence="closed-module-manifest")))

    def test_frozen_census_is_internally_consistent(self) -> None:
        analyzer = self.analyzer
        self.assertEqual(sum(analyzer.EXPECTED_SCOPE.values()), 1_484)
        self.assertEqual(
            analyzer.EXPECTED_SCOPE_OFFICIAL_BYTES["lvgl-topology"]
            + analyzer.EXPECTED_SCOPE_OFFICIAL_BYTES["lvgl-sandwich"],
            analyzer.EXPECTED_LVGL_BUCKET_OFFICIAL_BYTES,
        )
        self.assertEqual(analyzer.EXPECTED_SCOPE_OFFICIAL_BYTES["sea-0x5d"], 52_866)
        self.assertEqual(analyzer.EXPECTED_SCOPE_OFFICIAL_BYTES["sea-0x5a"], 37_058)
        self.assertEqual(
            sum(m["functions"] for m in analyzer.EXPECTED_MODULE_CENSUS.values()), 1_484
        )
        self.assertEqual(sum(analyzer.EXPECTED_EVIDENCE_CENSUS.values()), 1_484)
        backend = {
            name
            for name in analyzer.EXPECTED_MODULE_CENSUS
            if name in analyzer.VENDOR_BACKEND_MODULES
        }
        self.assertEqual(
            backend,
            {"ambiq-draw-backend", "ambiq-display-port", "ambiq-freetype-system"},
        )

    def test_parent_census_loader_reads_checked_in_manifest(self) -> None:
        rows = self.analyzer.load_parent_census(PARENT_TSV)
        self.assertEqual(len(rows), 5_610)
        lvgl = [row for row in rows.values() if row["bucket"] == "lvgl"]
        self.assertEqual(len(lvgl), 1_054)
        self.assertEqual(
            sum(int(row["official_opaque_bytes"]) for row in lvgl), 97_430
        )

    def test_parent_census_loader_fails_closed_on_count_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            lines = PARENT_TSV.read_text(encoding="utf-8").splitlines()
            target.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
            with self.assertRaises(self.analyzer.VendorForkCensusError):
                self.analyzer.load_parent_census(target)

    def test_parent_census_loader_fails_closed_on_duplicate_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            lines = PARENT_TSV.read_text(encoding="utf-8").splitlines()
            data_row = next(
                line for line in lines if line and not line.startswith("#")
                and not line.startswith("entry\t")
            )
            target.write_text(
                "\n".join(lines + [data_row]) + "\n", encoding="utf-8"
            )
            with self.assertRaises(self.analyzer.VendorForkCensusError):
                self.analyzer.load_parent_census(target)

    def test_parent_census_loader_fails_closed_on_schema_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            text = PARENT_TSV.read_text(encoding="utf-8").replace(
                "official_opaque_bytes", "opaque_bytes", 1
            )
            target.write_text(text, encoding="utf-8")
            with self.assertRaises(self.analyzer.VendorForkCensusError):
                self.analyzer.load_parent_census(target)

    def test_parent_census_loader_fails_closed_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(self.analyzer.VendorForkCensusError):
                self.analyzer.load_parent_census(Path(directory) / "absent.tsv")


@unittest.skipUnless(CORPUS.is_dir(), "authenticated Ghidra corpus unavailable")
class VendorForkCensusAuthenticatedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(CORPUS)

    def test_scope_reconciles_with_parent_census(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["scope_functions"], 1_484)
        self.assertEqual(reconciliation["parent_lvgl_bucket_functions"], 1_054)
        self.assertEqual(
            reconciliation["parent_lvgl_bucket_official_bytes"], 97_430
        )
        expected_scopes = {
            name: {
                "functions": self.analyzer.EXPECTED_SCOPE[name],
                "official_opaque_bytes": self.analyzer.EXPECTED_SCOPE_OFFICIAL_BYTES[name],
            }
            for name in self.analyzer.EXPECTED_SCOPE
        }
        self.assertEqual(reconciliation["scopes"], expected_scopes)

    def test_module_census_is_pinned(self) -> None:
        actual = {
            module["module"]: {
                "functions": module["functions"],
                "official_opaque_bytes": module["official_opaque_bytes"],
            }
            for module in self.report["modules"]
        }
        self.assertEqual(actual, self.analyzer.EXPECTED_MODULE_CENSUS)

    def test_evidence_census_is_pinned(self) -> None:
        self.assertEqual(
            self.report["reconciliation"]["evidence_classes"],
            self.analyzer.EXPECTED_EVIDENCE_CENSUS,
        )

    def test_evidence_and_confidence_classes_are_closed(self) -> None:
        valid_modules = set(self.analyzer.EXPECTED_MODULE_CENSUS)
        for record in self.report["functions"]:
            self.assertIn(record["evidence"], self.analyzer.EVIDENCE_CLASSES)
            self.assertIn(record["module"], valid_modules)
            self.assertEqual(
                record["confidence"],
                self.analyzer.CONFIDENCE_BY_EVIDENCE[record["evidence"]],
            )
            if record["evidence"] in ("call-topology-mixed", "none"):
                self.assertEqual(record["module"], "investigation-required")
            else:
                self.assertNotEqual(record["module"], "investigation-required")
            if record["evidence"].endswith("single-file") or record["evidence"] in (
                "call-topology-second-order-file",
                "link-order-file-sandwich",
            ):
                self.assertTrue(record["source_file"])

    def test_seas_stay_investigation_required(self) -> None:
        # The parent census hypotheses for the 0x5D/0x5A seas are not
        # confirmed: no sea function carries any within-LVGL evidence.
        for record in self.report["functions"]:
            if record["scope"] in ("sea-0x5d", "sea-0x5a"):
                self.assertEqual(record["module"], "investigation-required")
                self.assertEqual(record["evidence"], "none")
        by_entry = {record["entry"]: record for record in self.report["functions"]}
        largest = by_entry[0x005D4ED0]
        self.assertEqual(largest["envelope_bytes"], 7_880)
        self.assertEqual(largest["module"], "investigation-required")

    def test_vendor_backend_members_are_pinned(self) -> None:
        backend = [
            record
            for record in self.report["functions"]
            if record["module"] in self.analyzer.VENDOR_BACKEND_MODULES
        ]
        self.assertEqual(len(backend), 15)
        self.assertEqual(
            sum(record["official_opaque_bytes"] for record in backend), 4_080
        )
        self.assertTrue(
            all(record["module"].startswith("ambiq-") for record in backend)
        )

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
        analyzer.EXPECTED_EVIDENCE_CENSUS = dict(original, none=original["none"] + 1)
        try:
            with self.assertRaises(analyzer.VendorForkCensusError):
                analyzer.analyze(CORPUS)
        finally:
            analyzer.EXPECTED_EVIDENCE_CENSUS = original

    def test_parent_census_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / PARENT_TSV.name
            shutil.copy(PARENT_TSV, target)
            text = target.read_text(encoding="utf-8").replace(
                "\tlvgl\tcall-topology-single-family\t",
                "\tfirst-party\tcall-topology-single-family\t",
                1,
            )
            target.write_text(text, encoding="utf-8")
            with self.assertRaises(analyzer.VendorForkCensusError):
                analyzer.analyze(CORPUS, census_tsv=target)


if __name__ == "__main__":
    unittest.main()
