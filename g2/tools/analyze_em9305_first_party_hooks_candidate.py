#!/usr/bin/env python3
"""Qualify the fail-closed EM9305 first-party hook-span source model.

This read-only analyzer authenticates the seven residual spans, their
provenance rows, the nine-entry QF/QK hook table, salient ARC control flow,
and the isolated MIT candidate boundary.  It performs no hardware action and
does not route the candidate into a production image.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
OBJDUMP = ROOT / "research/corpus/em9305/size-delta/opencfw-em9305-application-objdump.txt"
PROVENANCE = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"
CANDIDATE = ROOT / "components/shared/em9305/runtime_first_party_hooks_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")

FILE_PINS = {
    IMAGE: (
        211_948,
        "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9",
    ),
    OBJDUMP: (
        3_463_728,
        "13d1e9c7c0d2c2d3db9436d21ec6d90a39622446cb8ab96de5c2c01ba752916f",
    ),
    PROVENANCE: (
        47_936,
        "2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36",
    ),
}

APP_BASE = 0x00302400
APP_FILE_OFFSET = 0x424
HOOK_TABLE_START = 0x00335B94
HOOK_TABLE_END = 0x00335BB8
HOOK_TABLE_SHA256 = "1370d2789d143388ecbd5c84edf4dfaaaf2c059ff69ec59e0f68ff0df0514b51"
HOOK_TABLE_TARGETS = (
    0x0030EB8C, 0x0030ECF8, 0x0031114C,
    0x00311150, 0x003111A0, 0x003111A4,
    0x0031161C, 0x00311620, 0x003117E8,
)

SPANS = {
    0x0030482C: (
        0x003048AE, 130,
        "1aff5715814514aacc29daa8bee11dc4a20cd3ff573e312f4014b884a38d813f",
        "startup_hook_glue", "application_startup_hook", "provider-required",
    ),
    0x0030EA08: (
        0x0030EB0A, 258,
        "e7b37ea140c3ed01ba07ffb164e1d06a46189d8c2682d44e261a7f837f96d722",
        "code_fragment", "application_module_myapp", "provider-required",
    ),
    0x0030EB8C: (
        0x0030EC9A, 270,
        "ff00d26e1173283a929d94b70c2b9e179b6909a7e4cb4d48d17b973188171a4f",
        "code_function", "application_hook", "provider-required",
    ),
    0x0030ECF8: (
        0x0030EF12, 538,
        "8da28f1db4ff4d13912c78b8f6f4ddb7f36a9f93018233187d69cca3f3934d9f",
        "code_function", "application_hook", "provider-required",
    ),
    0x00311150: (
        0x00311154, 4,
        "7766b559c480d3129860a74a673038b9db4a622de9bb71c7957ee5e1837047de",
        "hook_stub", "qpc_vendor_hook", "exact-tail-branch",
    ),
    0x003111A4: (
        0x003111A8, 4,
        "5c2ae05832a4449cd2bb20f41b843eb22dae95f3f95d0d30b0236e77ebcf5f1e",
        "hook_stub", "qpc_vendor_hook", "exact-tail-branch",
    ),
    0x00311620: (
        0x00311634, 20,
        "fbb0316db14f6fc107f338a4cbf5852049003c2def1230d9f5e117e7a0a2abe4",
        "code_function", "application_hook", "exact-ordered-call-shell",
    ),
}

REQUIRED_INSTRUCTIONS = {
    0x0030482C: ("mov_s", "0x8012e4"),
    0x00304832: ("b", ";0x310944"),
    0x0030483E: ("mpyuw", "912"),
    0x00304856: ("mpyuw", "912"),
    0x00304886: ("mpyuw", "912"),
    0x0030489E: ("mpyuw", "912"),
    0x0030EA08: ("mov_s", "0x801970"),
    0x0030EACE: ("bl.d", ";0x3117d8"),
    0x0030EAD2: ("mov_s", "0xb5"),
    0x0030EB8C: ("st.aw", "blink"),
    0x0030EB90: ("bl", ";0x302e80"),
    0x0030ECF8: ("enter_s", "blink"),
    0x00311150: ("b", ";0x310798"),
    0x003111A4: ("b", ";0x30482c"),
    0x00311620: ("push_s", "blink"),
    0x00311622: ("bl", ";0x333d7c"),
    0x00311626: ("bl", ";0x3100ec"),
    0x0031162A: ("bl.d", ";0x310728"),
    0x0031162E: ("mov_s", "r0,0"),
}

REQUIRED_SYMBOLS = (
    "open_cfw_em9305_first_party_span_evidence",
    "open_cfw_em9305_startup_hook_target_candidate",
    "open_cfw_em9305_myapp_module_candidate",
    "open_cfw_em9305_vendor_resume_extension_candidate",
    "open_cfw_em9305_vendor_startup_extension_candidate",
    "open_cfw_em9305_qf_resume_internal_hook_candidate",
    "open_cfw_em9305_qf_startup_internal_hook_candidate",
    "open_cfw_em9305_qk_idle_internal_hook_candidate",
)

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(\S+)(.*)$")


class CandidateError(RuntimeError):
    """Raised when authenticated evidence or candidate constraints drift."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path, expected: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    actual = (len(data), sha256(data))
    if actual != expected:
        raise CandidateError(f"{path}: identity drift: {actual} != {expected}")
    return data


