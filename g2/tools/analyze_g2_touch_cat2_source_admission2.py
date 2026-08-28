#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Second exact CAT2 source-order/register-signature admission batch."""

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
FIRST_ADMISSION = TOOLS / "analyze_g2_touch_source_admission.py"
CAT2_SOURCE = TOUCH / "runtime_touch_cat2_adapters.c"
CAT2_HEADER = TOUCH / "runtime_touch_cat2_adapters.h"
CAT2_COMMIT = "35f1714623cfea682d5e285af80d50416b4c7bbc"

ADMISSIONS = {
    0x58F4: ("ProcessStatusCode", "drivers/source/cy_flash.c", "CPUSS SYSARG SROM status-family decoder and 20-entry shipped switch table"),
    0x5974: ("Cy_Flash_ValidAddr", "drivers/source/cy_flash.c", "source-order helper after status decoder; flash/SFlash range validation"),
    0x59A8: ("Cy_Flash_GetRowNum", "drivers/source/cy_flash.c", "source-order row-address to row-number helper"),
    0x59C4: ("Cy_Flash_ClockBackup", "drivers/source/cy_flash.c", "CPUSS SYSARG/SYSREQ clock-backup SROM call"),
    0x5A00: ("Cy_Flash_ClockConfig", "drivers/source/cy_flash.c", "CPUSS SYSARG/SYSREQ clock-config SROM call"),
    0x5A20: ("Cy_Flash_ClockRestore", "drivers/source/cy_flash.c", "CPUSS SYSARG/SYSREQ clock-restore SROM call"),
    0x5A50: ("Cy_Flash_WriteRow", "drivers/source/cy_flash.c", "public write-row caller topology over the six adjacent helpers, memcpy, and critical section"),
    0x5BE4: ("Cy_GPIO_Pin_Init", "drivers/source/cy_gpio.c", "six pin-config call sites and ordered write/drive/HSIOM/edge/vtrip/slew helpers"),
    0x680C: ("Cy_SCB_I2C_SlaveInterrupt", "drivers/source/cy_scb_i2c.c", "slave IRQ entry from touch ISR and five receive/address/transmit/stop helper branches"),
}

EXPECTED = {
    "admitted_functions": 9,
    "flash_functions": 7,
    "gpio_functions": 1,
    "scb_i2c_functions": 1,
    "cat2_gap_before": 45,
    "cat2_gap_after": 36,
    "semantic_gap_before": 210,
    "semantic_gap_after": 201,
    "unsafe_batch_admissions": 0,
    "row_digest": "fb1160f25a1f4a0fa843147aa879f8e8038756dc64742b8cf007940c087eacb9",
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
        output = Path(raw) / "cat2.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(CAT2_SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"CAT2 target compile failed: {proc.stderr}")
        return output.stat().st_size


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_cat2_2_semantics")
    first_mod = _load(FIRST_ADMISSION, "touch_cat2_2_first")
    semantic = semantic_mod.analyze()
    first = first_mod.analyze()
    by_entry = {row["entry"]: row for row in semantic["semantic_rows"]}
    require(set(ADMISSIONS) <= by_entry.keys(), "second CAT2 entries disappeared")
    require(not (set(ADMISSIONS) & {row["entry"] for row in first["rows"]}),
            "second CAT2 batch overlaps first admission")
    require(all(by_entry[entry]["batch"] == "cat2_pdl" for entry in ADMISSIONS),
            "second CAT2 batch escaped CAT2 candidates")
    combined = CAT2_SOURCE.read_text() + CAT2_HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: Apache-2.0") == 2,
            "Apache declarations changed")
    require(CAT2_COMMIT in combined, "pinned CAT2 commit missing")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (name, source, evidence) in sorted(ADMISSIONS.items()):
        stock = by_entry[entry]
        subsystem = ("flash" if "cy_flash" in source else
                     "gpio" if "cy_gpio" in source else "scb_i2c")
        rows.append({
            "entry": entry, "symbol": name, "subsystem": subsystem,
            "source": f"https://github.com/Infineon/mtb-pdl-cat2/{source}",
            "provider_commit": CAT2_COMMIT, "license": "Apache-2.0",
            "adapter": "runtime_touch_cat2_adapters.c",
            "instruction_sha256": stock["instruction_sha256"],
            "evidence": evidence,
        })
    metrics = {
        "admitted_functions": len(rows),
        "flash_functions": sum(row["subsystem"] == "flash" for row in rows),
        "gpio_functions": sum(row["subsystem"] == "gpio" for row in rows),
        "scb_i2c_functions": sum(row["subsystem"] == "scb_i2c" for row in rows),
        "cat2_gap_before": first["metrics"]["cat2_candidates_remaining"],
        "cat2_gap_after": first["metrics"]["cat2_candidates_remaining"] - len(rows),
        "semantic_gap_before": first["metrics"]["semantic_gap_after"],
        "semantic_gap_after": first["metrics"]["semantic_gap_after"] - len(rows),
        "unsafe_batch_admissions": sum(by_entry[row["entry"]]["batch"] != "cat2_pdl"
                                       for row in rows),
        "row_digest": sha256(json.dumps(rows, sort_keys=True,
                                         separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"CAT2 second admission {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch CAT2 source admission batch 2",
        "analysis_mode": "offline exact source-order/register/caller signature and Cortex-M0+ compile gate; no hardware or MMIO execution",
        "metrics": metrics, "rows": rows,
        "adapter": {"path": str(CAT2_SOURCE.relative_to(ROOT)),
                    "sha256": sha256(CAT2_SOURCE.read_bytes()),
                    "target_object_bytes": target_object_bytes},
        "integration": "isolated Apache provider routes; not production-routed",
        "remaining": {"cat2_candidates": 36, "total_semantic_source_gap": 201},
        "exclusions": "mixed CAPSENSE/CAT2, Em_EEPROM EULA, application/startup, and system/DFU batches unchanged",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = MANIFEST_DIR / "g2-touch-cat2-source-admission2.tsv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "subsystem", "source", "provider_commit",
                         "license", "adapter", "instruction_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["subsystem"],
                             row["source"], row["provider_commit"], row["license"],
                             row["adapter"], row["instruction_sha256"], row["evidence"]])
    summary = MANIFEST_DIR / "g2-touch-cat2-source-admission2-summary.json"
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
        for path in write_manifests(result): print(f"wrote {path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2, sort_keys=True))
    else:
        print(f"CAT2 batch-2 admissions: {result['metrics']['admitted_functions']}")
        print(f"remaining semantic/source gap: {result['metrics']['semantic_gap_after']}")
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except AuditError as exc: raise SystemExit(f"Touch CAT2 admission 2 failed: {exc}") from exc
