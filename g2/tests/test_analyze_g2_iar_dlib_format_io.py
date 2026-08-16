#!/usr/bin/env python3
"""Guard the IAR DLIB formatted-I/O bounded audit.

The analyzer ``tools/analyze_g2_iar_dlib_format_io.py`` pins the twelve-unit
``iar-dlib`` formatted-I/O cluster of the Apollo unanchored census: exact
body spans and SHA-256, decode census, DLIB diagnostic-string
materializations, image-wide BL/B.W ingress digests, the stored-pointer
vacuity check, and the per-unit provider decisions.  This guard proves rule
totality, exact pins, fail-closed mutation rejection, and byte-for-byte
manifest regeneration.  Corpus-backed checks are gated on
``OPENCFW_APOLLO_GHIDRA_CORPUS`` (default
``/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth``).
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_iar_dlib_format_io.py"
MANIFEST = ROOT / "tools" / "manifests" / "g2-iar-dlib-format-io-map.tsv"
CENSUS_TSV = ROOT / "tools" / "manifests" / "g2-apollo-unanchored-census-functions.tsv"
CORPUS = Path(
    os.environ.get(
        "OPENCFW_APOLLO_GHIDRA_CORPUS",
        "/var/tmp/opencfw-apollo64-return.3LC1Dq/full64-j64-auth",
    )
)

EXPECTED_SPANS = {
    # unit: (start, end_exclusive, bytes, ingress_bl, ingress_bw, decision)
    "bounded_printf_wrapper_a": (0x0044B728, 0x0044B766, 62, 156, 0, "clean-room-recreate"),
    "bounded_printf_wrapper_b": (0x0044B76C, 0x0044B7A2, 54, 3, 0, "clean-room-recreate"),
    "string_scanf_wrapper": (0x00475FC0, 0x00475FE2, 34, 7, 0, "recreated-production"),
    "printf_core": (0x00481836, 0x004824EE, 3256, 4, 0, "licensed-retention"),
    "unbounded_printf_wrapper": (0x004B4728, 0x004B4762, 58, 75, 0, "clean-room-recreate"),
    "scanf_core": (0x004D1638, 0x004D2112, 2778, 1, 0, "licensed-retention"),
    "scanset_matcher": (0x004D2112, 0x004D2158, 70, 2, 0, "clean-room-recreate"),
    "scanf_string_helper": (0x004D2158, 0x004D22FC, 420, 1, 0, "clean-room-recreate"),
    "constraint_dispatcher": (0x004D40A0, 0x004D40BC, 28, 3, 0, "clean-room-recreate"),
    "strtod_engine": (0x00542C20, 0x00542D0C, 236, 1, 0, "licensed-retention"),
    "hexfloat_scanner": (0x00585410, 0x005855E2, 466, 2, 0, "clean-room-recreate"),
    "default_output_printf_wrapper": (0x00595A34, 0x00595A56, 34, 2, 0, "clean-room-recreate"),
}

EXPECTED_CORPUS_SPLIT = {
    # unit: (corpus-token-verified callers, unverifiable raw sites)
    "bounded_printf_wrapper_a": (115, 41),
    "bounded_printf_wrapper_b": (3, 0),
    "string_scanf_wrapper": (3, 4),
    "printf_core": (4, 0),
    "unbounded_printf_wrapper": (65, 10),
    "scanf_core": (1, 0),
    "scanset_matcher": (2, 0),
    "scanf_string_helper": (1, 0),
    "constraint_dispatcher": (3, 0),
    "strtod_engine": (1, 0),
    "hexfloat_scanner": (1, 1),
    "default_output_printf_wrapper": (2, 0),
}

VALID_DECISIONS = frozenset(
    {"clean-room-recreate", "licensed-retention", "recreated-production"}
)


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_iar_dlib_format_io", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FormatIoRuleTests(unittest.TestCase):
    """Corpus-independent checks of the audit rule tables."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_signature_string_table_is_total_and_self_consistent(self) -> None:
        strings = self.analyzer.SIGNATURE_STRINGS
        self.assertEqual(len(strings), 10)
        keys = [row[0] for row in strings]
        texts = [row[1] for row in strings]
        addresses = [row[2] for row in strings]
        self.assertEqual(len(set(keys)), 10)
        self.assertEqual(len(set(texts)), 10)
        self.assertEqual(len(set(addresses)), 10)
        for key, text, _address, digest in strings:
            self.assertTrue(key)
            self.assertEqual(
                hashlib.sha256(text.encode("ascii") + b"\x00").hexdigest(), digest
            )
        # The Annex-K spellings and the constraint-handler diagnostic are the
        # DLIB-only provenance anchors.
        self.assertTrue(any("printf_s" in text for text in texts))
        self.assertTrue(any("scanf_s" in text for text in texts))
        self.assertTrue(any("constraint handler" in text for text in texts))

    def test_evidence_spans_are_well_formed(self) -> None:
        spans = self.analyzer.EVIDENCE_SPANS
        self.assertEqual(len(spans), 6)
        names = [row[0] for row in spans]
        self.assertEqual(len(set(names)), 6)
        for _name, start, end, digest in spans:
            self.assertLess(start, end)
            self.assertEqual(len(digest), 64)

    def test_unit_pin_totality(self) -> None:
        units = self.analyzer.EXPECTED_UNITS
        self.assertEqual(len(units), 12)
        self.assertEqual(
            tuple(unit["name"] for unit in units), tuple(EXPECTED_SPANS)
        )
        previous_end = None
        for unit in units:
            start, end, code_end = unit["start"], unit["end"], unit["code_end"]
            self.assertLess(start, code_end)
            self.assertLessEqual(code_end, end)
            self.assertEqual((end - code_end) > 0, "data_window_sha256" in unit)
            self.assertEqual(len(unit["sha256"]), 64)
            self.assertEqual(len(unit["ingress_sha256"]), 64)
            self.assertEqual(len(unit["before"]), 16)
            self.assertEqual(len(unit["after"]), 32)
            if previous_end is not None and start < 0x004D0000:
                self.assertGreaterEqual(start, previous_end)
            previous_end = end
        # Every unit has exactly one disposition and vice versa.
        dispositions = self.analyzer.UNIT_DISPOSITIONS
        self.assertEqual(
            {unit["name"] for unit in units}, set(dispositions)
        )
        for name, disposition in dispositions.items():
            self.assertTrue(disposition["role"])
            self.assertIn(disposition["decision"], VALID_DECISIONS)
            self.assertTrue(disposition["condition"])
            self.assertEqual(name in EXPECTED_SPANS, True)

    def test_corpus_ingress_pins_cover_every_unit(self) -> None:
        pins = self.analyzer.CORPUS_INGRESS_PINS
        self.assertEqual(
            set(pins), {unit["name"] for unit in self.analyzer.EXPECTED_UNITS}
        )
        for name, (verified, vdigest, unverified, udigest) in pins.items():
            self.assertEqual(
                (verified, unverified), EXPECTED_CORPUS_SPLIT[name]
            )
            self.assertEqual(len(vdigest), 64)
            self.assertEqual(len(udigest), 64)

    def test_interior_artifact_census_is_pinned(self) -> None:
        self.assertEqual(
            self.analyzer.INTERIOR_ARTIFACTS, ((6064096, "bl", 5052404),)
        )


