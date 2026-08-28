#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fifth CAT2 batch: final exact providers and one unavailable halt ABI."""

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
FOURTH_ADMISSION = TOOLS / "analyze_g2_touch_cat2_source_admission4.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
CAT2_SOURCE = TOUCH / "runtime_touch_cat2_adapters.c"
CAT2_HEADER = TOUCH / "runtime_touch_cat2_adapters.h"
CAT2_COMMIT = "35f1714623cfea682d5e285af80d50416b4c7bbc"

SOURCE_HASHES = {
    "drivers/source/cy_msclp.c": "2613ec6fee3ac2ca6d8a42e483bb671f9ed63a58045b125ee6fe11f6f2d60f07",
    "drivers/source/cy_scb_i2c.c": "9f3e77675ea3f02798107fe28def78b826b35d6d136785644d90ff10877f248b",
    "drivers/source/cy_syspm.c": "be43e5aa704c99acca45850db68094977a274dcb1d4335fafca753269c5a93b8",
}
SYSLIB_HEADER_SHA256 = "6c6e35da19d618c752c767873e89ae6144877a1a4eacafe13b31cc0c0f8e7ca4"

ADMISSIONS = {
    0x5CA0: ("Cy_MSCLP_Capture", "drivers/source/cy_msclp.c", 213,
             "base/key/context validation and lock-key acquisition"),
    0x5CD0: ("Cy_MSCLP_Configure", "drivers/source/cy_msclp.c", 270,
             "lock-key validation and exhaustive MSCLP register/config arrays"),
    0x6044: ("SlaveHandleHsMode", "drivers/source/cy_scb_i2c.c", 2431,
             "HS callback, FIFO level, slave status and stretch-command branches"),
    0x60C4: ("SlaveHandleStop", "drivers/source/cy_scb_i2c.c", 2853,
             "three-argument stop/restart completion, FIFO recovery and callback"),
    0x6210: ("SlaveHandleAck", "drivers/source/cy_scb_i2c.c", 2975,
             "direction callback and RX/TX buffer/FIFO preparation"),
    0x62B8: ("SlaveHandleAddress", "drivers/source/cy_scb_i2c.c", 2494,
             "address callback ACK/NAK/WAIT handling followed by ack helper"),
    0x6448: ("SlaveHandleDataReceive", "drivers/source/cy_scb_i2c.c", 2661,
             "RX FIFO array copy, buffer accounting and next-level programming"),
    0x64FC: ("SlaveHandleDataTransmit", "drivers/source/cy_scb_i2c.c", 2749,
             "default/array TX FIFO fill, last-byte critical section and events"),
    0x70B0: ("Cy_SysPm_RegisterCallback", "drivers/source/cy_syspm.c", 357,
             "validated priority-ordered doubly-linked callback root insertion"),
}

REQUIRED_TARGET_TOKENS = {
    0x5CA0: ("strb r1, [r2]", "cmp r3, #0"),
    0x5CD0: ("ldr r3, [r3]", "str r3, [r0]", "cmp r0, #2"),
    0x6044: ("blx r3", "bl #0x6016", "str r2, [r4, r3]"),
    0x60C4: ("movs r4, r2", "str r2, [r4, #0x34]", "blx r3"),
    0x6210: ("blx r3", "bl #0x6016", "str r3, [r4, #4]"),
    0x62B8: ("blx r3", "bl #0x6210", "bl #0x6016"),
    0x6448: ("bl #0x5f50", "bl #0x6016", "strb r1, [r2, r3]"),
    0x64FC: ("bl #0x5fe6", "bl #0x5fa6", "blx r3"),
    0x70B0: ("str r0, [r3, #0x10]", "str r0, [r4, #0x14]", "str r0, [r5, r3]"),
}

CALL_SUBSETS = {
    0x6044: {0x6016}, 0x60C4: {0x6016}, 0x6210: {0x6016},
    0x62B8: {0x6016, 0x6210}, 0x6448: {0x5F50, 0x6016},
    0x64FC: {0x5FA6, 0x5FE6},
}

