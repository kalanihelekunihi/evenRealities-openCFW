#!/usr/bin/env python3
"""Fail-closed source/build closure for the G2 case UART/update protocol."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/case/runtime_case_uart_update.c"
HEADER = ROOT / "components/shared/case/runtime_case_uart_update.h"
EVIDENCE_ANALYZER = ROOT / "tools/analyze_g2_box_stm32g0_platform.py"
PINS = {
    SOURCE: (8450, "68d228d64ad2b4af9c871d61eb0226fcbf484a4d5de0ac701584e8231fa9781c"),
    HEADER: (3560, "400e5bfe549977f02b4487d4a4651fa8a19b5baa03c5bad3fe12b7e8213a390a"),
}
EXPORTS = {
    "open_cfw_case_channel_send_retry",
    "open_cfw_case_frame_checksum",
    "open_cfw_case_frame_find_validate",
    "open_cfw_case_image_be32_sum",
    "open_cfw_case_ota_advance",
    "open_cfw_case_ota_begin",
    "open_cfw_case_parse_ota_offer",
    "open_cfw_case_validate_chunk",
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _defined_symbols(nm: str, obj: Path) -> set[str]:
    output = subprocess.run([nm, "-g", str(obj)], check=True, capture_output=True, text=True).stdout
    found = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-2].upper() in {"T", "W"}:
            found.add(fields[-1])
    return found


def audit() -> dict:
    for path, (size, digest) in PINS.items():
        data = path.read_bytes()
        require(len(data) == size, f"size changed: {path.relative_to(ROOT)}")
        require(hashlib.sha256(data).hexdigest() == digest,
                f"SHA-256 changed: {path.relative_to(ROOT)}")

    evidence = _load(EVIDENCE_ANALYZER, "g2_case_platform_for_source").analyze()
    protocol = evidence["uart_update_protocol"]
    require(protocol["frame_format"]["header_bytes"] == [0x5A, 0xA5, 0xFF, "cmd"],
            "authenticated frame signature changed")
    require(protocol["frame_packer"]["retry_bound"] == 10,
            "authenticated retry bound changed")
    require(len(evidence["ota_state_machine_strings"]) == 22,
            "authenticated OTA step inventory changed")
    require(evidence["identity"]["wrapper"]["checksum_verified"] is True,
            "wrapper checksum evidence changed")

    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    require(clang is not None, "clang unavailable")
    require(nm is not None, "nm unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-case-uart-source-") as raw:
        obj = Path(raw) / "case.o"
        subprocess.run(
            [
                clang, "--target=thumbv6m-none-eabi", "-mthumb",
                "-mcpu=cortex-m0plus", "-O2", "-ffreestanding",
                "-fno-builtin", "-ffunction-sections", "-fdata-sections",
                "-Wall", "-Wextra", "-Werror", "-I" + str(SOURCE.parent),
                "-c", str(SOURCE), "-o", str(obj),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        symbols = _defined_symbols(nm, obj)
        require(symbols == EXPORTS, f"target exports changed: {sorted(symbols)}")

    return {
        "component": "G2 charging-case UART/update protocol",
        "analysis_mode": "offline authenticated-evidence/source/build audit; no hardware, erase, program, bank swap, signing, or flash operation",
        "status": "implemented-in-source / hardware-validation-blocked-by-unavailable-physical-evidence",
        "software_gap_count": 0,
        "target": "thumbv6m-none-eabi / Cortex-M0+ / Thumb",
        "exports": sorted(EXPORTS),
        "implemented_contracts": [
            "5A A5 FF header search in the first four offsets",
            "8-bit additive frame checksum seeded with length-2",
            "32-bit additive big-endian image word sum",
            "bounded nine-attempt channel write matching the stock retry loop",
            "0x58 version/length/checksum offer decode",
            "0x5A nested chunk checksum",
            "dual-bank erase/copy-SN/receive/verify/inform/swap state machine",
        ],
        "hardware_block": {
            "physical_evidence_available": False,
            "required_evidence": "authorized charging case plus UART capture and backed-up bank/SN windows validating RX timeouts, commands, flash erase/program, serial copy-forward, option-byte swap, reset, and glasses acknowledgements",
            "preserved_windows": [
                "0x0803F000..0x0803F00F", "0x0803F800..0x0803F807",
                "0x0807F000..0x0807F00F", "0x0807F800..0x0807F807",
            ],
            "stock_case_payload_retained": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Case UART/update closure: {report['status']}")
        print(f"  target exports: {len(report['exports'])}")
        print("  destructive bank operations: callback-only; physical evidence unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Case UART/update source audit failed: {exc}") from exc
