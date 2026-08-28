#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Third exact CAT2 admission batch: public SCB common FIFO functions."""

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
SECOND_ADMISSION = TOOLS / "analyze_g2_touch_cat2_source_admission2.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
CAT2_SOURCE = TOUCH / "runtime_touch_cat2_adapters.c"
CAT2_HEADER = TOUCH / "runtime_touch_cat2_adapters.h"
CAT2_COMMIT = "35f1714623cfea682d5e285af80d50416b4c7bbc"
SCB_SOURCE_SHA256 = "e0cd9973c871649e30cab5e6f4124f1b5bef696eb693c3a796d2c5f08968d3c1"
SCB_HEADER_SHA256 = "3d23105304c9c7bb4a6fa43cc9947d1bb3d50275f9b7b1e383ca56d89feb2deb"

# Entry, exact public symbol, provider file, source-order position, target proof.
ADMISSIONS = {
    0x5F18: ("Cy_SCB_ReadArrayNoCheck", "drivers/source/cy_scb_common.c", 1,
             "RX_CTRL data-width branch; RX_FIFO_RD byte/halfword stores"),
    0x5F50: ("Cy_SCB_ReadArray", "drivers/source/cy_scb_common.c", 2,
             "RX_FIFO_STATUS count clamp then direct call to 0x5F18"),
    0x5F6E: ("Cy_SCB_WriteArrayNoCheck", "drivers/source/cy_scb_common.c", 5,
             "TX_CTRL data-width branch; byte/halfword loads to TX_FIFO_WR"),
    0x5FA6: ("Cy_SCB_WriteArray", "drivers/source/cy_scb_common.c", 6,
             "FIFO-size minus TX_FIFO_STATUS clamp then call to 0x5F6E"),
    0x5FD6: ("Cy_SCB_WriteDefaultArrayNoCheck", "drivers/source/cy_scb_common.c", 9,
             "counted repeated value writes to TX_FIFO_WR"),
    0x5FE6: ("Cy_SCB_WriteDefaultArray", "drivers/source/cy_scb_common.c", 10,
             "FIFO-size minus TX count clamp then call to 0x5FD6"),
    0x6016: ("Cy_SCB_SetRxFifoLevel", "drivers/include/cy_scb_common.h", 11,
             "RX_FIFO_CTRL trigger-level clear/set with device FIFO-size assertion"),
}

EXPECTED = {
    "admitted_functions": 7,
    "scb_source_functions": 6,
    "scb_inline_functions": 1,
    "cat2_gap_before": 36,
    "cat2_gap_after": 29,
    "semantic_gap_before": 201,
    "semantic_gap_after": 194,
    "unsafe_batch_admissions": 0,
    "source_order_digest": "da7ffc8e230b86f36b29db4ae9d8b9c4360c49ec03f4041566aeed0cf3c0f981",
    "row_digest": "06c631b19f2ed0f3c0fe4781a7eed1fb5b5672eace69f9eedb5fb8512c4735f2",
}

