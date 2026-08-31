#!/usr/bin/env python3
"""Fail closed when the superseded G2 hardware premise reappears."""

from __future__ import annotations

import csv
import hashlib
import re
import tempfile
import unittest
from pathlib import Path
from typing import Sequence


G2_ROOT = Path(__file__).resolve().parents[1]
TOOLS = G2_ROOT / "tools"
MANIFESTS = TOOLS / "manifests"
COMPONENTS = G2_ROOT / "components"
DOCS = G2_ROOT / "docs"
POLICY = DOCS / "hardware-validation-policy.md"
HISTORICAL_HANDOFF = DOCS / "hardware-validation-2026-08-23.md"
PRODUCT_COMMON = DOCS / "research" / "g2-product-common-recovery.md"
PT_FONT_CRC = DOCS / "research" / "g2-pt-font-crc-production-routing.md"
CURRENT_SOURCE_POLICY_SURFACES = (
    COMPONENTS / "shared" / "cordio" / "runtime_cordio_hci_driver.c",
    TOOLS / "integrate_g2_cordio_wsf_buf_msg_overlay.py",
)
LIVE_PROJECT_PROVENANCE = (
    MANIFESTS / "g2-pb-service-quicklist-provenance.tsv",
    MANIFESTS / "g2-pb-service-setting-provenance.tsv",
    MANIFESTS / "g2-pb-service-notification-provenance.tsv",
    MANIFESTS / "g2-pb-service-dev-setting-provenance.tsv",
)

DEFERRED = "blocked by unavailable physical evidence"
TOKEN_GAP = r"(?:[-_]|[\s\"'])+"
RIGHT_TEMPLE = rf"right{TOKEN_GAP}temple"
LEFT_SIDE = rf"left(?:{TOKEN_GAP}temple)?"
SIDE_SPECIFIC_PREMISE = (
    rf"{RIGHT_TEMPLE}(?:_state)?(?:[\s\"':]+)"
    rf"(?:is(?:[\s\"']+)?)?not(?:[\s\"']+)under(?:[\s\"']+)test"
    rf"|{RIGHT_TEMPLE}(?:[\s\"']+)(?:evidence|execution|hardware)"
    rf"|(?:authorized(?:[\s\"']+))?responsive(?:[\s\"']+G2)?"
    rf"(?:[\s\"']+){RIGHT_TEMPLE}"
    rf"|{LEFT_SIDE}(?:_state)?(?:[\s\"':]+)"
    rf"(?:(?:must(?:[\s\"']+))?(?:remain|stay)s?(?:[\s\"']+))?stock"
    rf"|stock-only(?:[\s\"']+authorized)?(?:[\s\"']+){LEFT_SIDE}"
)
STALE_PREMISE = re.compile(
    r"nonresponsive|unresponsive|unavailable\s+hardware|hardware\s+unavailable|"
    r"blocked\s+by\s+unavailable\s+physical\s+evidence|"
    r"hardware\s+validation\s+(?:is|remains)\s+(?:explicitly\s+)?blocked|"
    r"implemented-in-source;\s*hardware-blocked|"
    r"unavailable\s+authorized|no\s+responsive\s+authorized|"
    r"no\s+authorized[^\n.]{0,160}\bavailable\b|physically\s+available|"
    + SIDE_SPECIFIC_PREMISE,
    re.IGNORECASE,
)
CURRENT_REFERENCE_STALE = re.compile(
    STALE_PREMISE.pattern
    + r"|hardware\s+validation\s+blocked"
    + r"|blocked\s+by\s+unavailable\s+physical\s+evidence"
    + r"|physical\s+evidence\s+(?:is\s+)?unavailable"
    + r"|evidence\s+(?:is|remains)\s+unavailable"
    + r"|evidence\s+remains\s+(?:explicitly\s+)?blocked"
    + r"|no\s+authorized\s+responsive\s+right\s+temple\s+exists"
    + r"|no\s+hardware\s+was\s+present"
    + r"|absence\s+of\s+an\s+authorized\s+responsive"
    + r"|hardware[-\s]+blocked"
    + r"|validation\s+(?:is|remains)\s+(?:explicitly\s+)?(?:evidence-)?blocked"
    + r"|evidence-blocked",
    re.IGNORECASE,
)
RESEARCH_SUPERSESSION_NOTE = """> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence."""
RESEARCH_FAILURE_TERM = re.compile(
    r"\b(?:nonresponsive|unresponsive|unresponsiveness|application(?:[-\s]+)dead)\b",
    re.IGNORECASE,
)
RESEARCH_RIGHT_TEMPLE = re.compile(
    r"\b(?:G2\s+right|right(?:\s*[- ]\s*|\s+)(?:G2\s+)?)temple\b",
    re.IGNORECASE,
)
RESEARCH_UNAVAILABLE_STATUS = re.compile(
    r"\b(?:unavailable|not\s+available|absence\s+of|without|"
    r"blocked|cannot\s+be\s+(?:validated|obtained|collected)|"
    r"no\s+(?:authorized\s+)?responsive)\b",
    re.IGNORECASE,
)


