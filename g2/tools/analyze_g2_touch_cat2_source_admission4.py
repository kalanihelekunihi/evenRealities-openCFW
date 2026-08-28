#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fourth exact CAT2 batch: public GPIO-inline and SysClk APIs."""

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
TOOLS = ROOT / "tools"
TOUCH = ROOT / "components/shared/touch"
MANIFEST_DIR = TOOLS / "manifests"
SEMANTIC_ANALYZER = TOOLS / "analyze_g2_touch_relocated_semantics.py"
THIRD_ADMISSION = TOOLS / "analyze_g2_touch_cat2_source_admission3.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
CAT2_SOURCE = TOUCH / "runtime_touch_cat2_adapters.c"
CAT2_HEADER = TOUCH / "runtime_touch_cat2_adapters.h"
CAT2_COMMIT = "35f1714623cfea682d5e285af80d50416b4c7bbc"
GPIO_HEADER_SHA256 = "b97bb3ca2eeb92940a63a4bc065310cad2dad46f275646c514475f2ce05d08f0"
SYSCLK_SOURCE_SHA256 = "fa7d3221a4a52f4cae68d291237c57541448539db05ddf0ba653fd0a04c08594"
SYSCLK_HEADER_SHA256 = "b23362eb4001ce5ccf648b2d7a9fe1c7af17568d102acfa309df679d363df574"

# Exact symbol locations are Function Name banner lines at the pinned commit.
ADMISSIONS = {
    0x5B28: ("Cy_GPIO_SetHSIOM", "drivers/include/cy_gpio.h", 482,
             "HSIOM port derivation and four-bit per-pin clear/set"),
    0x5B64: ("Cy_GPIO_Write", "drivers/include/cy_gpio.h", 719,
             "pin validation followed by DR_SET/DR_CLR atomic write"),
    0x5B84: ("Cy_GPIO_SetDrivemode", "drivers/include/cy_gpio.h", 867,
             "three-bit PC plus fourth drive-mode bit in PC2"),
    0x5BBE: ("Cy_GPIO_SetInterruptEdge", "drivers/include/cy_gpio.h", 1190,
             "two-bit per-pin interrupt configuration clear/set"),
    0x6938: ("Cy_SysClk_ExtClkGetFrequency", "drivers/source/cy_sysclk.c", 75,
             "single load of private EXTCLK frequency storage"),
    0x6944: ("Cy_SysClk_ImoGetFrequency", "drivers/source/cy_sysclk.c", 343,
             "IMO enabled check and CLK_IMO_SELECT frequency-field scaling"),
    0x6980: ("Cy_SysClk_ImoSetFrequency", "drivers/source/cy_sysclk.c", 190,
             "valid frequency set, trim-table programming, two 50-cycle delays"),
    0x6A90: ("Cy_SysClk_IloStartMeasurement", "drivers/source/cy_sysclk.c", 610,
             "measurement lock plus SRSS DFT source selections"),
    0x6ADC: ("Cy_SysClk_IloStopMeasurement", "drivers/source/cy_sysclk.c", 667,
             "measurement lock clear plus SRSS DFT cleanup"),
    0x6B18: ("Cy_SysClk_IloCompensate", "drivers/source/cy_sysclk.c", 722,
             "100..2000000 us validation and ILO counter compensation arithmetic"),
    0x6C34: ("Cy_SysClk_ClkHfGetDivider", "drivers/include/cy_sysclk.h", 2089,
             "SRSS CLK_SELECT HF divider two-bit extraction"),
    0x6C44: ("Cy_SysClk_ClkHfSetDivider", "drivers/include/cy_sysclk.h", 2049,
             "divider validation and SRSS CLK_SELECT HF divider clear/set"),
    0x6C9C: ("Cy_SysClk_ClkHfGetFrequency", "drivers/source/cy_sysclk.c", 2021,
             "HF source dispatch and right shift by selected divider"),
    0x6CD4: ("Cy_SysClk_PeriphSetDivider", "drivers/source/cy_sysclk.c", 2913,
             "integer divider type/range validation and PERI divider clear/set"),
    0x6D1C: ("Cy_SysClk_PeriphSetFracDivider", "drivers/source/cy_sysclk.c", 3013,
             "fractional divider type/range validation and INT/FRAC writes"),
    0x6DBC: ("Cy_SysClk_PeriphAssignDivider", "drivers/source/cy_sysclk.c", 3315,
             "peripheral destination/type validation and PCLK selector write"),
    0x6E04: ("Cy_SysClk_PeriphEnableDivider", "drivers/source/cy_sysclk.c", 3345,
             "validated PERI DIV_CMD enable/phase-align command and readback"),
    0x6E48: ("Cy_SysClk_PeriphDisableDivider", "drivers/source/cy_sysclk.c", 3383,
             "validated PERI DIV_CMD disable command"),
    0x6E88: ("Cy_SysClk_ClkHfSetSource", "drivers/source/cy_sysclk.c", 1882,
             "HF source validity/enable checks and SRSS source clear/set"),
}

