#!/usr/bin/env python3
"""Fail-closed source/build closure for the G2 touch I2C protocol."""

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
SOURCE = ROOT / "components/shared/touch/runtime_touch_i2c_protocol.c"
HEADER = ROOT / "components/shared/touch/runtime_touch_i2c_protocol.h"
EVIDENCE_ANALYZER = ROOT / "tools/analyze_g2_touch_i2c_protocol.py"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_touch.bin"
PINS = {
    SOURCE: (7307, "863728a0011c1518930971068e8360b3ab7ce458fcd8eca879fdf767b61f2bb0"),
    HEADER: (2787, "b1a4407b8c383295dac410bc6b54169261c5e867e272470f790f39fc578e2893"),
}
EXPORTS = {
    "open_cfw_touch_build_report", "open_cfw_touch_dispatch_event",
    "open_cfw_touch_fifo_arm", "open_cfw_touch_fifo_position",
    "open_cfw_touch_handle_command", "open_cfw_touch_power_mode_valid",
    "open_cfw_touch_protocol_init", "open_cfw_touch_tx_complete",
}


class AuditError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def load_evidence():
    spec = importlib.util.spec_from_file_location("g2_touch_i2c_for_source", EVIDENCE_ANALYZER)
    require(spec is not None and spec.loader is not None, "cannot load evidence analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def defined_symbols(nm: str, obj: Path) -> set[str]:
    output = subprocess.run([nm, "-g", str(obj)], check=True, capture_output=True, text=True).stdout
    result = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-2].upper() in {"T", "W"}:
            result.add(fields[-1])
    return result


def audit() -> dict:
    for path, (size, digest) in PINS.items():
        data = path.read_bytes()
        require(len(data) == size, f"size changed: {path.relative_to(ROOT)}")
        require(hashlib.sha256(data).hexdigest() == digest,
                f"SHA-256 changed: {path.relative_to(ROOT)}")

    evidence = load_evidence()
    original = evidence.audit(BLOB.read_bytes())
    require(len(original["checks"]) == 6 and
            all(item["result"] == "pass" for item in original["checks"]),
            "authenticated protocol evidence changed")
    require(len(evidence.COMMANDS) == 9, "command inventory changed")
    require(sum(item[1] is not None for item in evidence.COMMANDS) == 7,
            "linked command body inventory changed")

    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    require(clang is not None, "clang unavailable")
    require(nm is not None, "nm unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-i2c-source-") as raw:
        obj = Path(raw) / "touch.o"
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
        symbols = defined_symbols(nm, obj)
        require(symbols == EXPORTS, f"target exports changed: {sorted(symbols)}")

    return {
        "component": "G2 touch-controller I2C command/report protocol",
        "analysis_mode": "offline authenticated-evidence/source/build audit; no hardware, I2C, reset, signing, or flash operation",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "target": "thumbv6m-none-eabi / Cortex-M0+ / Thumb",
        "exports": sorted(EXPORTS),
        "implemented_contracts": [
            "1..16-byte RX validation and command 0..8 dispatch",
            "seven recovered command bodies plus fail-closed slots 7 and 8",
            "16-byte reply/report framing and active-low attention lifecycle",
            "proximity-baseline persistence threshold greater than 49",
            "long-press validation and dirty-state propagation",
            "sensor report, event 0..7, FIFO, timeout, and power-mode policies",
            "callback-only DFU mailbox/reset handoff",
        ],
        "hardware_block": {
            "physical_evidence_available": False,
            "required_evidence": "authorized responsive G2 touch controller plus I2C/GPIO trace validating resident command table order, IRQ/HAL descriptors, attention timing, sensor reports, EEPROM, sleep, and DFU reset handoff",
            "shipped_prefix_retained": True,
        },
        "proprietary_block": {
            "resident_region": "flash >=0x8680",
            "unavailable_inputs": ["resident command/event/SROM switch tables", "resident HAL descriptors", "resident boot and DFU engine"],
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
        print(f"Touch I2C closure: {report['status']}")
        print(f"  target exports: {len(report['exports'])}")
        print("  resident table/DFU evidence: unavailable; shipped prefix retained")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Touch I2C source audit failed: {exc}") from exc
