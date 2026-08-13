#!/usr/bin/env python3
"""Guard the EM9305 residual provenance classification."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_em9305_residual_provenance.py"
MANIFEST = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
IMAGE_SHA256 = "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
PACKAGE_MAP_BASE = 0x0030_1FDC


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location(
            "analyze_em9305_residual_provenance", TOOL
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def base_record(**overrides):
    record = {
        "start": 0x0031_0000,
        "end": 0x0031_0020,
        "size": 32,
        "sha256": "00" * 32,
        "ninsn": 8,
        "insns": [],
        "bl_count": 0,
        "id_calls": 0,
        "res_calls": 0,
        "rom_calls": 0,
        "named_callees": [],
        "callee_families": [],
        "neighbor_families": [],
        "branch_only": False,
        "rom_branch_targets": 0,
        "has_internal_branch": False,
        "id_tail_refs": 0,
        "tail_families": [],
        "named_tail_targets": [],
        "assertion_sites": [],
        "ram_imm_refs": 0,
        "stack_limit_refs": 0,
        "has_brk": False,
        "has_blink_return": False,
        "runtime_arith": [],
        "prologue": False,
        "entry_branches": 0,
        "incoming_calls": 0,
        "imm_in": 0,
        "hook_table_entry": False,
        "mem_runtime_tail_ref": False,
    }
    record.update(overrides)
    return record


class Em9305ResidualProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_exactly_seven_ownership_categories(self) -> None:
        self.assertEqual(len(self.tool.OWNERSHIP_CATEGORIES), 7)
        self.assertEqual(
            list(self.tool.OWNERSHIP_CATEGORIES),
            [
                "public_upstream_redistribution_safe",
                "sdk_oracle_matched_license_unresolved",
                "vendor_modified_upstream_identified",
                "proprietary_modern_controller_source_unavailable",
                "toolchain_or_linker_generated",
                "first_party_application_retained",
                "unclassified_insufficient_evidence",
            ],
        )

    def test_expected_census_constants_are_consistent(self) -> None:
        tool = self.tool
        self.assertEqual(sum(tool.EXPECTED_CATEGORY_COUNTS.values()), 175)
        self.assertEqual(sum(tool.EXPECTED_CATEGORY_BYTES.values()), 33_658)
        self.assertEqual(
            sum(tool.EXPECTED_FAMILY_BYTES.values()),
            tool.EXPECTED_CATEGORY_BYTES[tool.CAT_PROPRIETARY_CONTROLLER],
        )
        self.assertEqual(sum(tool.EXPECTED_STRUCTURAL_COUNTS.values()), 175)
        self.assertEqual(
            set(tool.EXPECTED_CATEGORY_COUNTS) | set(tool.EXPECTED_CATEGORY_BYTES),
            {
                tool.CAT_PROPRIETARY_CONTROLLER,
                tool.CAT_TOOLCHAIN,
                tool.CAT_FIRST_PARTY_APP,
                tool.CAT_UNCLASSIFIED,
            },
        )
        # No residual segment may claim source availability categories.
        for empty_category in (
            tool.CAT_PUBLIC_UPSTREAM,
            tool.CAT_SDK_ORACLE,
            tool.CAT_VENDOR_MODIFIED,
        ):
            self.assertNotIn(empty_category, tool.EXPECTED_CATEGORY_COUNTS)
        for start, pinned in tool.EXPECTED_KEY_SEGMENTS.items():
            size, structural, category, family, confidence = pinned
            self.assertGreater(size, 0)
            self.assertIn(category, tool.OWNERSHIP_CATEGORIES)
            self.assertIn(confidence, {"high", "medium", "low"})
            self.assertIn(structural, tool.EXPECTED_STRUCTURAL_COUNTS)
            self.assertGreaterEqual(start, tool.APP_BASE)
            self.assertLess(start, tool.APP_END)

    def test_manifest_rows_match_blob_and_constants(self) -> None:
        tool = self.tool
        image = IMAGE.resolve().read_bytes()
        if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
            raise unittest.SkipTest("official EM9305 blob not available")
        with MANIFEST.open(newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
        self.assertEqual(len(rows), 175)
        category_counts = {}
        category_bytes = {}
        structural_counts = {}
        family_bytes = {}
        key_segments = {}
        previous_end = None
        for row in rows:
            start = int(row["start"], 16)
            end = int(row["end"], 16)
            size = int(row["size"])
            self.assertEqual(end - start, size)
            body = image[start - PACKAGE_MAP_BASE:end - PACKAGE_MAP_BASE]
            self.assertEqual(hashlib.sha256(body).hexdigest(), row["sha256"])
            if previous_end is not None:
                self.assertGreaterEqual(start, previous_end)
            previous_end = end
            self.assertIn(row["ownership_category"], tool.OWNERSHIP_CATEGORIES)
            self.assertIn(row["confidence"], {"high", "medium", "low"})
            self.assertTrue(row["evidence"])
            category_counts[row["ownership_category"]] = (
                category_counts.get(row["ownership_category"], 0) + 1
            )
            category_bytes[row["ownership_category"]] = (
                category_bytes.get(row["ownership_category"], 0) + size
            )
            structural_counts[row["structural_class"]] = (
                structural_counts.get(row["structural_class"], 0) + 1
            )
            if row["ownership_category"] == tool.CAT_PROPRIETARY_CONTROLLER:
                family_bytes[row["family_hint"]] = (
                    family_bytes.get(row["family_hint"], 0) + size
                )
            if start in tool.EXPECTED_KEY_SEGMENTS:
                key_segments[start] = (
                    size,
                    row["structural_class"],
                    row["ownership_category"],
                    row["family_hint"],
                    row["confidence"],
                )
        self.assertEqual(category_counts, tool.EXPECTED_CATEGORY_COUNTS)
        self.assertEqual(category_bytes, tool.EXPECTED_CATEGORY_BYTES)
        self.assertEqual(structural_counts, tool.EXPECTED_STRUCTURAL_COUNTS)
        self.assertEqual(family_bytes, tool.EXPECTED_FAMILY_BYTES)
        self.assertEqual(key_segments, tool.EXPECTED_KEY_SEGMENTS)

    def test_named_hook_stub_rule_is_fail_closed(self) -> None:
        tool = self.tool
        record = base_record(
            start=0x0031_1150,
            size=4,
            ninsn=1,
            insns=[("b", ";0x310798")],
        )
        structural, category, family, confidence, evidence = tool.classify_segment(record)
        self.assertEqual(
            (structural, category, family, confidence),
            ("hook_stub", tool.CAT_FIRST_PARTY_APP, "qpc_vendor_hook", "high"),
        )
        self.assertIn("authenticated_hook_stub:QF_onResumeInternalHook", evidence[0])
        tampered = base_record(
            start=0x0031_1150,
            size=4,
            ninsn=1,
            insns=[("b", ";0x310799")],
        )
        with self.assertRaises(tool.ResidualProvenanceError):
            tool.classify_segment(tampered)

    def test_arith_runtime_vocabulary_guard(self) -> None:
        tool = self.tool
        record = base_record(
            start=tool.ARITH_RUNTIME_SEGMENT_START,
            size=822,
            runtime_arith=["divu", "macdu", "mpy", "norm"],
            stack_limit_refs=1,
            has_brk=True,
            prologue=True,
            entry_branches=1,
        )
        structural, category, family, confidence, _ = tool.classify_segment(record)
        self.assertEqual(
            (structural, category, family, confidence),
            ("runtime_support_code", tool.CAT_TOOLCHAIN,
             "metaware_arith_runtime", "high"),
        )
        degraded = dict(record, runtime_arith=[])
        with self.assertRaises(tool.ResidualProvenanceError):
            tool.classify_segment(degraded)

    def test_synthetic_rule_outcomes(self) -> None:
        tool = self.tool
        # Authenticated hook-pointer-table entry.
        outcome = tool.classify_segment(base_record(
            start=0x0030_EB8C,
            hook_table_entry=True,
            prologue=True,
            named_callees=["BSP_Init"],
        ))
        self.assertEqual(outcome[:4], (
            "code_function", tool.CAT_FIRST_PARTY_APP, "application_hook", "high",
        ))
        # ROM wrapper with register shuffling.
        outcome = tool.classify_segment(base_record(
            size=18,
            ninsn=7,
            rom_branch_targets=1,
        ))
        self.assertEqual(outcome[:4], (
            "code_veneer", tool.CAT_PROPRIETARY_CONTROLLER,
            "em_vendor_rom_wrapper", "medium",
        ))
        # MetaWare memset tail stub: ownership stays unclassified.
        outcome = tool.classify_segment(base_record(
            size=14,
            ninsn=4,
            mem_runtime_tail_ref=True,
        ))
        self.assertEqual(outcome[:4], (
            "code_veneer", tool.CAT_UNCLASSIFIED, "unknown", "low",
        ))
        # Packetcraft call frontier with prologue and three callees.
        outcome = tool.classify_segment(base_record(
            prologue=True,
            bl_count=3,
            id_calls=3,
            callee_families=["packetcraft_modern_controller"] * 3,
            named_callees=["BbStart", "SchRmAdd", "WsfMsgSend"],
        ))
        self.assertEqual(outcome[:4], (
            "code_function", tool.CAT_PROPRIETARY_CONTROLLER,
            "packetcraft_modern_controller", "high",
        ))
        # MyApp assertion-site segment is first-party application code.
        outcome = tool.classify_segment(base_record(
            size=258,
            ninsn=80,
            assertion_sites=[("0x0030EACE", "MyApp", 181)],
            named_callees=["QF_newX_", "Q_onAssert"],
        ))
        self.assertEqual(outcome[:4], (
            "code_fragment", tool.CAT_FIRST_PARTY_APP,
            "application_module_myapp", "high",
        ))
        # Feature-free bytes remain explicitly unclassified, never guessed.
        outcome = tool.classify_segment(base_record(ninsn=0))
        self.assertEqual(outcome[:4], (
            "opaque_code_or_data", tool.CAT_UNCLASSIFIED, "unknown", "low",
        ))

    def test_no_rule_assigns_source_availability_categories(self) -> None:
        tool = self.tool
        probes = [
            base_record(),
            base_record(prologue=True, bl_count=5, id_calls=5,
                        callee_families=["packetcraft_modern_controller"] * 5),
            base_record(hook_table_entry=True),
            base_record(size=4, ninsn=1, branch_only=True, imm_in=3),
            base_record(size=16, ninsn=4, bl_count=2,
                        callee_families=["em_vendor_system"] * 2, rom_calls=1),
        ]
        for probe in probes:
            _structural, category, _family, _confidence, _evidence = (
                tool.classify_segment(probe)
            )
            self.assertNotIn(category, {
                tool.CAT_PUBLIC_UPSTREAM,
                tool.CAT_SDK_ORACLE,
                tool.CAT_VENDOR_MODIFIED,
            })


if __name__ == "__main__":
    unittest.main()
