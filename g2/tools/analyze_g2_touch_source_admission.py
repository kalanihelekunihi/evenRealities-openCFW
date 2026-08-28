#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Source-admission gate for exact touch runtime and CAT2 provider matches."""

from __future__ import annotations

import argparse
from collections import Counter
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
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
SEMANTIC_ANALYZER = TOOLS / "analyze_g2_touch_relocated_semantics.py"

SOURCES = {
    "runtime_c": TOUCH / "runtime_touch_runtime_adapters.c",
    "runtime_h": TOUCH / "runtime_touch_runtime_adapters.h",
    "cat2_c": TOUCH / "runtime_touch_cat2_adapters.c",
    "cat2_h": TOUCH / "runtime_touch_cat2_adapters.h",
}

CAT2_COMMIT = "35f1714623cfea682d5e285af80d50416b4c7bbc"
CAT2_ADMISSIONS = {
    0x7024: ("Cy_SysLib_DelayUs", "drivers/source/cy_syslib.c",
             "exact uint16 microseconds * cy_delayFreqMhz then Cy_SysLib_DelayCycles"),
    0x7144: ("Cy_SysPm_ExecuteCallback", "drivers/source/cy_syspm.c",
             "forward/reverse registered-callback execution topology"),
    0x7228: ("Cy_SysPm_CpuEnterSleep", "drivers/source/cy_syspm.c",
             "CHECK_READY/BEFORE/no-callback sleep/AFTER or CHECK_FAIL topology"),
    0x728C: ("Cy_SysPm_CpuEnterDeepSleep", "drivers/source/cy_syspm.c",
             "CHECK_READY/BEFORE/no-callback deep sleep/AFTER or CHECK_FAIL topology"),
    0x72F4: ("Cy_SysTick_ServiceCallbacks", "drivers/source/cy_systick.c",
             "COUNTFLAG gate and ordered five-slot callback traversal"),
    0x7320: ("Cy_SysTick_Enable", "drivers/source/cy_systick.c",
             "sets TICKINT then ENABLE in SysTick CTRL"),
    0x7338: ("Cy_SysTick_SetClockSource", "drivers/source/cy_systick.c",
             "clear/set CLKSOURCE bit from enum value"),
    0x7350: ("Cy_SysTick_Init", "drivers/source/cy_systick.c",
             "five callbacks cleared, vector installed, clock/reload/clear/enable sequence"),
    0x73A8: ("Cy_SysTick_SetCallback", "drivers/source/cy_systick.c",
             "five-slot bound, return prior callback, install replacement"),
}

RUNTIME_ADMISSIONS = {
    0x76AC: ("exit_wrapper", "open_cfw_touch_runtime_exit_adapter",
             "optional fini hook followed by mandatory halt provider"),
    0x76E4: ("__libc_init_array", "open_cfw_touch_runtime_init_arrays",
             "ordered preinit then init arrays with null entries skipped"),
    0x7740: ("_exit_halt", "open_cfw_touch_runtime_exit_adapter",
             "non-returning target represented by a mandatory fail-closed halt provider"),
    0x7744: ("runtime_init_stub", "open_cfw_touch_runtime_init_stub",
             "empty callee-saved-register-compatible initialization boundary"),
}

