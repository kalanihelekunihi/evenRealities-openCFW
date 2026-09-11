#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Target-build and package qualification for the EM9305 tail overlay."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "components/em9305/source_overlay/build_overlay.py"
RECORD_PATH = ROOT / "components/em9305/source_image/record_package.py"
STOCK_PATH = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
DOCKER_IMAGE = "opencfw-arc-toolchain:fedora44"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RECORDS = load_module("em9305_overlay_record_package", RECORD_PATH)
BUILDER = load_module("em9305_reconstructible_tail_builder", BUILDER_PATH)


def _native_toolchain() -> dict[str, str] | None:
    """Resolve the same OPENCFW_ARC_* toolchain build_overlay.py would use.

    Returns None if none of an explicit override, the pinned macOS cache
    (see toolchain/fetch_arc_toolchain.sh), or an arc-linux-gnu-* toolchain
    on PATH is available.
    """
    tools = {
        name: BUILDER._default_tool(name, f"OPENCFW_ARC_{name.upper()}")
        for name in ("gcc", "nm", "objcopy", "objdump", "readelf")
    }
    for tool in tools.values():
        resolved = tool if Path(tool).is_absolute() else shutil.which(tool)
        if not resolved:
            return None
    return tools


def _docker_toolchain() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = subprocess.run(
        ["docker", "image", "inspect", DOCKER_IMAGE],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return probe.returncode == 0


class EM9305ReconstructibleTailOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (ROOT / "build").mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="em9305-tail-test-", dir=ROOT / "build"
        )
        cls.output = Path(cls.temporary.name)

        tools = _native_toolchain()
        if tools is not None:
            cls.report = BUILDER.build(
                gcc=tools["gcc"], nm=tools["nm"], objcopy=tools["objcopy"],
                objdump=tools["objdump"], readelf=tools["readelf"],
                output_dir=cls.output,
            )
            disassembly = subprocess.run(
                [tools["objdump"], "-d", str(cls.output / "reconstructible_tail.elf")],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            cls.disassembly = disassembly.stdout
        elif _docker_toolchain():
            relative_output = cls.output.relative_to(ROOT)
            command = [
                "docker", "run", "--rm",
                "-v", f"{ROOT}:/work", "-w", "/work", DOCKER_IMAGE,
                "python3", "components/em9305/source_overlay/build_overlay.py",
                "--gcc", "/usr/bin/arc-linux-gnu-gcc",
                "--nm", "/usr/bin/arc-linux-gnu-nm",
                "--objcopy", "/usr/bin/arc-linux-gnu-objcopy",
                "--output-dir", relative_output.as_posix(),
            ]
            subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
            cls.report = json.loads((cls.output / "build-report.json").read_text())
            disassembly = subprocess.run(
                [
                    "docker", "run", "--rm", "-v", f"{ROOT}:/work", "-w", "/work",
                    DOCKER_IMAGE, "/usr/bin/arc-linux-gnu-objdump", "-d",
                    f"/work/{relative_output.as_posix()}/reconstructible_tail.elf",
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            cls.disassembly = disassembly.stdout
        else:
            raise unittest.SkipTest(
                "no ARC toolchain is available: install "
                "components/em9305/source_overlay/toolchain/fetch_arc_toolchain.sh "
                f"or provide the {DOCKER_IMAGE} Docker image"
            )

        cls.provider = (cls.output / "firmware_ble_em9305.bin").read_bytes()
        cls.stock = STOCK_PATH.read_bytes()
        cls.parsed = RECORDS.parse_package(cls.provider)
        cls.stock_parsed = RECORDS.parse_package(cls.stock)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_provider_identity_and_disjoint_accounting_are_pinned(self) -> None:
        self.assertEqual(len(self.provider), 212_984)
        self.assertEqual(
            hashlib.sha256(self.provider).hexdigest(),
            "56694060c0d2761c2004581d0cec97cdb8642c1ff44675194d05d605bf8dd9c7",
        )
        accounting = self.report["accounting"]
        self.assertEqual(
            accounting,
            {
                "production_source_bytes": 1_190,
                "generated_or_reconstructible_bytes": 1_210,
                "candidate_source_not_routed_bytes": 0,
                "typed_retained_or_external_bytes": 210_584,
                "unclassified_bytes": 0,
            },
        )
        self.assertEqual(sum(accounting.values()), len(self.provider))
        self.assertTrue(self.report["production_routed"])
        self.assertEqual(
            self.report["hardware_validation"],
            "blocked by unavailable physical evidence",
        )

    def test_only_authenticated_application_spans_and_sector_tail_change(self) -> None:
        self.assertEqual(self.parsed.records[:3], self.stock_parsed.records[:3])
        application = self.parsed.records[3]
        stock_application = self.stock_parsed.records[3]
        self.assertEqual(application.address, 0x00302400)
        self.assertEqual(len(application.payload), len(stock_application.payload) + 1_036)
        mutable = [
            (address - application.address, address - application.address + allocation)
            for _section, address, allocation in BUILDER.ENTRY_PATCHES
        ]
        mutable.extend(
            (address - application.address, address - application.address + size)
            for address, size in BUILDER.META_ISLANDS
        )
        for offset, (before, after) in enumerate(
            zip(stock_application.payload, application.payload)
        ):
            if before != after:
                self.assertTrue(
                    any(start <= offset < end for start, end in mutable),
                    f"unexpected stock-prefix mutation at application offset 0x{offset:x}",
                )
        self.assertEqual(
            application.address + len(application.payload),
            self.report["application"]["source_end_exclusive"],
        )
        self.assertEqual(
            self.report["application"]["metaware_implementation_bytes"], 748
        )
        self.assertLessEqual(
            self.report["application"]["source_end_exclusive"],
            self.report["application"]["sector_end_exclusive"],
        )

    def test_all_entry_wrappers_are_exact_branches_to_c_implementations(self) -> None:
        rows = self.report["entry_patches"]
        self.assertEqual(len(rows), 23)
        allocation_by_section = {
            section: allocation for section, _address, allocation in BUILDER.ENTRY_PATCHES
        }
        for row in rows:
            section = row["section"]
            suffix = section.removeprefix(".tail_")
            with self.subTest(section=section):
                # The compiled wrapper is always at least a single four-byte
                # tail branch; some entries additionally carry a compiler-
                # emitted narrow-argument extension ahead of it (see
                # toolchain/TOOLCHAIN.md).  Either way it must still fit the
                # entry's authenticated stock allocation.
                self.assertGreaterEqual(row["source_bytes"], 4)
                self.assertEqual(row["source_bytes"] % 2, 0)
                self.assertLessEqual(row["source_bytes"], allocation_by_section[section])
                self.assertIn(f"Disassembly of section {section}:", self.disassembly)
                self.assertIn(f"_{suffix}_impl>", self.disassembly)
        self.assertEqual(self.report["undefined_symbols"], [])

    def test_metaware_public_entries_branch_to_packaged_c_bodies(self) -> None:
        rows = self.report["metaware_entry_patches"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            with self.subTest(section=row["section"]):
                self.assertEqual(row["source_bytes"], 4)
                self.assertIn(
                    f"Disassembly of section {row['section']}:", self.disassembly
                )
                self.assertIn(f"<{row['target']}>", self.disassembly)
        self.assertEqual(
            self.report["metaware_interior_entries_replaced_with_generated_nops"],
            [0x003026A8, 0x00302844],
        )

    def test_direct_c_noops_reproduce_authenticated_stock_bytes(self) -> None:
        rows = self.report["direct_c_noops"]
        self.assertEqual(sum(row["allocation_bytes"] for row in rows), 16)
        stock_application = self.stock_parsed.records[3]
        application = self.parsed.records[3]
        for row in rows:
            offset = row["address"] - application.address
            size = row["allocation_bytes"]
            with self.subTest(section=row["section"]):
                self.assertEqual(
                    application.payload[offset:offset + size],
                    stock_application.payload[offset:offset + size],
                )
                self.assertEqual(
                    hashlib.sha256(application.payload[offset:offset + size]).hexdigest(),
                    row["sha256"],
                )


if __name__ == "__main__":
    unittest.main()