CALL_EDGES = {
    0x5F50: [0x5F18],
    0x5FA6: [0x5F6E],
    0x5FE6: [0x5FD6],
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
        output = Path(raw) / "cat2-scb.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(CAT2_SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"CAT2 SCB target compile failed: {proc.stderr}")
        return output.stat().st_size


def _target_evidence(prefix, payload: bytes, entries: set[int]) -> dict[int, str]:
    evidence = {}
    for entry in ADMISSIONS:
        body = prefix._walk(payload, entry, entries)
        evidence[entry] = "|".join(
            f"{address:04X}:{insn.mnemonic} {insn.op_str}"
            for address, insn in sorted(body["instructions"].items())
        )
    require("strb" in evidence[0x5F18] and "strh" in evidence[0x5F18],
            "SCB RX array width signature changed")
    require("ldrb" in evidence[0x5F6E] and "ldrh" in evidence[0x5F6E],
            "SCB TX array width signature changed")
    require("bkpt #1" in evidence[0x6016] and "str r1, [r0, r4]" in evidence[0x6016],
            "SCB RX level assertion/register signature changed")
    return {entry: sha256(text.encode()) for entry, text in evidence.items()}


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_cat2_3_semantics")
    second_mod = _load(SECOND_ADMISSION, "touch_cat2_3_second")
    prefix = _load(PREFIX_ANALYZER, "touch_cat2_3_prefix")
    semantic = semantic_mod.analyze()
    second = second_mod.analyze()
    by_entry = {row["entry"]: row for row in semantic["semantic_rows"]}
    require(set(ADMISSIONS) <= by_entry.keys(), "third CAT2 entries disappeared")
    prior = {row["entry"] for row in second["rows"]}
    require(not (set(ADMISSIONS) & prior), "third CAT2 batch overlaps batch 2")
    require(all(by_entry[entry]["batch"] == "cat2_pdl" for entry in ADMISSIONS),
            "third CAT2 batch escaped CAT2 candidates")
    for caller, callees in CALL_EDGES.items():
        require(by_entry[caller]["callees"] == callees,
                f"SCB call edge changed at {caller:#x}")

    blob = prefix.BLOB.read_bytes()
    payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    target_signatures = _target_evidence(prefix, payload, set(by_entry))
    combined = CAT2_SOURCE.read_text() + CAT2_HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: Apache-2.0") == 2,
            "Apache declarations changed")
    require(CAT2_COMMIT in combined, "pinned CAT2 commit missing")
    for route in ("open_cfw_touch_cat2_scb_read_route",
                  "open_cfw_touch_cat2_scb_write_route",
                  "open_cfw_touch_cat2_scb_set_rx_level_route"):
        require(combined.count(route) == 2, f"SCB adapter route changed: {route}")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (name, source, order, evidence) in sorted(ADMISSIONS.items()):
        stock = by_entry[entry]
        rows.append({
            "entry": entry, "symbol": name,
            "subsystem": "scb_common_inline" if source.endswith(".h") else "scb_common",
            "source_order": order,
            "source": f"https://github.com/Infineon/mtb-pdl-cat2/{source}",
            "source_file_sha256": SCB_HEADER_SHA256 if source.endswith(".h") else SCB_SOURCE_SHA256,
            "provider_commit": CAT2_COMMIT, "license": "Apache-2.0",
            "adapter": "runtime_touch_cat2_adapters.c",
            "instruction_sha256": stock["instruction_sha256"],
            "target_signature_sha256": target_signatures[entry],
            "evidence": evidence,
        })
    order_pairs = [(row["entry"], row["source_order"]) for row in rows]
    metrics = {
        "admitted_functions": len(rows),
        "scb_source_functions": sum(row["subsystem"] == "scb_common" for row in rows),
        "scb_inline_functions": sum(row["subsystem"] == "scb_common_inline" for row in rows),
        "cat2_gap_before": second["metrics"]["cat2_gap_after"],
        "cat2_gap_after": second["metrics"]["cat2_gap_after"] - len(rows),
        "semantic_gap_before": second["metrics"]["semantic_gap_after"],
        "semantic_gap_after": second["metrics"]["semantic_gap_after"] - len(rows),
        "unsafe_batch_admissions": sum(by_entry[row["entry"]]["batch"] != "cat2_pdl" for row in rows),
        "source_order_digest": sha256(json.dumps(order_pairs, separators=(",", ":")).encode()),
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"CAT2 third admission {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch CAT2 source admission batch 3",
        "analysis_mode": "offline exact public symbol/source-order/SCB register signature and Cortex-M0+ compile gate; no hardware or MMIO execution",
        "metrics": metrics, "rows": rows,
        "provider_sources": {
            "commit": CAT2_COMMIT,
            "cy_scb_common.c_sha256": SCB_SOURCE_SHA256,
            "cy_scb_common.h_sha256": SCB_HEADER_SHA256,
        },
        "adapter": {"path": str(CAT2_SOURCE.relative_to(ROOT)),
                    "sha256": sha256(CAT2_SOURCE.read_bytes()),
                    "target_object_bytes": target_object_bytes},
        "integration": "isolated Apache typed routes; MMIO provider unavailable and fail-closed on host",
        "remaining": {"cat2_candidates": 29, "total_semantic_source_gap": 194},
        "exclusions": "larger SCB I2C bodies plus mixed CAPSENSE/CAT2, Em_EEPROM EULA, application/startup, and system/DFU batches unchanged",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = MANIFEST_DIR / "g2-touch-cat2-source-admission3.tsv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "subsystem", "source_order", "source",
                         "source_file_sha256", "provider_commit", "license", "adapter",
                         "instruction_sha256", "target_signature_sha256", "evidence"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["subsystem"],
                             row["source_order"], row["source"], row["source_file_sha256"],
                             row["provider_commit"], row["license"], row["adapter"],
                             row["instruction_sha256"], row["target_signature_sha256"],
                             row["evidence"]])
    summary = MANIFEST_DIR / "g2-touch-cat2-source-admission3-summary.json"
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
        print(f"CAT2 batch-3 admissions: {result['metrics']['admitted_functions']}")
        print(f"remaining semantic/source gap: {result['metrics']['semantic_gap_after']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch CAT2 admission 3 failed: {exc}") from exc