EXPECTED = {
    "admitted_functions": 13,
    "admission_counts": {"cat2_apache": 9, "runtime_mit": 4},
    "cat2_candidates_before": 54,
    "cat2_candidates_admitted": 9,
    "cat2_candidates_remaining": 45,
    "semantic_gap_before": 223,
    "semantic_gap_after": 210,
    "mixed_eula_application_admitted": 0,
    "admission_digest": "2e9179bdae38cb2d825c46f048fb7a03b992b64d010d178f9a91518d69d71218",
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None,
            f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _digest(rows: list[dict]) -> str:
    return sha256(json.dumps(rows, sort_keys=True,
                             separators=(",", ":")).encode())


def _compile_target() -> dict:
    clang = shutil.which("clang")
    require(clang is not None, "clang is required for Cortex-M0+ source gate")
    sizes = {}
    with tempfile.TemporaryDirectory() as raw:
        for key in ("runtime_c", "cat2_c"):
            source = SOURCES[key]
            output = Path(raw) / f"{source.stem}.o"
            proc = subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                "-mthumb", "-ffreestanding", "-std=c11", "-Wall", "-Wextra",
                "-Werror", "-I", str(TOUCH), "-c", str(source), "-o", str(output),
            ], capture_output=True, text=True)
            require(proc.returncode == 0,
                    f"Cortex-M0+ compile failed for {source.name}: {proc.stderr}")
            sizes[source.name] = output.stat().st_size
    return sizes


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_source_semantics")
    semantic = semantic_mod.analyze()
    rows_by_entry = {row["entry"]: row for row in semantic["semantic_rows"]}
    require(set(CAT2_ADMISSIONS) <= rows_by_entry.keys(),
            "CAT2 admitted entry disappeared")
    require(set(RUNTIME_ADMISSIONS) <= rows_by_entry.keys(),
            "runtime admitted entry disappeared")
    require(all(rows_by_entry[entry]["batch"] == "cat2_pdl"
                for entry in CAT2_ADMISSIONS), "CAT2 admission escaped CAT2 batch")
    require(all(rows_by_entry[entry]["batch"] == "runtime"
                for entry in RUNTIME_ADMISSIONS), "runtime admission escaped runtime batch")

    combined_runtime = (SOURCES["runtime_c"].read_text() +
                        SOURCES["runtime_h"].read_text())
    combined_cat2 = SOURCES["cat2_c"].read_text() + SOURCES["cat2_h"].read_text()
    require(combined_runtime.count("SPDX-License-Identifier: MIT") == 2,
            "runtime MIT declarations changed")
    require(combined_cat2.count("SPDX-License-Identifier: Apache-2.0") == 2,
            "CAT2 Apache declarations changed")
    require(CAT2_COMMIT in combined_cat2,
            "CAT2 pinned provider commit missing from adapter")
    require("Infineon-EULA" in combined_cat2,
            "CAT2 adapter must state EULA exclusion")
    target_objects = _compile_target()

    rows = []
    for entry, (name, symbol, evidence) in sorted(RUNTIME_ADMISSIONS.items()):
        stock = rows_by_entry[entry]
        rows.append({
            "entry": entry, "stock_candidate": name,
            "admitted_symbol": symbol, "admission": "runtime_mit",
            "source": "components/shared/touch/runtime_touch_runtime_adapters.c",
            "provider_commit": None, "license": "MIT",
            "instruction_sha256": stock["instruction_sha256"],
            "evidence": evidence,
        })
    for entry, (name, path, evidence) in sorted(CAT2_ADMISSIONS.items()):
        stock = rows_by_entry[entry]
        rows.append({
            "entry": entry, "stock_candidate": name,
            "admitted_symbol": name, "admission": "cat2_apache",
            "source": f"https://github.com/Infineon/mtb-pdl-cat2/{path}",
            "provider_commit": CAT2_COMMIT, "license": "Apache-2.0",
            "instruction_sha256": stock["instruction_sha256"],
            "evidence": evidence,
        })

    counts = dict(sorted(Counter(row["admission"] for row in rows).items()))
    batch_counts = semantic["metrics"]["batch_counts"]
    metrics = {
        "admitted_functions": len(rows),
        "admission_counts": counts,
        "cat2_candidates_before": batch_counts["cat2_pdl"],
        "cat2_candidates_admitted": len(CAT2_ADMISSIONS),
        "cat2_candidates_remaining": batch_counts["cat2_pdl"] - len(CAT2_ADMISSIONS),
        "semantic_gap_before": semantic["metrics"]["semantic_rows"],
        "semantic_gap_after": semantic["metrics"]["semantic_rows"] - len(rows),
        "mixed_eula_application_admitted": sum(
            rows_by_entry[row["entry"]]["batch"] in {
                "application_startup_clean_room", "capsense_cat2_mixed",
                "emeeprom_eula", "system_handoff_mixed",
            } for row in rows
        ),
        "admission_digest": _digest(rows),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"source admission {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch isolated source admission",
        "analysis_mode": "offline source/license/Cortex-M0+ compile gate; no hardware, MMIO, reset, DFU, signing, or flash operation",
        "metrics": metrics,
        "rows": rows,
        "source_files": {key: {
            "path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
            "sha256": sha256(path.read_bytes()),
        } for key, path in SOURCES.items()},
        "target": "ARM Cortex-M0+ freestanding Thumb",
        "target_objects": target_objects,
        "integration": "isolated adapters; not production-routed",
        "remaining": {
            "cat2_provider_candidates": 45,
            "application_startup": 99,
            "capsense_cat2_mixed": 55,
            "emeeprom_eula": 10,
            "system_handoff": 1,
            "total": 210,
        },
        "license_policy": "MIT clean-room runtime adapters; Apache-2.0 CAT2 provider and notices retained; no EULA/private/application source admission.",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = MANIFEST_DIR / "g2-touch-source-admission.tsv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "stock_candidate", "admitted_symbol",
                         "admission", "source", "provider_commit", "license",
                         "instruction_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["stock_candidate"],
                row["admitted_symbol"], row["admission"], row["source"],
                row["provider_commit"] or "-", row["license"],
                row["instruction_sha256"], row["evidence"],
            ])
    summary = MANIFEST_DIR / "g2-touch-source-admission-summary.json"
    slim = {key: value for key, value in result.items() if key != "rows"}
    slim["row_count"] = len(result["rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [path, summary]


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
        print(json.dumps({key: value for key, value in result.items()
                          if key != "rows"}, indent=2, sort_keys=True))
    else:
        print(f"admitted source routes: {result['metrics']['admitted_functions']}")
        print(f"remaining semantic/source gap: {result['metrics']['semantic_gap_after']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch source admission failed: {exc}") from exc
