from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_bootloader_opaque_frontier.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
CENSUS = ROOT / "tools/manifests/g2-bootloader-opaque-frontier.tsv"
BOUNDARY = (
    ROOT / "research/admission/bootloader_opaque_frontier/"
    "runtime_bootloader_qsort_boundary.c"
)
HEADER = BOUNDARY.with_suffix(".h")


class Boundary(ctypes.Structure):
    _fields_ = (
        ("core_start", ctypes.c_uint32),
        ("core_end", ctypes.c_uint32),
        ("wrapper_start", ctypes.c_uint32),
        ("wrapper_end", ctypes.c_uint32),
        ("direct_caller", ctypes.c_uint32),
        ("comparator_pointer", ctypes.c_uint32),
        ("record_width", ctypes.c_uint32),
        ("core_sha256", ctypes.c_char_p),
        ("wrapper_sha256", ctypes.c_char_p),
        ("provider_family", ctypes.c_char_p),
        ("license_status", ctypes.c_char_p),
        ("status", ctypes.c_int),
    )


class BootloaderOpaqueFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("CC") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("clang is required")
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-boot-frontier-")
        cls.output = Path(cls.temporary.name)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_census_selects_largest_complete_actionable_frontier(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "superseded-by-exact-source-admission")
        self.assertEqual(
            report["selected_frontier"],
            {
                "bytes": 728,
                "core_bytes": 704,
                "end": 0x00423D20,
                "sole_public_caller": 0x0041FA22,
                "start": 0x00423A48,
                "wrapper_bytes": 24,
            },
        )
        self.assertEqual(
            report["census"],
            {
                "earliest_complete_opaque_body_bytes": 570,
                "post_mspi_parent_region_bytes": 57153,
                "sequential_parent_region_bytes": 9190,
            },
        )
        self.assertTrue(report["production"]["routed"])
        self.assertFalse(report["production"]["official_bytes_retained"])
        self.assertEqual(report["production"]["local_successor"], {
            "start": 0x00423D20,
            "end": 0x00423D58,
            "address_status": "source_compiled",
        })
        self.assertEqual(report["hardware_operations"], [])

    def test_typed_boundary_compiles_and_fails_closed(self) -> None:
        library = self.output / (
            "qsort-boundary.dylib" if sys.platform == "darwin" else "qsort-boundary.so"
        )
        command = [
            self.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(BOUNDARY),
        ]
        command += (["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"])
        command += ["-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        loaded = ctypes.CDLL(str(library))
        loaded.open_cfw_bootloader_qsort_boundary.restype = ctypes.POINTER(Boundary)
        descriptor = loaded.open_cfw_bootloader_qsort_boundary().contents
        loaded.open_cfw_bootloader_qsort_admission_status.restype = ctypes.c_int
        self.assertEqual(loaded.open_cfw_bootloader_qsort_admission_status(), 1)
        self.assertEqual(
            (descriptor.core_start, descriptor.core_end,
             descriptor.wrapper_start, descriptor.wrapper_end),
            (0x00423A48, 0x00423D08, 0x00423D08, 0x00423D20),
        )
        self.assertEqual(descriptor.direct_caller, 0x0041FA22)
        self.assertEqual(descriptor.comparator_pointer, 0x0041F9F1)
        self.assertEqual(descriptor.record_width, 8)
        self.assertIn(b"IAR DLIB", descriptor.provider_family)
        self.assertIn(b"redistribution authority unresolved", descriptor.license_status)
        self.assertEqual(descriptor.status, 1)

        target = self.output / "qsort-boundary.o"
        subprocess.run(
            [
                self.clang, "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                "-mthumb", "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
                "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-Wall", "-Wextra", "-Werror", "-c", str(BOUNDARY),
                "-o", str(target),
            ],
            check=True, capture_output=True, text=True,
        )
        self.assertGreater(target.stat().st_size, 0)

    def test_raw_body_and_census_mutations_fail_closed(self) -> None:
        mutated_image = self.output / "mutated-bootloader.bin"
        payload = bytearray(OFFICIAL.read_bytes())
        payload[0x00423A48 - 0x00410000 + 12] ^= 0x01
        mutated_image.write_bytes(payload)
        failed = subprocess.run(
            [sys.executable, str(ANALYZER), "--official", str(mutated_image)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("official bootloader pin changed", failed.stderr)

        mutated_census = self.output / "mutated-census.tsv"
        mutated_census.write_text(
            CENSUS.read_text(encoding="utf-8").replace("\t704\t", "\t702\t", 1),
            encoding="utf-8",
        )
        failed = subprocess.run(
            [sys.executable, str(ANALYZER), "--census", str(mutated_census)],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("file pin changed", failed.stderr)

    def test_license_and_superseded_boundary_are_explicit(self) -> None:
        source = BOUNDARY.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        census = CENSUS.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", source)
        self.assertIn("SPDX-License-Identifier: MIT", header)
        self.assertIn("EXACT_PROVIDER_UNSUPPORTED", source + header)
        self.assertIn("source_owned_production\topenCFW clean-room exact in-place source\tGPL-3.0-or-later", census)
        self.assertIn("Even first-party bootloader body\tredistribution authority unresolved", census)
        overlay = (ROOT / "components/bootloader/core_overlay/overlay.json").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("runtime_bootloader_qsort_boundary", overlay)


if __name__ == "__main__":
    unittest.main()
