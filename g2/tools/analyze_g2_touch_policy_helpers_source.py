#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Source/build closure for eight typed touch application-policy boundaries."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/touch/runtime_touch_policy_helpers.c"
HEADER = ROOT / "components/shared/touch/runtime_touch_policy_helpers.h"
FIXTURE = ROOT / "tests/fixtures/touch_policy_helpers_host.c"
HELPER_ANALYZER = ROOT / "tools/analyze_g2_touch_prefix_helper_evidence.py"
MANIFEST_DIR = ROOT / "tools/manifests"

PINS = {
    SOURCE: (6092, "e702bc819ca9c62c027e36550d7ad21afcf9165c30682a495b1e047bf48b3178"),
    HEADER: (3323, "62c57e00aace9f1b54d0a384e9c9fd83b714800d9c852b0896fe7336d86d823c"),
    FIXTURE: (6064, "b8f664b9f1b217ed34d7353403c416c693b5aa4d40cdaee4c29150893e6f4ef4"),
}
HELPER_EVIDENCE_DIGEST = "27b3373ad1475a6370eb0acb338f4564e10ba523a4e35d10ab6f61406b00329d"

EXPORTS = {
    "open_cfw_touch_policy_defaults",
    "open_cfw_touch_policy_config_read",
    "open_cfw_touch_policy_config_load",
    "open_cfw_touch_policy_saved_baseline_read",
    "open_cfw_touch_policy_timeout_default",
    "open_cfw_touch_policy_attention_rearm",
    "open_cfw_touch_policy_gesture_step",
    "open_cfw_touch_policy_baseline_update",
}

# Stock entry, source export, closure, provider contract, evidence limit.
BOUNDARIES = (
    (0x0268, "touch_config_read_adapter", "open_cfw_touch_policy_config_read",
     "implemented", "storage_ready + storage_read",
     "256-byte logical bound and provider-status translation"),
    (0x071C, "saved_proximity_baseline_read",
     "open_cfw_touch_policy_saved_baseline_read", "implemented", "none",
     "magic/config-valid gate then u16 baseline read"),
    (0x0738, "touch_config_load_from_eeprom",
     "open_cfw_touch_policy_config_load", "implemented",
     "storage_ready + storage_read",
     "UNVE defaults, eight-byte read, magic validation; defaults retained on failure"),
    (0x07FC, "attention_release_timeout_rearm",
     "open_cfw_touch_policy_attention_rearm", "provider_contract_fail_closed",
     "attention_release_timeout_rearm(delay_ms=200)",
     "transaction is external; no GPIO or timing implementation in MIT candidate"),
    (0x0BE8, "timeout_default_1000_if_zero",
     "open_cfw_touch_policy_timeout_default", "implemented", "none",
     "zero becomes 1000; nonzero remains unchanged"),
    (0x0BFC, "gesture_policy_helper_0bfc",
     "open_cfw_touch_policy_gesture_step", "provider_contract_fail_closed",
     "gesture_policy_step(observation,result)",
     "exact private gesture sub-policy unavailable; no fallback semantics invented"),
    (0x0D70, "touch_gesture_state_machine",
     "open_cfw_touch_policy_gesture_step", "provider_contract_fail_closed",
     "gesture_policy_step(observation,result)",
     "shared typed gesture provider; exact stock state-machine ABI unavailable"),
    (0x111C, "proximity_baseline_update_adapter",
     "open_cfw_touch_policy_baseline_update", "provider_contract_fail_closed",
     "baseline_update(saved,current)",
     "provider result commits atomically; missing/error leaves state unchanged"),
)


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_helpers():
    spec = importlib.util.spec_from_file_location(
        "g2_touch_prefix_helpers_for_source", HELPER_ANALYZER
    )
    require(spec is not None and spec.loader is not None,
            "cannot load helper evidence analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _symbols(nm: str, obj: Path) -> set[str]:
    output = subprocess.run([nm, "-g", str(obj)], check=True,
                            capture_output=True, text=True).stdout
    symbols = set()
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-2].upper() in {"T", "W"}:
            symbols.add(fields[-1])
    return symbols


