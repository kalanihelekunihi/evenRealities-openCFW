#!/usr/bin/env python3
"""Authenticate the clean-room NemaVG start/end stroke-cap candidate."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
CORPUS = ROOT / "research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-08.c"
PROVENANCE = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
SOURCE = ROOT / "components/shared/lvgl/runtime_nemavg_stroke_caps_candidate.c"
HEADER = SOURCE.with_suffix(".h")
SUMMARY = ROOT / "tools/manifests/g2-nemavg-stroke-caps-candidate-summary.json"

PINS = {
    FUNCTIONS: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    CORPUS: (981_479, "2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"),
    PROVENANCE: (24_898, "5a8e427ae337afb78f2901e74ae48d08d8c222944a50ada8adadfbdd98296bfa"),
    SOURCE: (6_523, "738b8749da5f234aacaa076c087f4c99541330c30c6c475d775dc1566747edb0"),
    HEADER: (2_379, "39f9d1b645f6cbfd4cb267ba32953a0787e717ebf67936619b4d7c67142bba6c"),
}

EXPECTED = {
    0x0051B8F0: {
        "symbol": "draw_start_cap",
        "style_offsets": ["0x2e0"],
        "body_bytes": 1664,
        "physical_bytes": 1668,
        "body_sha256": "549fd3c4e21f1074d6f2b04309e72283b3f85b575f41bd31fc4718f7a63e3382",
        "ranges": [["0051b8f0", "0051bd1b"], ["0051bd20", "0051bf73"]],
        "public_dwarf_line": 1853,
    },
    0x0051BF7C: {
        "symbol": "draw_end_cap",
        "style_offsets": ["0x2e1"],
        "body_bytes": 1636,
        "physical_bytes": 1640,
        "body_sha256": "d022571f745517bf7494d69d79e5c1ba934faf8dc65c0cb6f465d4f36fb81d56",
        "ranges": [["0051bf7c", "0051c393"], ["0051c398", "0051c5e3"]],
        "public_dwarf_line": 1888,
    },
    0x0051C5EC: {
        "symbol": "draw_caps",
        "style_offsets": ["0x2e0", "0x2e1"],
        "body_bytes": 3298,
        "physical_bytes": 3306,
        "body_sha256": "7487038aa5bf05ee5c13296625a2ddf2c7ea592f5dc975661b7f6e0c7a3c1c27",
        "ranges": [["0051c5ec", "0051ccc7"], ["0051cccc", "0051d08f"],
                   ["0051d094", "0051d2d5"]],
        "public_dwarf_line": 1924,
    },
}
EXPECTED_CALLEES = {
    "00516b34", "0052266e", "005226b2", "00522a24", "00522f1c",
    "00523a34", "0052405c", "00524130", "00524218",
}
DRAW_CAPS_EXTRA_CALLEES = {"0051565c"}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != PINS[path]:
        raise AuditError(f"identity drift: {path}")
    return data


def _function_body(corpus: str, entry: int, next_entry: int | None) -> str:
    marker = f"/* FUN 0x{entry:08x} "
    start = corpus.find(marker)
    if start < 0:
        raise AuditError(f"0x{entry:08X}: corpus marker missing")
    if next_entry is None:
        end = len(corpus)
    else:
        end = corpus.find(f"/* FUN 0x{next_entry:08x} ", start + len(marker))
        if end < 0:
            raise AuditError(f"0x{entry:08X}: successor marker missing")
    return corpus[start:end]


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path) for path in PINS}
    functions = {
        int(row["entry"], 16): row
        for row in (json.loads(line) for line in
                    inputs[FUNCTIONS].decode("utf-8").splitlines())
        if int(row["entry"], 16) in EXPECTED
    }
    if set(functions) != set(EXPECTED):
        raise AuditError("stock stroke-cap function set changed")
    corpus = inputs[CORPUS].decode("utf-8", errors="ignore")
    records = []
    ordered = sorted(EXPECTED)
    for index, entry in enumerate(ordered):
        expected = EXPECTED[entry]
        row = functions[entry]
        expected_callees = EXPECTED_CALLEES | (
            DRAW_CAPS_EXTRA_CALLEES if entry == 0x0051C5EC else set())
        if (row["body_bytes"], row["body_sha256"], row["ranges"],
                set(row["callees"])) != (
                    expected["body_bytes"], expected["body_sha256"],
                    expected["ranges"], expected_callees):
            raise AuditError(f"0x{entry:08X}: stock body/call graph drift")
        successor = ordered[index + 1] if index + 1 < len(ordered) else 0x0051D2E0
        body = _function_body(corpus, entry, successor)
        if expected["body_sha256"] not in body.splitlines()[0]:
            raise AuditError(f"0x{entry:08X}: corpus digest marker drift")
        if (any(offset not in body for offset in expected["style_offsets"]) or
                "0x800000" not in body):
            raise AuditError(f"0x{entry:08X}: cap-style dispatch evidence drift")
        records.append({
            "entry": f"0x{entry:08X}",
            "end_exclusive": f"0x{int(row['body_end_inclusive'], 16) + 1:08X}",
            "body_bytes": expected["body_bytes"],
            "physical_bytes": expected["physical_bytes"],
            "body_sha256": expected["body_sha256"],
            "symbol": expected["symbol"],
            "style_context_offsets": expected["style_offsets"],
            "public_archive_dwarf_declaration_line": expected["public_dwarf_line"],
            "source_status": "clean-room-candidate",
            "production_routed": False,
        })

    provenance = json.loads(inputs[PROVENANCE])
    artifacts = {item["path"]: item for item in provenance["selected_artifacts"]}
    archive = artifacts.get("libraries/lib_nema_apollo5x_nemagfx.a", {})
    license_record = artifacts.get("headers/LICENSE", {})
    if (provenance["public_source_state"]["first_complete_exact_commit"] !=
            "b853fded7e545f005727e13bf2ce83018c7e242d" or
            archive.get("sha256") !=
            "109840f6e0bbeb8618a1a853966cdf68cf169620bcc4075ed7a1c86ab0d3286f" or
            license_record.get("sha256") !=
            "bb504491bd00c656c9622c9b9cfe805273c8c626ceb35480b5907983de718fbc"):
        raise AuditError("public Nema artifact/license identity drift")

    source_text = inputs[SOURCE].decode("ascii")
    header_text = inputs[HEADER].decode("ascii")
    combined = source_text + header_text
    if combined.count("SPDX-License-Identifier: MIT") != 2:
        raise AuditError("candidate MIT declarations drift")
    for symbol in ("open_cfw_nemavg_draw_start_cap",
                   "open_cfw_nemavg_draw_end_cap",
                   "open_cfw_nemavg_draw_caps"):
        if combined.count(symbol) < 2:
            raise AuditError(f"candidate API missing: {symbol}")
    if "__asm" in combined or ".byte" in combined:
        raise AuditError("candidate contains raw instruction directives")

    return {
        "schema_version": 1,
        "status": "nemavg-stroke-caps-clean-room-candidate-qualified",
        "analysis_mode": "offline; no hardware, MMIO, signing, flashing, or publishing operation",
        "provider_evidence": {
            "family": "Think Silicon NemaVG 1.1.8 co-packaged candidate",
            "public_artifact_commit": "b853fded7e545f005727e13bf2ce83018c7e242d",
            "public_archive_sha256": archive["sha256"],
            "public_dwarf_symbols": ["draw_start_cap", "draw_end_cap", "draw_caps"],
            "public_dwarf_lines": [1853, 1888, 1924],
            "license": "LicenseRef-Think-Silicon-NemaSDK-Permissive",
            "exact_stock_generating_archive_proven": False,
        },
        "stock": {
            "functions": len(records),
            "function_body_bytes": sum(item["body_bytes"] for item in records),
            "physical_bytes": sum(item["physical_bytes"] for item in records),
            "records": records,
        },
        "candidate": {
            "license": "MIT",
            "semantic_c": True,
            "raw_instruction_bytes": 0,
            "functions": 3,
            "production_routed": False,
            "software_blocker": "exact stock ABI/context binding and reviewed dual-profile placement proof remain unavailable",
        },
        "hardware_validation": "deferred by project direction",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = run_audit()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_manifest:
        SUMMARY.write_text(rendered, encoding="utf-8")
        print(f"wrote {SUMMARY}")
    else:
        print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