class FormatIoAuditTests(unittest.TestCase):
    """Image-backed audit checks (no Ghidra corpus required)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_analysis_mode_is_read_only(self) -> None:
        self.assertTrue(self.report["analysis_mode"].startswith("read-only"))
        self.assertEqual(self.report["schema_version"], 1)

    def test_reconciliation_is_pinned(self) -> None:
        reconciliation = self.report["reconciliation"]
        self.assertEqual(reconciliation["units"], 12)
        self.assertEqual(reconciliation["envelope_bytes"], 7_496)
        self.assertEqual(reconciliation["ingress_sites"], 257)
        self.assertEqual(
            reconciliation["provider_decisions"],
            {
                "clean-room-recreate": 8,
                "licensed-retention": 3,
                "recreated-production": 1,
            },
        )

    def test_exact_unit_spans_and_decisions(self) -> None:
        self.assertEqual(len(self.report["units"]), 12)
        for record in self.report["units"]:
            start, end, size, bl, bw, decision = EXPECTED_SPANS[record["name"]]
            with self.subTest(unit=record["name"]):
                self.assertEqual(record["start"], start)
                self.assertEqual(record["end_exclusive"], end)
                self.assertEqual(record["bytes"], size)
                self.assertEqual(record["ingress_bl"], bl)
                self.assertEqual(record["ingress_bw"], bw)
                self.assertEqual(record["provider_decision"], decision)
                self.assertEqual(
                    record["code_bytes"] + record["data_bytes"], size
                )

    def test_exact_unit_body_digests(self) -> None:
        pins = {
            unit["name"]: unit["sha256"] for unit in self.analyzer.EXPECTED_UNITS
        }
        for record in self.report["units"]:
            self.assertEqual(record["sha256"], pins[record["name"]])

    def test_scanf_core_inline_data_window_is_accounted(self) -> None:
        record = next(
            row for row in self.report["units"] if row["name"] == "scanf_core"
        )
        self.assertEqual(record["code_bytes"], 2_756)
        self.assertEqual(record["data_bytes"], 22)

    def test_signature_strings_materialize_from_cluster_units(self) -> None:
        string_records = self.report["signature_strings"]
        self.assertEqual(len(string_records), 10)
        pins = {row[2] for row in self.analyzer.SIGNATURE_STRINGS}
        self.assertEqual({row["address"] for row in string_records}, pins)
        materialized = set()
        for record in self.report["units"]:
            for item in record["string_materializations"]:
                target = item["target"]
                # ``adr``/``addw`` materializations land on the string or one
                # byte in (the constraint message's leading space is skipped).
                self.assertTrue(target in pins or target - 1 in pins)
                materialized.add(target if target in pins else target - 1)
        # The five string-signature units directly materialize eight of the
        # ten diagnostics; the remaining two (scanf_s bad-argument and the
        # scanf_s floating-point diagnostic) are reached through the PIC
        # idiom (pic_references) instead.
        self.assertEqual(len(materialized), 8)

    def test_checked_in_manifest_matches_regeneration(self) -> None:
        regenerated = self.analyzer.map_tsv(self.report)
        self.assertEqual(
            regenerated.encode("utf-8"),
            MANIFEST.read_bytes(),
            "checked-in g2-iar-dlib-format-io-map.tsv drifted",
        )

    def test_body_digest_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_UNITS[3]["sha256"]
        analyzer.EXPECTED_UNITS[3]["sha256"] = "0" * 64
        try:
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()
        finally:
            analyzer.EXPECTED_UNITS[3]["sha256"] = original

    def test_span_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_UNITS[6]["end"]
        analyzer.EXPECTED_UNITS[6]["end"] = original + 2
        try:
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()
        finally:
            analyzer.EXPECTED_UNITS[6]["end"] = original

    def test_signature_address_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.SIGNATURE_STRINGS
        key, text, address, digest = original[0]
        analyzer.SIGNATURE_STRINGS = ((key, text, address + 4, digest),) + original[1:]
        try:
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()
        finally:
            analyzer.SIGNATURE_STRINGS = original

    def test_evidence_span_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EVIDENCE_SPANS
        name, start, end, _digest = original[0]
        analyzer.EVIDENCE_SPANS = ((name, start, end, "0" * 64),) + original[1:]
        try:
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()
        finally:
            analyzer.EVIDENCE_SPANS = original

    def test_ingress_count_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.EXPECTED_UNITS[0]["ingress_bl"]
        analyzer.EXPECTED_UNITS[0]["ingress_bl"] = original + 1
        try:
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze()
        finally:
            analyzer.EXPECTED_UNITS[0]["ingress_bl"] = original

    def test_census_membership_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        with tempfile.TemporaryDirectory() as directory:
            mutated = Path(directory) / "census.tsv"
            shutil.copy(CENSUS_TSV, mutated)
            text = mutated.read_text(encoding="utf-8")
            needle = "0x00481836\t0x00481836\t0x004824EE\t3256\t3256\tiar-dlib\t"
            self.assertIn(needle, text)
            mutated.write_text(
                text.replace(needle, needle.replace("iar-dlib", "first-party"), 1),
                encoding="utf-8",
            )
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze(census_tsv=mutated)

    def test_map_tsv_unmapped_string_target_fails_closed(self) -> None:
        analyzer = self.analyzer
        report = copy.deepcopy(self.report)
        record = next(
            row for row in report["units"] if row["name"] == "printf_core"
        )
        record["string_materializations"][0]["target"] = 0x00790000
        with self.assertRaises(analyzer.AuditError):
            analyzer.map_tsv(report)


@unittest.skipUnless(CORPUS.is_dir(), "authenticated Ghidra corpus unavailable")
class FormatIoCorpusTests(unittest.TestCase):
    """Corpus-backed envelope and caller-verification checks."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze(corpus_root=CORPUS)

    def test_corpus_envelopes_and_caller_split_are_pinned(self) -> None:
        corpus = self.report["corpus"]
        self.assertIsNotNone(corpus)
        self.assertEqual(set(corpus), set(EXPECTED_CORPUS_SPLIT))
        verified_total = 0
        unverified_total = 0
        for name, (verified, unverified) in EXPECTED_CORPUS_SPLIT.items():
            with self.subTest(unit=name):
                self.assertEqual(corpus[name]["verified_callers"], verified)
                self.assertEqual(corpus[name]["unverified_sites"], unverified)
            verified_total += verified
            unverified_total += unverified
        self.assertEqual(verified_total, 201)
        self.assertEqual(unverified_total, 56)
        self.assertEqual(
            verified_total + unverified_total,
            self.report["reconciliation"]["ingress_sites"],
        )

    def test_corpus_pin_mutation_fails_closed(self) -> None:
        analyzer = self.analyzer
        original = analyzer.CORPUS_INGRESS_PINS["scanf_core"]
        analyzer.CORPUS_INGRESS_PINS["scanf_core"] = (
            original[0] + 1,
            original[1],
            original[2],
            original[3],
        )
        try:
            with self.assertRaises(analyzer.AuditError):
                analyzer.analyze(corpus_root=CORPUS)
        finally:
            analyzer.CORPUS_INGRESS_PINS["scanf_core"] = original


if __name__ == "__main__":
    unittest.main()
