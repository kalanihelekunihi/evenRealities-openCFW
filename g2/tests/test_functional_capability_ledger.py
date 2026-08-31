# SPDX-License-Identifier: MIT
"""Keep the capability-ledger summary derived from its detailed rows."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs/functional-capability-ledger.md"
DOMAINS = (
    "Protocol",
    "Security",
    "Platform",
    "Health",
    "System",
    "Storage",
    "Sensors",
    "Hardware services",
    "Deployment",
)
STATUSES = (
    "implemented-in-source",
    "software-gap",
    "hardware-dependent",
    "proprietary-blocked",
)
STATUS_ALIASES = {
    "authenticated donor retained / hardware-deferred": "proprietary-blocked",
    "external-provider/proprietary-blocked": "proprietary-blocked",
}


def markdown_fields(line: str) -> list[str]:
    return [field.strip() for field in line.strip().strip("|").split("|")]


def detailed_counts(text: str, domain: str) -> Counter[str]:
    start = text.index(f"## {domain}\n")
    next_heading = text.find("\n## ", start + 4)
    section = text[start:next_heading if next_heading >= 0 else len(text)]
    result: Counter[str] = Counter()
    for line in section.splitlines():
        if not line.startswith("|") or line.startswith("| ---"):
            continue
        fields = markdown_fields(line)
        if len(fields) < 2 or fields[1] == "Gap status":
            continue
        matches = [status for status in STATUSES if fields[1].startswith(status)]
        if fields[1] in STATUS_ALIASES:
            matches = [STATUS_ALIASES[fields[1]]]
        if len(matches) != 1:
            raise AssertionError(
                f"{domain} capability has an uncounted status: {fields[1]!r}"
            )
        result[matches[0]] += 1
    return Counter({status: result[status] for status in STATUSES})


class FunctionalCapabilityLedgerTests(unittest.TestCase):
    def test_summary_counts_equal_detailed_rows(self) -> None:
        text = LEDGER.read_text(encoding="utf-8")
        start = text.index("## Row counts\n")
        end = text.index("\n## Protocol\n", start)
        summary = {}
        for line in text[start:end].splitlines():
            if not line.startswith("|") or line.startswith("| ---"):
                continue
            fields = markdown_fields(line)
            if not fields or fields[0] not in DOMAINS:
                continue
            self.assertEqual(len(fields), 5)
            summary[fields[0]] = Counter(
                {status: int(value) for status, value in zip(STATUSES, fields[1:])}
            )

        self.assertEqual(tuple(summary), DOMAINS)
        for domain in DOMAINS:
            self.assertEqual(summary[domain], detailed_counts(text, domain), domain)

        totals = sum((summary[domain] for domain in DOMAINS), Counter())
        self.assertGreater(totals["implemented-in-source"], 0)
        self.assertEqual(sum(totals.values()), sum(sum(row.values()) for row in summary.values()))


if __name__ == "__main__":
    unittest.main()
