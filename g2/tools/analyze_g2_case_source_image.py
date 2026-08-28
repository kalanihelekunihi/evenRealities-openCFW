#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed build/link/package admission for the G2 Case source image."""

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
BUILDER = ROOT / "components/case/source_image/build_image.py"
MANIFEST = ROOT / "tools/manifests/g2-case-source-image-summary.json"
NM = Path("/opt/homebrew/opt/llvm/bin/llvm-nm")
EXPECTED_UNITS = 8
EXPECTED_GLOBALS = 223
REQUIRED = {
    "Reset_Handler", "HardFault_Handler", "__aeabi_uidiv",
    "__aeabi_llsl", "__aeabi_llsr", "open_cfw_case_boot_initialize",
    "open_cfw_case_configure_system_clock", "open_cfw_case_process_frame_byte",
    "open_cfw_case_event_group_set_bits", "open_cfw_case_ota_advance",
}


class AuditError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def load_builder():
    spec = importlib.util.spec_from_file_location("g2_case_source_builder", BUILDER)
    require(spec is not None and spec.loader is not None,
            "cannot import Case source-image builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze() -> dict:
    builder = load_builder()
    with tempfile.TemporaryDirectory(prefix="g2-case-source-admission-") as directory:
        output = Path(directory)
        build = builder.build(output)
        elf = output / build["elf"]["path"]
        raw = (output / build["raw"]["path"]).read_bytes()
        package = (output / build["even"]["path"]).read_bytes()
        nm = str(NM) if NM.is_file() else "llvm-nm"
        lines = subprocess.run([nm, "-g", "--defined-only", str(elf)],
                               check=True, text=True,
                               capture_output=True).stdout.splitlines()
        symbols = {line.split()[-1] for line in lines if line.split()}
        globals_ = {name for name in symbols if name.startswith("open_cfw_case_")}
        undefined = subprocess.run([nm, "-u", str(elf)], check=True, text=True,
                                   capture_output=True).stdout.strip()
        require(build["source_translation_units"] == EXPECTED_UNITS,
                "Case source translation-unit inventory changed")
        require(undefined == "" and build["undefined_symbols"] == 0,
                "Case source ELF retains undefined symbols")
        require(len(globals_) == EXPECTED_GLOBALS,
                "Case linked global surface changed")
        require(REQUIRED <= symbols,
                f"Case linked surface lost symbols: {sorted(REQUIRED-symbols)}")
        stack, reset = struct.unpack_from("<II", raw)
        require(stack == 0x20002C88 and reset & 1 == 1,
                "Case vector table is invalid")
        require(0x08000000 <= reset < 0x08000000 + len(raw),
                "Case reset vector escapes the raw image")
        require(package[:4] == b"EVEN" and package[4:8] == bytes((1, 2, 57, 0)),
                "Case EVEN identity changed")
        length, checksum = struct.unpack_from(">II", package, 8)
        require(length == len(raw) and package[16:32] == bytes(16),
                "Case EVEN layout changed")
        calculated = sum(struct.unpack(f">{len(raw)//4}I", raw)) & 0xFFFFFFFF
        require(checksum == calculated, "Case EVEN checksum mismatch")
        return {
            "schema_version": 1,
            "component": "G2 charging-case source image admission",
            "metrics": {
                "source_translation_units": EXPECTED_UNITS,
                "linked_open_cfw_globals": len(globals_),
                "undefined_symbols": 0,
                "elf_bytes": build["elf"]["size"],
                "raw_flash_bytes": len(raw),
                "even_package_bytes": len(package),
                "covered_function_frontier": 222,
            },
            "artifacts": {
                "elf_sha256": build["elf"]["sha256"],
                "raw_sha256": build["raw"]["sha256"],
                "even_sha256": build["even"]["sha256"],
                "source_inventory": build["source_inventory"],
            },
            "software_link_complete": True,
            "software_package_complete": True,
            "physical_board_services_routed": False,
            "production_routed": False,
            "hardware_validation": "deferred by project direction",
            "hardware_blocker": "deferred by project direction",
            "hardware_operations": [],
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    report = analyze()
    if args.write_manifest:
        MANIFEST.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"wrote {MANIFEST.relative_to(ROOT)}")
    print(json.dumps(report["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as error:
        raise SystemExit(f"Case source image admission failed: {error}") from error