def research_has_superseded_temple_status(text: str) -> bool:
    """Return true only for the stale device-status premise, not BLE terminology."""

    for block in re.split(r"\n\s*\n", text):
        if "**Superseded temple-status premise:**" in block:
            continue
        normalized = " ".join(block.split())
        if RESEARCH_FAILURE_TERM.search(normalized):
            return True
        if (
            RESEARCH_RIGHT_TEMPLE.search(normalized)
            and RESEARCH_UNAVAILABLE_STATUS.search(normalized)
        ):
            return True
    return False


def unqualified_research_records(paths: Sequence[Path]) -> list[str]:
    """List research records that repeat the premise without the exact banner."""

    offenders = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if (
            research_has_superseded_temple_status(text)
            and RESEARCH_SUPERSESSION_NOTE not in text
        ):
            offenders.append(path.name)
    return offenders


class HardwareValidationPolicyTests(unittest.TestCase):
    def test_policy_records_supersession_and_future_gate(self) -> None:
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("charging case being bumped", policy)
        self.assertIn("Multiple successful firmware flashing", policy)
        self.assertIn("evenRealities-webflasher", policy)
        self.assertIn(DEFERRED, policy)
        self.assertIn("future gates", policy)
        self.assertIn("must not be treated as current device status", policy)

    def test_high_risk_handoffs_record_the_user_correction(self) -> None:
        for path in (HISTORICAL_HANDOFF, PRODUCT_COMMON, PT_FONT_CRC):
            with self.subTest(path=path.relative_to(G2_ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn("charging case being bumped during lunch", text)
                self.assertIn("multiple successful firmware flashing", text)
                self.assertIn("evenRealities-webflasher", text)
                self.assertIn(DEFERRED, text)

    def test_current_machine_and_public_outputs_reject_the_stale_premise(self) -> None:
        current_files = sorted(TOOLS.glob("analyze_g2_*.py"))
        current_files += sorted(MANIFESTS.glob("*.tsv"))
        current_files += sorted(MANIFESTS.glob("*.json"))
        current_files += sorted(COMPONENTS.glob("**/EVIDENCE.md"))
        current_files += sorted(COMPONENTS.glob("**/NOTICE.md"))
        current_files += list(CURRENT_SOURCE_POLICY_SURFACES)
        self.assertTrue(all(path.is_file() for path in current_files))
        offenders = {}
        for path in current_files:
            matches = sorted(set(STALE_PREMISE.findall(path.read_text(encoding="utf-8"))))
            if matches:
                offenders[path.relative_to(G2_ROOT).as_posix()] = matches
        self.assertEqual(offenders, {})

    def test_machine_qualification_status_is_exactly_deferred(self) -> None:
        source_values = []
        patterns = (
            re.compile(r'["\x27]hardware_validation["\x27]\s*:\s*["\x27]([^"\x27]+)'),
            re.compile(r'hardware_validation["\x27]\]\s*!=\s*["\x27]([^"\x27]+)'),
        )
        for path in sorted(TOOLS.glob("analyze_g2_*.py")):
            text = path.read_text(encoding="utf-8")
            for pattern in patterns:
                source_values.extend(
                    (path.relative_to(G2_ROOT).as_posix(), value)
                    for value in pattern.findall(text)
                )
        self.assertTrue(source_values)
        self.assertEqual(
            [
                (path, value)
                for path, value in source_values
                if value != DEFERRED and not value.startswith("not-applicable")
            ],
            [],
        )

        manifest_values = []
        for path in sorted(MANIFESTS.glob("*.tsv")):
            for line in path.read_text(encoding="utf-8").splitlines():
                fields = line.split("\t")
                if fields[0] == "hardware_validation" and not fields[1].startswith(
                    "not-applicable"
                ):
                    manifest_values.append(
                        (path.relative_to(G2_ROOT).as_posix(), fields[1])
                    )
        self.assertTrue(manifest_values)
        self.assertEqual(
            [(path, value) for path, value in manifest_values if value != DEFERRED],
            [],
        )

    def test_live_project_provenance_matches_mit_source_and_deferred_status(self) -> None:
        for provenance in LIVE_PROJECT_PROVENANCE:
            with self.subTest(path=provenance.relative_to(G2_ROOT)):
                with provenance.open(encoding="utf-8", newline="") as handle:
                    rows = list(csv.DictReader(handle, delimiter="\t"))
                project_rows = [
                    row for row in rows if row["source"] == "OpenCFW implementation"
                ]
                self.assertEqual(len(project_rows), 1)
                row = project_rows[0]
                source = G2_ROOT / row["path"]
                body = source.read_bytes()
                self.assertEqual(int(row["bytes"]), len(body))
                self.assertEqual(row["sha256"], hashlib.sha256(body).hexdigest())
                self.assertEqual(row["license"], "MIT")
                self.assertIn(DEFERRED, row["qualification"])
                self.assertNotIn("blocked", row["qualification"].lower())

    def test_historical_audits_locally_supersede_the_temple_status_premise(self) -> None:
        research_docs = sorted((DOCS / "research").glob("*.md"))
        corrected = [
            path
            for path in research_docs
            if RESEARCH_SUPERSESSION_NOTE in path.read_text(encoding="utf-8")
        ]
        self.assertTrue(corrected)
        self.assertEqual(unqualified_research_records(research_docs), [])
        docs_index = (DOCS / "README.md").read_text(encoding="utf-8")
        self.assertIn("hardware-validation-policy.md", docs_index)
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("historical per-closure audit records", policy)
        self.assertIn("retained as an evidence chronology", policy)
        self.assertIn("must not be treated as current device status", policy)

    def test_research_lint_rejects_unqualified_recurrence_but_allows_banner(self) -> None:
        stale = "The authorized right temple is nonresponsive."
        self.assertTrue(research_has_superseded_temple_status(stale))
        self.assertFalse(
            research_has_superseded_temple_status(
                "The BLE peer disconnected after HCI_Disconnect; retry is implemented."
            )
        )
        self.assertFalse(
            research_has_superseded_temple_status(RESEARCH_SUPERSESSION_NOTE)
        )
        with tempfile.TemporaryDirectory() as tmp:
            record = Path(tmp) / "historical.md"
            record.write_text(
                RESEARCH_SUPERSESSION_NOTE + "\n\n" + stale + "\n",
                encoding="utf-8",
            )
            self.assertEqual(unqualified_research_records([record]), [])
            record.write_text(stale + "\n", encoding="utf-8")
            self.assertEqual(
                unqualified_research_records([record]), ["historical.md"]
            )

    def test_current_reference_docs_do_not_repeat_the_stale_premise(self) -> None:
        reference_docs = (
            DOCS / "functional-capability-ledger.md",
            DOCS / "progress.md",
            DOCS / "source-coverage.md",
            DOCS / "upstream-inventory.md",
        )
        offenders = {
            path.name: sorted(set(CURRENT_REFERENCE_STALE.findall(path.read_text(encoding="utf-8"))))
            for path in reference_docs
            if CURRENT_REFERENCE_STALE.search(path.read_text(encoding="utf-8"))
        }
        self.assertEqual(offenders, {})
        upstream = (DOCS / "upstream-inventory.md").read_text(encoding="utf-8")
        self.assertIn("zero unclassified bytes", upstream)
        self.assertIn("Historical “opaque” counts", upstream)
        self.assertNotIn("The remaining opaque bytes are", upstream)


if __name__ == "__main__":
    unittest.main()