SOURCE_HASHES = {
    "drivers/include/cy_gpio.h": GPIO_HEADER_SHA256,
    "drivers/source/cy_sysclk.c": SYSCLK_SOURCE_SHA256,
    "drivers/include/cy_sysclk.h": SYSCLK_HEADER_SHA256,
}

REQUIRED_TARGET_TOKENS = {
    0x5B28: ("bkpt #1", "str r2, [r3]"),
    0x5B64: ("str r3, [r0, #0x40]", "str r3, [r0, #0x44]"),
    0x5B84: ("str r3, [r0, #8]", "str r3, [r0, #0x18]"),
    0x5BBE: ("str r3, [r0, #0xc]",),
    0x6938: ("ldr r0, [r3]",),
    0x6944: ("ldr r3, [r3, #0x30]",),
    0x6980: ("bl #0x6944", "bl #0x1180"),
    0x6A90: ("str r3, [r1, #0x34]", "str r3, [r1]"),
    0x6ADC: ("str r3, [r2, #0x34]", "str r3, [r2]"),
    0x6B18: ("muls r5, r0, r5", "str r0, [r4]"),
    0x6C34: ("ldr r3, [r3, #0x28]",),
    0x6C44: ("bl #0x6c34", "str r3, [r1, #0x28]"),
    0x6C9C: ("bl #0x6c34", "lsrs r0, r5"),
    0x6CD4: ("str r3, [r1, r0]",),
    0x6D1C: ("str r2, [r0, r5]", "str r3, [r0, r5]"),
    0x6DBC: ("str r3, [r0, r2]",),
    0x6E04: ("str r3, [r2]", "ldr r3, [r2]"),
    0x6E48: ("str r3, [r2]",),
    0x6E88: ("str r3, [r1, #0x28]",),
}

CALL_SUBSETS = {
    0x6980: {0x6944},
    0x6C44: {0x6938, 0x6C34},
    0x6C9C: {0x6938, 0x6944, 0x6C34},
}

