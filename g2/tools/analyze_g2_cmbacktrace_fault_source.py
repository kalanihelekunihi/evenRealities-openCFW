#!/usr/bin/env python3
"""Fail-closed source/build closure for the G2 CmBacktrace fault path.

This audit proves that the authenticated compatible upstream implementation,
the recovered G2 configuration, and the Cortex-M55 exception-entry shim are
compilable production C.  It deliberately does not register the shim as the
HardFault vector and does not claim physical fault-path validation.
"""

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
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION_ANALYZER = ROOT / "tools/analyze_g2_cmbacktrace_version.py"
SNAPSHOT_VERIFIER = ROOT / "third_party/cmbacktrace/verify_snapshot.py"
UPSTREAM_C = ROOT / "third_party/cmbacktrace/cm_backtrace/cm_backtrace.c"
CONFIG = ROOT / "third_party/cmbacktrace/g2-config/cmb_user_cfg.h"
COMPAT = ROOT / "components/shared/cmbacktrace/target_compat"
ENTRY_C = ROOT / "components/shared/cmbacktrace/runtime_cmbacktrace_fault_entry.c"
ENTRY_H = ROOT / "components/shared/cmbacktrace/runtime_cmbacktrace_fault_entry.h"

FILE_PINS = {
    CONFIG: (1776, "9599205cc01589927c5384a316c8fd0919d2fb238f094c9f1b1933c55f85c411"),
    ENTRY_C: (912, "ed12b67d191970834c8513956ceed36f10b375b96ae548df474ceae72601f3b7"),
    ENTRY_H: (475, "0ca332635ba733752eb6aece5ddca0b3b304ee75e774d0a93a42541ad0fec35e"),
    COMPAT / "FreeRTOS.h": (168, "531a73fa2b140e20548a83882e7291c111630f685a5b54a44d41c93ac0c87128"),
    COMPAT / "open_cfw_cmbacktrace_port.h": (152, "1a95aa00853f1c1f085204372ff1c0acd52c60d438893770c968e3e45ce8d5aa"),
    COMPAT / "stdio.h": (163, "62f53724b4885cabd4795a63c2d82506a40045264cd27edd9b14e82f539b202c"),
    COMPAT / "stdlib.h": (133, "93a9752725fac19ef7c879385921f2c5bf720965da1a63b4a75bc7b6fdfe1833"),
    COMPAT / "string.h": (202, "36e48456cc901f50f535a2e1a2bbed46397b0b0609ea8d6d881c66ed2c0aae9d"),
}

EXPECTED_EXPORTS = {
    "cm_backtrace_assert",
    "cm_backtrace_call_stack",
    "cm_backtrace_call_stack_any",
    "cm_backtrace_fault",
    "cm_backtrace_firmware_info",
    "cm_backtrace_init",
}
EXPECTED_UPSTREAM_UNDEFINED = {
    "__aeabi_memclr4",
    "_estack",
    "_etext",
    "_sstack",
    "_stext",
    "open_cfw_cmbacktrace_print",
    "sprintf",
    "strncpy",
    "vTaskName",
    "vTaskStackAddr",
    "vTaskStackSize",
}


class AuditError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def _load_version_analyzer():
    spec = importlib.util.spec_from_file_location("g2_cmbacktrace_version_for_source", VERSION_ANALYZER)
    _require(spec is not None and spec.loader is not None, "cannot load version analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _symbols(nm: str, obj: Path) -> tuple[set[str], set[str]]:
    output = subprocess.run([nm, "-g", str(obj)], check=True, capture_output=True, text=True).stdout
    defined: set[str] = set()
    undefined: set[str] = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0] == "U":
            undefined.add(fields[1])
        elif len(fields) >= 3 and fields[-2].upper() in {"T", "W", "D", "B", "R"}:
            defined.add(fields[-1])
    return defined, undefined


