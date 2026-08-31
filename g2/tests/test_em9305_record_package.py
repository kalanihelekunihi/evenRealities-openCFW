# SPDX-License-Identifier: MIT
"""Deterministic and fail-closed tests for the EM9305 record package."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components/em9305/source_image"
MODULE_PATH = COMPONENT / "record_package.py"
BUILDER = COMPONENT / "build_image.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"

SPEC = importlib.util.spec_from_file_location("em9305_record_package", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot import EM9305 record-package module")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class Em9305RecordPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock = OFFICIAL.read_bytes()
        cls.parsed = MODULE.parse_package(cls.stock)

    def assertRejected(self, package: bytes) -> None:  # noqa: N802
        with self.assertRaises(MODULE.RecordPackageError):
            MODULE.parse_package(package)

    def test_authenticated_stock_layout_is_exact(self) -> None:
        self.assertEqual(len(self.stock), 211_948)
        self.assertEqual(
            hashlib.sha256(self.stock).hexdigest(),
            "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9",
        )
        self.assertEqual(self.parsed.metadata_size, 124)
        self.assertEqual(self.parsed.payload_size, 211_824)
        self.assertEqual(
            [(record.address, len(record.payload)) for record in self.parsed.records],
            [
                (0x00300000, 224),
                (0x00300400, 656),
                (0x00302000, 56),
                (0x00302400, 210_888),
            ],
        )
        self.assertEqual(
            self.parsed.erase_sectors,
            (0, 0, 1, 1, *range(2, 27)),
        )

    def test_stock_package_rebuild_is_byte_exact(self) -> None:
        rebuilt = MODULE.build_package(
            self.parsed.records, self.parsed.erase_sectors)
        self.assertEqual(rebuilt, self.stock)

    def test_parser_rejects_noncanonical_or_corrupt_packages(self) -> None:
        bad_magic = bytearray(self.stock)
        bad_magic[0] ^= 0xFF
        self.assertRejected(bytes(bad_magic))

        bad_payload_length = bytearray(self.stock)
        struct.pack_into("<I", bad_payload_length, 4, self.parsed.payload_size - 1)
        self.assertRejected(bytes(bad_payload_length))

        noncontiguous = bytearray(self.stock)
        struct.pack_into("<I", noncontiguous, 16, self.parsed.metadata_size + 1)
        self.assertRejected(bytes(noncontiguous))

        empty = bytearray(self.stock)
        struct.pack_into("<I", empty, 20, 0)
        self.assertRejected(bytes(empty))

        target_overlap = bytearray(self.stock)
        struct.pack_into("<I", target_overlap, 16 + 12 + 8, 0x00300080)
        self.assertRejected(bytes(target_overlap))

        nonzero_padding = bytearray(self.stock)
        nonzero_padding[122] = 1
        self.assertRejected(bytes(nonzero_padding))

        self.assertRejected(self.stock[:-1])

    def test_builder_rejects_invalid_source_records_and_sector_ids(self) -> None:
        record = MODULE.Record(0x00300000, b"a")
        invalid_records = (
            (),
            (MODULE.Record(0x00300000, b""),),
            (MODULE.Record(True, b"a"),),
            (MODULE.Record(1 << 32, b"a"),),
            (MODULE.Record(0xFFFFFFFF, b"ab"),),
            (record, MODULE.Record(0x00300000, b"b")),
        )
        for records in invalid_records:
            with self.subTest(records=records):
                with self.assertRaises(MODULE.RecordPackageError):
                    MODULE.build_package(records, ())
        for sectors in ((True,), (-1,), (1 << 16,)):
            with self.subTest(sectors=sectors):
                with self.assertRaises(MODULE.RecordPackageError):
                    MODULE.build_package((record,), sectors)

    def test_cli_build_and_check_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-em9305-package-") as raw:
            directory = Path(raw)
            (directory / "record-a.bin").write_bytes(b"abc")
            (directory / "record-b.bin").write_bytes(b"defg")
            layout = directory / "layout.json"
            layout.write_text(json.dumps({
                "records": [
                    {"address": "0x300000", "path": "record-a.bin"},
                    {"address": 0x300010, "path": "record-b.bin"},
                ],
                "erase_sectors": [0, 1],
            }), encoding="utf-8")
            output = directory / "firmware.bin"
            command = [
                sys.executable, str(BUILDER), "--layout", str(layout),
                "--output", str(output),
            ]
            first = subprocess.run(command, check=True, text=True,
                                   capture_output=True)
            report = json.loads(first.stdout)
            self.assertEqual(report["status"], "em9305-record-package-built")
            self.assertEqual(report["records"], 2)
            built = output.read_bytes()
            subprocess.run(command + ["--check"], check=True, text=True,
                           capture_output=True)
            subprocess.run(command, check=True, text=True, capture_output=True)
            self.assertEqual(output.read_bytes(), built)

    def test_cli_rejects_path_escape_and_boolean_address(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-em9305-layout-") as raw:
            directory = Path(raw)
            output = directory / "firmware.bin"
            for record in (
                {"address": 0x300000, "path": "../outside.bin"},
                {"address": True, "path": "record.bin"},
                {"address": 0x300000, "path": 7},
            ):
                layout = directory / "layout.json"
                layout.write_text(json.dumps({
                    "records": [record], "erase_sectors": [],
                }), encoding="utf-8")
                completed = subprocess.run([
                    sys.executable, str(BUILDER), "--layout", str(layout),
                    "--output", str(output),
                ], text=True, capture_output=True)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("EM9305 source-image build failed", completed.stderr)


if __name__ == "__main__":
    unittest.main()