EXPECTED = {
    "admitted_functions": 19,
    "gpio_inline_functions": 4,
    "sysclk_functions": 15,
    "cat2_gap_before": 29,
    "cat2_gap_after": 10,
    "semantic_gap_before": 194,
    "semantic_gap_after": 175,
    "unsafe_batch_admissions": 0,
    "location_digest": "e9d5639ad89e99dea8e818128b0241ac783f018082f815e34c7deda694a1acec",
    "row_digest": "8367deeecf6856157a281c1bf14e8ec646bf9d35e3b609aad1867e8b299a8b8c",
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
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _target_compile() -> int:
    clang = shutil.which("clang")
    require(clang is not None, "clang unavailable")
    with tempfile.TemporaryDirectory() as raw:
        output = Path(raw) / "cat2-gpio-sysclk.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(CAT2_SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"CAT2 GPIO/SysClk compile failed: {proc.stderr}")
        return output.stat().st_size


def _target_signatures(prefix, payload: bytes, entries: set[int]) -> dict[int, str]:
    result = {}
    for entry, tokens in REQUIRED_TARGET_TOKENS.items():
        body = prefix._walk(payload, entry, entries)
        canonical = "|".join(
            f"{address:04X}:{insn.mnemonic} {insn.op_str}"
            for address, insn in sorted(body["instructions"].items())
        )
        for token in tokens:
            require(token in canonical, f"target register signature changed at {entry:#x}: {token}")
        result[entry] = sha256(canonical.encode())
    return result


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_cat2_4_semantics")
    third_mod = _load(THIRD_ADMISSION, "touch_cat2_4_third")
    prefix = _load(PREFIX_ANALYZER, "touch_cat2_4_prefix")
    semantic = semantic_mod.analyze()
    third = third_mod.analyze()
    by_entry = {row["entry"]: row for row in semantic["semantic_rows"]}
    require(set(ADMISSIONS) <= by_entry.keys(), "fourth CAT2 entries disappeared")
    prior = {row["entry"] for row in third["rows"]}
    require(not (set(ADMISSIONS) & prior), "fourth CAT2 batch overlaps batch 3")
    require(all(by_entry[entry]["batch"] == "cat2_pdl" for entry in ADMISSIONS),
            "fourth CAT2 batch escaped CAT2 candidates")
    for caller, required in CALL_SUBSETS.items():
        require(required <= set(by_entry[caller]["callees"]),
                f"public SysClk call topology changed at {caller:#x}")

    blob = prefix.BLOB.read_bytes()
    payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    target_signatures = _target_signatures(prefix, payload, set(by_entry))
    combined = CAT2_SOURCE.read_text() + CAT2_HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: Apache-2.0") == 2,
            "Apache declarations changed")
    require(CAT2_COMMIT in combined, "pinned CAT2 commit missing")
    for route in ("open_cfw_touch_cat2_gpio_value_route",
                  "open_cfw_touch_cat2_sysclk_route"):
        require(combined.count(route) == 2, f"batch-4 route changed: {route}")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (symbol, source, line, evidence) in sorted(ADMISSIONS.items()):
        stock = by_entry[entry]
        subsystem = "gpio_inline" if "gpio" in source else "sysclk"
        rows.append({
            "entry": entry, "symbol": symbol, "subsystem": subsystem,
            "source": f"https://github.com/Infineon/mtb-pdl-cat2/{source}",
            "source_line": line, "source_file_sha256": SOURCE_HASHES[source],
            "provider_commit": CAT2_COMMIT, "license": "Apache-2.0",
            "adapter": "runtime_touch_cat2_adapters.c",
            "instruction_sha256": stock["instruction_sha256"],
            "target_signature_sha256": target_signatures[entry],
            "evidence": evidence,
        })
    locations = [(row["entry"], row["source_line"]) for row in rows]
    metrics = {
        "admitted_functions": len(rows),
        "gpio_inline_functions": sum(row["subsystem"] == "gpio_inline" for row in rows),
        "sysclk_functions": sum(row["subsystem"] == "sysclk" for row in rows),
        "cat2_gap_before": third["metrics"]["cat2_gap_after"],
        "cat2_gap_after": third["metrics"]["cat2_gap_after"] - len(rows),
        "semantic_gap_before": third["metrics"]["semantic_gap_after"],
        "semantic_gap_after": third["metrics"]["semantic_gap_after"] - len(rows),
        "unsafe_batch_admissions": sum(by_entry[row["entry"]]["batch"] != "cat2_pdl" for row in rows),
        "location_digest": sha256(json.dumps(locations, separators=(",", ":")).encode()),
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"CAT2 fourth admission {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch CAT2 source admission batch 4",
        "analysis_mode": "offline exact public symbol/location/register/caller signature and Cortex-M0+ compile gate; no hardware or MMIO execution",
        "metrics": metrics, "rows": rows,
        "provider_sources": {"commit": CAT2_COMMIT, **SOURCE_HASHES},
        "adapter": {"path": str(CAT2_SOURCE.relative_to(ROOT)),
                    "sha256": sha256(CAT2_SOURCE.read_bytes()),
                    "target_object_bytes": target_object_bytes},
        "integration": "isolated Apache typed routes; GPIO/SRSS/PERI MMIO providers unavailable and fail-closed on host",
        "remaining": {"cat2_candidates": 10, "total_semantic_source_gap": 175},
        "remaining_entries": ["0x5CA0", "0x5CD0", "0x6044", "0x60C4", "0x6210",
                              "0x62B8", "0x6448", "0x64FC", "0x7038", "0x70B0"],
        "exclusions": "remaining SCB/device/system entries plus mixed CAPSENSE/CAT2, Em_EEPROM EULA, application/startup, and system/DFU batches unchanged",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = MANIFEST_DIR / "g2-touch-cat2-source-admission4.tsv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "subsystem", "source", "source_line",
                         "source_file_sha256", "provider_commit", "license", "adapter",
                         "instruction_sha256", "target_signature_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["subsystem"],
                             row["source"], row["source_line"], row["source_file_sha256"],
                             row["provider_commit"], row["license"], row["adapter"],
                             row["instruction_sha256"], row["target_signature_sha256"],
                             row["evidence"]])
    summary = MANIFEST_DIR / "g2-touch-cat2-source-admission4-summary.json"
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
        print(json.dumps({key: value for key, value in result.items() if key != "rows"},
                         indent=2, sort_keys=True))
    else:
        print(f"CAT2 batch-4 admissions: {result['metrics']['admitted_functions']}")
        print(f"remaining semantic/source gap: {result['metrics']['semantic_gap_after']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch CAT2 admission 4 failed: {exc}") from exc
