# SPDX-License-Identifier: MIT
"""Skip a test module when the locally authorized official payloads are absent.

The official Even Realities payloads are not tracked (see
blobs/official/g2-2.2.6.10/PROVENANCE.md). Tests that read them call
require() at import time, so that a checkout without the payloads reports
them as skipped rather than erroring.
"""

from pathlib import Path
import unittest

OFFICIAL = Path(__file__).resolve().parents[1] / "blobs/official/g2-2.2.6.10"


def require(*names: str) -> None:
    missing = [name for name in names if not (OFFICIAL / name).is_file()]
    if missing:
        raise unittest.SkipTest(
            "official payloads not present: " + ", ".join(missing)
            + " (see blobs/official/g2-2.2.6.10/PROVENANCE.md)"
        )