EXPECTED = {
    "admitted_functions": 9,
    "msclp_functions": 2,
    "scb_i2c_private_functions": 6,
    "syspm_functions": 1,
    "typed_unavailable_functions": 1,
    "cat2_gap_before": 10,
    "cat2_gap_after": 1,
    "semantic_gap_before": 175,
    "semantic_gap_after": 166,
    "unsafe_batch_admissions": 0,
    "location_digest": "14bfe9e877a4691e238412e0a83956e586c896125561952815450c4719653356",
    "row_digest": "6f50b021ebdaac1345b8cdcee3ee7ecb3e78ba8232f36d807d0a6d11b3aa898d",
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
        output = Path(raw) / "cat2-final.o"
        proc = subprocess.run([
            clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
            "-ffreestanding", "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-I", str(TOUCH), "-c", str(CAT2_SOURCE), "-o", str(output),
        ], capture_output=True, text=True)
        require(proc.returncode == 0, f"final CAT2 target compile failed: {proc.stderr}")
        return output.stat().st_size


def _canonical_body(prefix, payload: bytes, entry: int, entries: set[int]) -> str:
    body = prefix._walk(payload, entry, entries)
    return "|".join(
        f"{address:04X}:{insn.mnemonic} {insn.op_str}"
        for address, insn in sorted(body["instructions"].items())
    )


def analyze(*, enforce_expected: bool = True) -> dict:
    semantic_mod = _load(SEMANTIC_ANALYZER, "touch_cat2_5_semantics")
    fourth_mod = _load(FOURTH_ADMISSION, "touch_cat2_5_fourth")
    prefix = _load(PREFIX_ANALYZER, "touch_cat2_5_prefix")
    semantic = semantic_mod.analyze()
    fourth = fourth_mod.analyze()
    by_entry = {row["entry"]: row for row in semantic["semantic_rows"]}
    require(set(ADMISSIONS) | {0x7038} <= by_entry.keys(),
            "final CAT2 entries disappeared")
    prior = {row["entry"] for row in fourth["rows"]}
    require(not (set(ADMISSIONS) & prior), "fifth CAT2 batch overlaps batch 4")
    require(all(by_entry[entry]["batch"] == "cat2_pdl" for entry in ADMISSIONS),
            "fifth CAT2 batch escaped CAT2 candidates")
    for caller, required in CALL_SUBSETS.items():
        require(required <= set(by_entry[caller]["callees"]),
                f"SCB I2C helper topology changed at {caller:#x}")

    blob = prefix.BLOB.read_bytes()
    payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    entries = set(by_entry)
    signatures = {}
    for entry, tokens in REQUIRED_TARGET_TOKENS.items():
        canonical = _canonical_body(prefix, payload, entry, entries)
        for token in tokens:
            require(token in canonical, f"final CAT2 signature changed at {entry:#x}: {token}")
        signatures[entry] = sha256(canonical.encode())
    halt_body = _canonical_body(prefix, payload, 0x7038, entries)
    require(halt_body == "7038:b #0x7038", "halt self-loop body changed")

    combined = CAT2_SOURCE.read_text() + CAT2_HEADER.read_text()
    require(combined.count("SPDX-License-Identifier: Apache-2.0") == 2,
            "Apache declarations changed")
    require(CAT2_COMMIT in combined, "pinned CAT2 commit missing")
    for route in ("open_cfw_touch_cat2_msclp_route",
                  "open_cfw_touch_cat2_i2c_helper_route",
                  "open_cfw_touch_cat2_register_callback_route",
                  "open_cfw_touch_cat2_system_halt_route"):
        require(combined.count(route) == 2, f"final CAT2 route changed: {route}")
    target_object_bytes = _target_compile()

    rows = []
    for entry, (symbol, source, line, evidence) in sorted(ADMISSIONS.items()):
        subsystem = ("msclp" if "msclp" in source else
                     "scb_i2c_private" if "scb_i2c" in source else "syspm")
        rows.append({
            "entry": entry, "symbol": symbol, "subsystem": subsystem,
            "source": f"https://github.com/Infineon/mtb-pdl-cat2/{source}",
            "source_line": line, "source_file_sha256": SOURCE_HASHES[source],
            "provider_commit": CAT2_COMMIT, "license": "Apache-2.0",
            "adapter": "runtime_touch_cat2_adapters.c",
            "instruction_sha256": by_entry[entry]["instruction_sha256"],
            "target_signature_sha256": signatures[entry], "evidence": evidence,
        })
    unavailable = [{
        "entry": 0x7038, "symbol": "legacy_halt_self_loop",
        "status": "typed_external_system_provider_unavailable",
        "provider": "explicit injected halt provider required",
        "license": "LicenseRef-Upstream-Body-Unavailable",
        "instruction_sha256": by_entry[0x7038]["instruction_sha256"],
        "target_signature_sha256": sha256(halt_body.encode()),
        "evidence": "exact two-byte self-loop; pinned cy_syslib.h changelog says Cy_SysLib_Halt was removed and supplies no authentic body",
    }]
    locations = [(row["entry"], row["source_line"]) for row in rows]
    metrics = {
        "admitted_functions": len(rows),
        "msclp_functions": sum(row["subsystem"] == "msclp" for row in rows),
        "scb_i2c_private_functions": sum(row["subsystem"] == "scb_i2c_private" for row in rows),
        "syspm_functions": sum(row["subsystem"] == "syspm" for row in rows),
        "typed_unavailable_functions": len(unavailable),
        "cat2_gap_before": fourth["metrics"]["cat2_gap_after"],
        "cat2_gap_after": fourth["metrics"]["cat2_gap_after"] - len(rows),
        "semantic_gap_before": fourth["metrics"]["semantic_gap_after"],
        "semantic_gap_after": fourth["metrics"]["semantic_gap_after"] - len(rows),
        "unsafe_batch_admissions": sum(by_entry[row["entry"]]["batch"] != "cat2_pdl" for row in rows),
        "location_digest": sha256(json.dumps(locations, separators=(",", ":")).encode()),
        "row_digest": sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"CAT2 fifth admission {key} changed: {metrics[key]!r} != {expected!r}")
    return {
        "schema_version": 1,
        "component": "G2 touch CAT2 source admission batch 5",
        "analysis_mode": "offline exact public/private symbol/location/register/caller signature and Cortex-M0+ compile gate; no hardware or MMIO execution",
        "metrics": metrics, "rows": rows, "typed_unavailable": unavailable,
        "provider_sources": {"commit": CAT2_COMMIT, **SOURCE_HASHES,
                             "drivers/include/cy_syslib.h": SYSLIB_HEADER_SHA256},
        "adapter": {"path": str(CAT2_SOURCE.relative_to(ROOT)),
                    "sha256": sha256(CAT2_SOURCE.read_bytes()),
                    "target_object_bytes": target_object_bytes},
        "integration": "isolated Apache typed routes; MSCLP/SCB/SysPm/halt providers unavailable and fail-closed on host",
        "remaining": {"cat2_candidates": 1, "total_semantic_source_gap": 166,
                      "typed_unavailable_entry": "0x7038"},
        "exclusions": "legacy halt remains typed external; mixed CAPSENSE/CAT2, Em_EEPROM EULA, application/startup, and DFU/system batches unchanged",
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    admitted = MANIFEST_DIR / "g2-touch-cat2-source-admission5.tsv"
    with admitted.open("w", newline="") as handle:
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
    external = MANIFEST_DIR / "g2-touch-cat2-source-admission5-unavailable.tsv"
    with external.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "symbol", "status", "provider", "license",
                         "instruction_sha256", "target_signature_sha256", "evidence"])
        for row in result["typed_unavailable"]:
            writer.writerow([f"0x{row['entry']:04X}", row["symbol"], row["status"],
                             row["provider"], row["license"], row["instruction_sha256"],
                             row["target_signature_sha256"], row["evidence"]])
    summary = MANIFEST_DIR / "g2-touch-cat2-source-admission5-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("rows", "typed_unavailable")}
    slim["admitted_row_count"] = len(result["rows"])
    slim["typed_unavailable_row_count"] = len(result["typed_unavailable"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [admitted, external, summary]


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
                          if key not in ("rows", "typed_unavailable")},
                         indent=2, sort_keys=True))
    else:
        print(f"CAT2 batch-5 admissions: {result['metrics']['admitted_functions']}")
        print(f"remaining typed CAT2 boundary: {result['remaining']['typed_unavailable_entry']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch CAT2 admission 5 failed: {exc}") from exc
