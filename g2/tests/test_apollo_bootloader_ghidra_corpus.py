# SPDX-License-Identifier: MIT
"""Gate the Apollo bootloader Ghidra decompilation corpus (XC-009).

Unlike the Apollo main harvest, there is no per-function decompilation
corpus for the bootloader image before this: BL-* items had to disassemble
from the raw blob with no named, bounded functions to anchor on.  This test
authenticates the checked-in harvest that ``tools/harvest_ghidra_decomp.py``
produced from a local, headless-Ghidra-analyzed project over
``blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`` -- it does not need
Ghidra itself and skips if the corpus is absent, matching the rest of the
G2 suite's harvested-evidence tests (see
``tests.test_transparent_source_pipeline.HarvestCorpusTests``, the Apollo
main analog this mirrors).
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "research/corpus/apollo-bootloader/ghidra/decomp"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"

BOOTLOADER_IMAGE_SHA256 = (
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
)
BOOTLOADER_LOAD_ADDRESS = 0x00410000
BOOTLOADER_IMAGE_END = 0x00434477


class BootloaderHarvestCorpusTests(unittest.TestCase):
    """The harvested bootloader decompilation must authenticate itself."""

    @classmethod
    def setUpClass(cls) -> None:
        summary_path = HARVEST / "HARVEST.json"
        if not summary_path.is_file():
            raise unittest.SkipTest("no harvested bootloader decompilation corpus present")
        cls.summary = json.loads(summary_path.read_text(encoding="utf-8"))

    def test_blob_matches_the_pinned_bootloader_image(self) -> None:
        if not BLOB.is_file():
            raise unittest.SkipTest("official bootloader payload is not present")
        actual = hashlib.sha256(BLOB.read_bytes()).hexdigest()
        self.assertEqual(actual, BOOTLOADER_IMAGE_SHA256)
        self.assertEqual(
            BOOTLOADER_IMAGE_END - BOOTLOADER_LOAD_ADDRESS, BLOB.stat().st_size
        )

    def test_every_artifact_matches_its_recorded_digest(self) -> None:
        for name, digest in self.summary["artifacts"].items():
            with self.subTest(artifact=name):
                path = HARVEST / name
                self.assertTrue(path.is_file(), f"{name} is missing")
                actual = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertEqual(actual, digest)

    def test_harvest_targets_the_authenticated_bootloader_payload(self) -> None:
        self.assertEqual(
            self.summary["census"]["executable_sha256"], BOOTLOADER_IMAGE_SHA256
        )
        self.assertEqual(
            self.summary["census"]["program"], "ota_s200_bootloader.bin"
        )

    def test_every_function_decompiled(self) -> None:
        counts = self.summary["counts"]
        self.assertGreater(counts["functions"], 0)
        self.assertEqual(counts["not_decompiled"], 0)
        self.assertEqual(counts["decompiled"], counts["functions"])

    def test_records_and_bodies_agree(self) -> None:
        records = [
            json.loads(line)
            for line in (HARVEST / "functions.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        self.assertEqual(len(records), self.summary["counts"]["functions"])
        self.assertEqual(
            sum(record["body_bytes"] for record in records),
            self.summary["counts"]["function_body_bytes"],
        )
        entries = [int(record["entry"], 16) for record in records]
        self.assertEqual(entries, sorted(entries), "records must be address-ordered")
        self.assertEqual(len(set(entries)), len(entries), "entries must be unique")
        for entry in entries:
            with self.subTest(entry=hex(entry)):
                self.assertGreaterEqual(entry, BOOTLOADER_LOAD_ADDRESS)
                self.assertLess(entry, BOOTLOADER_IMAGE_END)

    def test_body_ranges_account_for_every_body_byte(self) -> None:
        for line in (HARVEST / "functions.jsonl").read_text(
            encoding="utf-8"
        ).splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            spanned = sum(
                int(high, 16) - int(low, 16) + 1 for low, high in record["ranges"]
            )
            with self.subTest(entry=record["entry"]):
                self.assertEqual(spanned, record["body_bytes"])

    def test_named_functions_include_the_reset_and_vector_targets(self) -> None:
        # SeedCortexMVectorTable seeds every distinct in-image vector target
        # as a defined function before analysis; the harvest must retain at
        # least that many bounded entries so BL-* work can name real
        # boundaries instead of guessing at raw offsets.
        records = [
            json.loads(line)
            for line in (HARVEST / "functions.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]
        entries = {int(record["entry"], 16) for record in records}
        # Reset handler is vector[1] of the bootloader's own Cortex-M table
        # at its load address, with the Thumb bit stripped.
        self.assertIn(0x43291A, entries)


if __name__ == "__main__":
    unittest.main()
