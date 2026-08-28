#!/usr/bin/env python3
"""Fail closed when the superseded G2 hardware premise reappears."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


G2_ROOT = Path(__file__).resolve().parents[1]
TOOLS = G2_ROOT / "tools"
MANIFESTS = TOOLS / "manifests"
DOCS = G2_ROOT / "docs"
POLICY = DOCS / "hardware-validation-policy.md"

DEFERRED = "deferred by project direction"
STALE_PREMISE = re.compile(
    r"nonresponsive|unresponsive|unavailable\s+hardware|hardware\s+unavailable|"
    r"blocked\s+by\s+unavailable\s+physical\s+evidence|"
    r"unavailable\s+authorized|no\s+responsive\s+authorized|"
    r"no\s+authorized[^\n.]{0,160}\bavailable\b|physically\s+available",
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
    + r"|absence\s+of\s+an\s+authorized\s+responsive",
    re.IGNORECASE,
)


class HardwareValidationPolicyTests(unittest.TestCase):
    def test_policy_records_supersession_and_future_gate(self) -> None:
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("charging case being bumped", policy)
        self.assertIn(DEFERRED, policy)
        self.assertIn("future gates", policy)
        self.assertIn("must not be treated as current device status", policy)

    def test_current_machine_outputs_reject_the_stale_premise(self) -> None:
        current_files = sorted(TOOLS.glob("analyze_g2_*.py"))
        current_files += sorted(MANIFESTS.glob("*.tsv"))
        current_files += sorted(MANIFESTS.glob("*.json"))
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

    def test_historical_audits_are_centrally_superseded_without_rewriting(self) -> None:
        stale_audits = []
        for path in sorted((DOCS / "research").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            if STALE_PREMISE.search(text):
                stale_audits.append(path)
        self.assertTrue(stale_audits)
        docs_index = (DOCS / "README.md").read_text(encoding="utf-8")
        self.assertIn("hardware-validation-policy.md", docs_index)
        policy = POLICY.read_text(encoding="utf-8")
        self.assertIn("historical per-closure audit records", policy)
        self.assertIn("retained as an evidence chronology", policy)
        self.assertIn("must not be treated as current device status", policy)

    def test_current_reference_docs_do_not_repeat_the_stale_premise(self) -> None:
        reference_docs = (
            DOCS / "functional-capability-ledger.md",
            DOCS / "progress.md",
            DOCS / "source-coverage.md",
        )
        offenders = {
            path.name: sorted(set(CURRENT_REFERENCE_STALE.findall(path.read_text(encoding="utf-8"))))
            for path in reference_docs
            if CURRENT_REFERENCE_STALE.search(path.read_text(encoding="utf-8"))
        }
        self.assertEqual(offenders, {})


if __name__ == "__main__":
    unittest.main()