def audit() -> dict[str, Any]:
    subprocess.run([sys.executable, str(SNAPSHOT_VERIFIER)], cwd=ROOT, check=True, capture_output=True)
    for path, (size, digest) in FILE_PINS.items():
        data = path.read_bytes()
        _require(len(data) == size, f"size changed: {path.relative_to(ROOT)}")
        _require(hashlib.sha256(data).hexdigest() == digest, f"SHA-256 changed: {path.relative_to(ROOT)}")

    version = _load_version_analyzer()
    identity = version.audit(version._load())
    _require(identity["pinned_bodies"]["cm_backtrace_fault"]["size"] == 786, "stock fault body pin changed")
    _require(identity["effective_configuration"]["CMB_CALL_STACK_MAX_DEPTH"] == 32, "call depth changed")
    _require(identity["effective_configuration"]["CMB_DUMP_STACK_DEPTH_SIZE"] == 16, "dump depth changed")

    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    objdump = shutil.which("llvm-objdump") or shutil.which("objdump")
    _require(clang is not None, "clang is unavailable")
    _require(nm is not None, "nm is unavailable")
    _require(objdump is not None, "objdump is unavailable")

    common = [
        clang, "--target=thumbv7em-none-eabi", "-mthumb", "-mcpu=cortex-m55", "-O2",
        "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections",
        "-Wall", "-Wextra", "-Werror",
    ]
    with tempfile.TemporaryDirectory(prefix="open-cfw-cmbacktrace-fault-") as raw_tmp:
        tmp = Path(raw_tmp)
        upstream_obj = tmp / "cm_backtrace.o"
        entry_obj = tmp / "fault_entry.o"
        upstream_cmd = common + [
            "-Wno-unused-parameter", "-DCMB_USER_CFG",
            "-DOPENCFW_CMB_PRINTLN(...)=open_cfw_cmbacktrace_print(__VA_ARGS__)",
            "-include", str(COMPAT / "open_cfw_cmbacktrace_port.h"),
            "-I" + str(COMPAT), "-I" + str(CONFIG.parent),
            "-I" + str(UPSTREAM_C.parent), "-c", str(UPSTREAM_C), "-o", str(upstream_obj),
        ]
        subprocess.run(upstream_cmd, cwd=ROOT, check=True, capture_output=True)
        subprocess.run(common + ["-c", str(ENTRY_C), "-o", str(entry_obj)], cwd=ROOT, check=True, capture_output=True)

        exports, unresolved = _symbols(nm, upstream_obj)
        entry_exports, entry_unresolved = _symbols(nm, entry_obj)
        _require(exports == EXPECTED_EXPORTS, f"upstream exports changed: {sorted(exports)}")
        _require(unresolved == EXPECTED_UPSTREAM_UNDEFINED, f"upstream seams changed: {sorted(unresolved)}")
        _require(entry_exports == {"open_cfw_cmbacktrace_hardfault_entry"}, "entry export changed")
        _require(entry_unresolved == {"cm_backtrace_fault"}, "entry dependency changed")

        disassembly = subprocess.run([objdump, "-d", str(entry_obj)], check=True, capture_output=True, text=True).stdout
        for instruction in ("mov\tr0, lr", "mov\tr1, sp", "bl\t", "b\t"):
            _require(instruction in disassembly, f"entry instruction missing: {instruction!r}")

    return {
        "component": "CmBacktrace fault path",
        "analysis_mode": "offline source/build audit; no hardware, signing, or flash operation",
        "status": "implemented-in-source / hardware-validation-blocked",
        "software_gap_count": 0,
        "source": {
            "upstream_commit": "73714489f9d8af130aacb515586b397b604a5768",
            "exact_vendor_checkout_proven": False,
            "target": "thumbv7em-none-eabi / Cortex-M55 / Thumb",
            "exports": sorted(EXPECTED_EXPORTS),
            "undefined_platform_seams": sorted(EXPECTED_UPSTREAM_UNDEFINED),
            "fault_entry_export": "open_cfw_cmbacktrace_hardfault_entry",
            "fault_entry_contract": ["r0 = EXC_RETURN (lr)", "r1 = exception sp", "call cm_backtrace_fault", "trap on return"],
        },
        "stock_evidence": {
            "fault_span": "[0x005944BC,0x005947CE)",
            "fault_size": 786,
            "fault_sha256": version.PINNED_BODIES["cm_backtrace_fault"][2],
            "historical_alignment_behavior_retained": True,
        },
        "production_registration": {
            "hardfault_vector_replaced": False,
            "stock_path_retained": True,
            "reason": "authorized G2 fault-injection evidence unavailable",
        },
        "hardware_block": {
            "required_evidence": "authorized G2 deliberate fault-injection validating register capture, FreeRTOS task/stack bounds, logger output, and terminal behavior",
            "physical_evidence_available": False,
            "authorized_right_temple_state": "nonresponsive/unavailable",
            "left_temple_state": "stock; not accessed",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"CmBacktrace fault closure: {result['status']}")
        print(f"  target: {result['source']['target']}")
        print(f"  source exports: {len(result['source']['exports'])}")
        print("  production HardFault vector: retained stock (physical validation unavailable)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"CmBacktrace fault source audit failed: {exc}") from exc
