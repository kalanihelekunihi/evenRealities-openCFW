#!/usr/bin/env python3
"""Fail-closed source/build closure for G2 touch sensing and gestures."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_touch.bin"
SOURCE = ROOT / "components/shared/touch/runtime_touch_sensing.c"
HEADER = ROOT / "components/shared/touch/runtime_touch_sensing.h"
IDENTITY = ROOT / "tools/analyze_g2_touch_identity.py"
PINS = {
    SOURCE: (4629, "30d7fd3e9c2c9d0a02b1ae4a5737cdf66a17d0f0aebab7b61531326373e9c811"),
    HEADER: (2461, "9fc6c523ba0fa7fa06aa6afb0a46385c326a246e1de4273732e4f8c9ca477f52"),
}
MSC_SPAN = (0x36C4, 0x376C, "5cee0e3336b8a6e052adc77ba845ff2d03d1dd5c9f4926588d523217aa7a13bc")
EXPORTS = {
    "open_cfw_touch_calibration_threshold", "open_cfw_touch_gesture_init",
    "open_cfw_touch_gesture_press", "open_cfw_touch_gesture_release",
    "open_cfw_touch_msc_scan", "open_cfw_touch_power_transition",
}


class AuditError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuditError(message)


def load_identity():
    spec = importlib.util.spec_from_file_location("g2_touch_identity_for_sensing", IDENTITY)
    require(spec is not None and spec.loader is not None, "cannot load identity analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def symbols(nm: str, obj: Path) -> set[str]:
    output = subprocess.run([nm, "-g", str(obj)], check=True, capture_output=True, text=True).stdout
    return {line.split()[-1] for line in output.splitlines()
            if len(line.split()) >= 3 and line.split()[-2].upper() in {"T", "W"}}


def audit() -> dict:
    for path, (size, digest) in PINS.items():
        data = path.read_bytes()
        require(len(data) == size, f"size changed: {path.relative_to(ROOT)}")
        require(hashlib.sha256(data).hexdigest() == digest,
                f"SHA-256 changed: {path.relative_to(ROOT)}")

    identity = load_identity()
    report = identity.audit(BLOB.read_bytes())
    require(all(item["result"] == "pass" for item in report["checks"]),
            "touch identity evidence changed")
    payload = BLOB.read_bytes()[0x20:]
    start, end, digest = MSC_SPAN
    require(hashlib.sha256(payload[start:end]).hexdigest() == digest,
            "authenticated MSC loop changed")
    for offset, value in ((0x376C, 0xC000FFCA), (0x3770, 0x00FF0004),
                          (0x3774, 0x00FF0063), (0x3778, 0x00400064),
                          (0x377C, 0x000006D9)):
        require(struct.unpack_from("<I", payload, offset)[0] == value,
                f"MSC literal changed at {offset:#x}")

    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    require(clang is not None and nm is not None, "target build tools unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-sensing-source-") as raw:
        obj = Path(raw) / "sensing.o"
        subprocess.run([
            clang, "--target=thumbv6m-none-eabi", "-mthumb",
            "-mcpu=cortex-m0plus", "-O2", "-ffreestanding", "-fno-builtin",
            "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
            "-Werror", "-I" + str(SOURCE.parent), "-c", str(SOURCE),
            "-o", str(obj),
        ], cwd=ROOT, check=True, capture_output=True)
        found = symbols(nm, obj)
        require(found == EXPORTS, f"target exports changed: {sorted(found)}")

    return {
        "component": "G2 touch sensing/gesture/calibration policy",
        "analysis_mode": "offline source/build audit; no hardware, sleep, reset, signing, or flash operation",
        "status": "implemented-in-source / hardware validation blocked by unavailable physical evidence",
        "license": "MIT OR GPL-3.0-only",
        "software_gap_count": 0,
        "target": "thumbv6m-none-eabi / Cortex-M0+ / Thumb",
        "exports": sorted(EXPORTS),
        "msc_contract": {
            "stock_span": "[0x36C4,0x376C)",
            "channels": "runtime count, six descriptor words each",
            "selector": "0x06D9",
            "failure_status": 4,
            "maximum_reduction": True,
        },
        "implemented_policy": [
            "ACT->ALR", "ALR->WOT", "WOT->ACT", "WOT->ALR",
            "left/right swipe", "long press", "five fast clicks",
            "saturating calibration threshold",
        ],
        "hardware_block": {
            "physical_evidence_available": False,
            "required_evidence": "authorized responsive touch controller and golden raw MSCLP/gesture/power traces validating channel descriptors, thresholds, direction, click timing, ACT/ALR/WOT timers, sleep, wake, and noise behavior",
            "shipped_touch_application_retained": True,
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
        print(f"Touch sensing closure: {report['status']}")
        print(f"  target exports: {len(report['exports'])}")
        print("  physical MSCLP/gesture traces: unavailable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Touch sensing source audit failed: {exc}") from exc