def installed_slice(image: bytes, start: int, end: int) -> bytes:
    offset = APP_FILE_OFFSET + start - APP_BASE
    return image[offset:offset + end - start]


def parse_objdump(text: str) -> dict[int, tuple[str, str, int]]:
    instructions: dict[int, tuple[str, str, int]] = {}
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            instructions[int(match.group(1), 16)] = (
                match.group(3), match.group(4).strip(),
                2 * len(match.group(2).split()),
            )
    if not instructions:
        raise CandidateError("authenticated objdump decoded no instructions")
    return instructions


def provenance_rows(text: str) -> dict[int, dict[str, str]]:
    fields = (
        "start", "end", "size", "sha256", "structural_class",
        "category", "family", "confidence", "evidence",
    )
    rows: dict[int, dict[str, str]] = {}
    for values in csv.reader(text.splitlines(), delimiter="\t"):
        if not values or values[0].startswith("#") or values[0] == "start":
            continue
        if len(values) != len(fields):
            raise CandidateError("residual provenance schema drift")
        row = dict(zip(fields, values))
        rows[int(row["start"], 16)] = row
    return rows


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path, pin) for path, pin in FILE_PINS.items()}
    image = inputs[IMAGE]
    instructions = parse_objdump(inputs[OBJDUMP].decode("ascii"))
    rows = provenance_rows(inputs[PROVENANCE].decode("ascii"))
    source = CANDIDATE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")

    if (source + header).count("SPDX-License-Identifier: MIT") != 2:
        raise CandidateError("candidate sources must retain MIT SPDX declarations")
    combined = source + "\n" + header
    for symbol in REQUIRED_SYMBOLS:
        if len(re.findall(rf"\b{symbol}\s*\(", combined)) < 2:
            raise CandidateError(f"candidate declaration/definition missing: {symbol}")
    for marker in (
        "OPEN_CFW_EM9305_CANDIDATE_UNRESOLVED_PROVIDER",
        "OPEN_CFW_EM9305_MODEL_PROVIDER_REQUIRED",
        "OPEN_CFW_EM9305_MODEL_EXACT_TAIL_BRANCH",
        "OPEN_CFW_EM9305_MODEL_EXACT_ORDERED_CALL_SHELL",
    ):
        if marker not in combined:
            raise CandidateError(f"candidate fail-closed marker missing: {marker}")

    table = installed_slice(image, HOOK_TABLE_START, HOOK_TABLE_END)
    if len(table) != 36 or sha256(table) != HOOK_TABLE_SHA256:
        raise CandidateError("QF/QK hook table identity drift")
    targets = struct.unpack("<9I", table)
    if targets != HOOK_TABLE_TARGETS:
        raise CandidateError("QF/QK hook table target order drift")

    span_results: dict[str, Any] = {}
    total = 0
    for start, (end, size, digest, structural, family, model) in SPANS.items():
        body = installed_slice(image, start, end)
        if len(body) != size or sha256(body) != digest:
            raise CandidateError(f"0x{start:08x}: official span identity drift")
        row = rows.get(start)
        if row is None:
            raise CandidateError(f"0x{start:08x}: provenance row missing")
        observed = (
            row["end"], row["size"], row["sha256"], row["structural_class"],
            row["category"], row["family"], row["confidence"],
        )
        expected = (
            f"0x{end:08X}", str(size), digest, structural,
            "first_party_application_retained", family, "high",
        )
        if observed != expected:
            raise CandidateError(f"0x{start:08x}: provenance assignment drift")
        if digest not in source:
            raise CandidateError(f"0x{start:08x}: candidate evidence descriptor drift")
        total += size
        span_results[f"0x{start:08X}"] = {
            "end_exclusive": end,
            "bytes": size,
            "sha256": digest,
            "family": family,
            "source_model": model,
        }
    if total != 1_224 or len(span_results) != 7:
        raise CandidateError("first-party span census drift")

    for address, (mnemonic, operand_fragment) in REQUIRED_INSTRUCTIONS.items():
        observed = instructions.get(address)
        if observed is None or observed[0] != mnemonic or operand_fragment not in observed[1]:
            raise CandidateError(f"0x{address:08x}: salient instruction drift")

    return {
        "status": "candidate-qualified-fail-closed",
        "read_only": True,
        "hardware_operations": False,
        "license": "MIT",
        "stock_first_party": {
            "spans": span_results,
            "span_count": len(span_results),
            "total_bytes": total,
            "hook_table": {
                "start": HOOK_TABLE_START,
                "end_exclusive": HOOK_TABLE_END,
                "sha256": HOOK_TABLE_SHA256,
                "targets": list(targets),
            },
        },
        "candidate": {
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
            "symbols": list(REQUIRED_SYMBOLS),
            "production_routed": False,
            "provider_required_spans": 4,
            "exact_tail_branch_spans": 2,
            "exact_ordered_call_shell_spans": 1,
            "idle_final_argument": 0,
        },
        "integration_blockers": [
            "recover first-party behavior and exact ARC ABI for the four provider-required spans",
            "identify all three QK idle callees by redistributable source provenance before production binding",
            "recover the QF resume target at 0x00310798 and validate its argument and return contract",
            "define clean-room MyApp active-object state/event semantics and assertion policy",
            "authenticate link placement, relocations, callback registration, and startup ordering before production routing",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("EM9305 first-party hooks: candidate-qualified-fail-closed")
        print("authenticated spans: 7 / 1224 bytes")
        print("production routing: disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
