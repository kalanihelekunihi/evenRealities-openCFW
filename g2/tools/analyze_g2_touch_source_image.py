#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed aggregate build/link/package admission for the G2 Touch image."""

from __future__ import annotations

import argparse
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "components/touch/source_image/build_image.py"
MANIFEST = ROOT / "tools/manifests/g2-touch-source-image-summary.json"
NM = Path("/opt/homebrew/opt/llvm/bin/llvm-nm")
EXPECTED_UNITS = 31
EXPECTED_OPEN_CFW_GLOBALS = 176
REQUIRED_SYMBOLS = {
    "Reset_Handler", "HardFault_Handler", "SCB1_IRQHandler",
    "MSCLP_IRQHandler", "open_cfw_touch_firmware_main",
    "open_cfw_touch_firmware_service_command",
    "open_cfw_touch_firmware_publish", "open_cfw_touch_protocol_init",
    "open_cfw_touch_handle_command", "open_cfw_touch_msc_scan",
    "open_cfw_touch_eeprom_write", "open_cfw_touch_product_09b4_run",
    "open_cfw_touch_runtime_0164_reset", "__aeabi_uidiv",
    "__aeabi_uidivmod", "__aeabi_memclr4",
}


class AuditError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def load_builder():
    spec = importlib.util.spec_from_file_location("g2_touch_source_builder", BUILDER)
    require(spec is not None and spec.loader is not None,
            "cannot import Touch source-image builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze() -> dict:
    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="g2-touch-source-admission-") as directory:
        output = Path(directory)
        build = builder.build(output)
        elf = output / build["elf"]["path"]
        raw = (output / build["raw"]["path"]).read_bytes()
        fwpk = (output / build["fwpk"]["path"]).read_bytes()
        nm_tool = str(NM) if NM.is_file() else "llvm-nm"
        lines = subprocess.run(
            [nm_tool, "-g", "--defined-only", str(elf)], check=True,
            text=True, capture_output=True).stdout.splitlines()
        symbols = {line.split()[-1] for line in lines if line.split()}
        open_cfw_globals = {name for name in symbols
                            if name.startswith("open_cfw_touch_")}
        undefined = subprocess.run(
            [nm_tool, "-u", str(elf)], check=True, text=True,
            capture_output=True).stdout.strip()

        require(build["source_translation_units"] == EXPECTED_UNITS,
                "Touch source translation-unit inventory changed")
        require(build["undefined_symbols"] == 0 and undefined == "",
                "Touch source ELF retains undefined symbols")
        require(len(open_cfw_globals) == EXPECTED_OPEN_CFW_GLOBALS,
                "Touch linked global surface changed")
        require(REQUIRED_SYMBOLS <= symbols,
                f"Touch linked surface lost symbols: {sorted(REQUIRED_SYMBOLS-symbols)}")
        stack, reset = struct.unpack_from("<II", raw)
        require(stack == 0x20002000 and reset & 1 == 1,
                "Touch vector table is not a valid Cortex-M0+ vector table")
        require(reset < len(raw) and len(raw) <= 65536,
                "Touch reset vector or flash extent is invalid")
        require(fwpk[:4] == b"FWPK" and fwpk[4:8] == bytes.fromhex("01000202"),
                "Touch FWPK identity changed")
        kind, size, offset, checksum = struct.unpack_from("<IIII", fwpk, 16)
        require((kind, size, offset) == (3, len(raw), 0x20),
                "Touch FWPK record layout changed")
        require(builder.crc32c(raw) == checksum,
                "Touch FWPK record checksum mismatch")
        require(struct.unpack_from("<I", raw, len(raw) - 4)[0] ==
                builder.crc32c(raw[:-4]),
                "Touch raw trailing checksum mismatch")

        return {
            "schema_version": 1,
            "component": "G2 Touch source image admission",
            "metrics": {
                "source_translation_units": EXPECTED_UNITS,
                "linked_open_cfw_globals": len(open_cfw_globals),
                "undefined_symbols": 0,
                "elf_bytes": build["elf"]["size"],
                "raw_flash_bytes": len(raw),
                "fwpk_bytes": len(fwpk),
            },
            "artifacts": {
                "elf_sha256": build["elf"]["sha256"],
                "raw_sha256": build["raw"]["sha256"],
                "fwpk_sha256": build["fwpk"]["sha256"],
                "source_inventory": build["source_inventory"],
            },
            "software_link_complete": True,
            "software_package_complete": True,
            "physical_board_services_routed": False,
            "production_routed": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": "blocked by unavailable physical evidence",
            "hardware_operations": [],
        }


def write_manifest(report: dict) -> None:
    MANIFEST.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    report = analyze()
    if args.write_manifest:
        write_manifest(report)
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
    print(json.dumps(report["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as error:
        raise SystemExit(f"Touch source image admission failed: {error}") from error