def analyze() -> dict:
    for path, (size, digest) in PINS.items():
        data = path.read_bytes()
        require(len(data) == size, f"source pin size changed: {path.relative_to(ROOT)}")
        require(sha256(data) == digest,
                f"source pin digest changed: {path.relative_to(ROOT)}")

    helpers = _load_helpers().analyze()
    require(helpers["metrics"]["evidence_digest"] == HELPER_EVIDENCE_DIGEST,
            "touch helper evidence digest changed")
    clean_room_entries = {
        row["entry"] for row in helpers["rows"]
        if row["boundary"] == "open_cfw_clean_room"
    }
    require(clean_room_entries == {row[0] for row in BOUNDARIES},
            "source closure does not cover all eight clean-room boundaries")

    source_text = SOURCE.read_text()
    header_text = HEADER.read_text()
    for forbidden in ("0x40040400", "0x40290000", "0x40250000",
                      "cy_capsense", "cy_em_eeprom", "Cy_Em_EEPROM"):
        require(forbidden not in source_text,
                f"direct vendor/MMIO dependency entered source: {forbidden}")
    require("SPDX-License-Identifier: MIT" in source_text,
            "source MIT SPDX marker missing")
    require("SPDX-License-Identifier: MIT" in header_text,
            "header MIT SPDX marker missing")
    require("OPEN_CFW_TOUCH_POLICY_UNAVAILABLE" in source_text,
            "fail-closed provider status missing")

    clang = shutil.which("clang")
    nm = shutil.which("llvm-nm") or shutil.which("nm")
    require(clang is not None and nm is not None, "target build tools unavailable")
    with tempfile.TemporaryDirectory(prefix="open-cfw-touch-policy-source-") as raw:
        obj = Path(raw) / "policy.o"
        subprocess.run([
            clang, "--target=thumbv6m-none-eabi", "-mthumb",
            "-mcpu=cortex-m0plus", "-std=c11", "-O2", "-ffreestanding",
            "-fno-builtin", "-ffunction-sections", "-fdata-sections",
            "-Wall", "-Wextra", "-Werror", "-I" + str(SOURCE.parent),
            "-c", str(SOURCE), "-o", str(obj),
        ], cwd=ROOT, check=True, capture_output=True)
        found = _symbols(nm, obj)
        require(found == EXPORTS, f"target exports changed: {sorted(found)}")
        object_bytes = obj.stat().st_size

    return {
        "schema_version": 1,
        "component": "G2 touch application-policy helper boundaries",
        "analysis_mode": "offline source/build audit; no hardware, MMIO, sleep, reset, DFU, signing, or flash operation",
        "license": "MIT",
        "target": "thumbv6m-none-eabi / Cortex-M0+ / Thumb",
        "helper_evidence_digest": HELPER_EVIDENCE_DIGEST,
        "source": str(SOURCE.relative_to(ROOT)),
        "header": str(HEADER.relative_to(ROOT)),
        "exports": sorted(EXPORTS),
        "target_object_bytes": object_bytes,
        "boundaries": [
            {"stock_entry": entry, "evidence_name": name,
             "source_export": export, "closure": closure,
             "provider_contract": provider, "evidence_limit": limit}
            for entry, name, export, closure, provider, limit in BOUNDARIES
        ],
        "metrics": {
            "stock_boundaries": len(BOUNDARIES),
            "source_exports": len(EXPORTS),
            "implemented_boundaries": sum(row[3] == "implemented"
                                            for row in BOUNDARIES),
            "fail_closed_provider_boundaries": sum(
                row[3] == "provider_contract_fail_closed" for row in BOUNDARIES
            ),
            "direct_mmio_dependencies": 0,
            "infineon_eula_source_dependencies": 0,
        },
        "provider_policy": {
            "missing_callback": "OPEN_CFW_TOUCH_POLICY_UNAVAILABLE; output/state unchanged",
            "provider_error": "OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR; output/state unchanged",
            "invalid_provider_result": "OPEN_CFW_TOUCH_POLICY_INVALID_DATA; output/state unchanged",
            "infineon_capsense_and_emeeprom": "external providers only; no EULA source copied or compiled",
        },
        "integration": "isolated candidate; not production-routed by this tranche",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    tsv = MANIFEST_DIR / "g2-touch-policy-helper-source-closure.tsv"
    with tsv.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["stock_entry", "evidence_name", "source_export",
                         "closure", "provider_contract", "evidence_limit"])
        for row in result["boundaries"]:
            writer.writerow([
                f"0x{row['stock_entry']:04X}", row["evidence_name"],
                row["source_export"], row["closure"],
                row["provider_contract"], row["evidence_limit"],
            ])
    summary = MANIFEST_DIR / "g2-touch-policy-helper-source-summary.json"
    summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return [tsv, summary]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        metrics = result["metrics"]
        print(f"touch policy boundaries: {metrics['stock_boundaries']}")
        print(f"implemented: {metrics['implemented_boundaries']}")
        print(f"provider fail-closed: {metrics['fail_closed_provider_boundaries']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Touch policy helper source audit failed: {exc}") from exc
