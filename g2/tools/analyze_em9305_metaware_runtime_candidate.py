#!/usr/bin/env python3
"""Qualify the production-routed clean-room EM9305 runtime islands.

The analyzer is read-only.  It authenticates the two 980-byte residual
segments, their ARC instruction/caller evidence, existing provenance rows,
the isolated MIT implementation, and the fail-closed ARC package route.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
OBJDUMP = ROOT / "research/corpus/em9305/size-delta/opencfw-em9305-application-objdump.txt"
PROVENANCE = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"
CANDIDATE = ROOT / "components/shared/em9305/runtime_metaware_helpers_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
ARC_BUILD_SUMMARY = ROOT / "tools/manifests/em9305-arc-candidate-build-summary.json"
PRODUCTION_REPORT = ROOT / "components/em9305/source_overlay/build/build-report.json"

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
ISLANDS = {
    0x00302664: {
        "end": 0x0030299A,
        "size": 822,
        "sha256": "60ac29e8f3b990e27619d33532df6c1c267212f354d91489d8f725cff3ed1d86",
        "family": "metaware_arith_runtime",
    },
    0x00332FC4: {
        "end": 0x00333062,
        "size": 158,
        "sha256": "510d1c07ddec7c1d25b0c724810c8f8f586a30ee63b7df4859153cdd0d8e70fb",
        "family": "metaware_memory_runtime",
    },
}

ENTRY_FACTS = {
    0x00302664: ("memmove", "enter_s", 1),
    0x003026A8: ("udiv64_by_u32_core", "enter_s", 2),
    0x00302748: ("udiv64", "mov_s", 5),
    0x00302760: ("sdiv64", "enter_s", 1),
    0x003027C8: ("shift_left64", "bmsk.f", 8),
    0x003027F4: ("shift_right64", "bmsk.f", 14),
    0x00302820: ("stack_bounds_guard", "push_s", 1),
    0x00302844: ("udiv64_core", "b.d", 2),
    0x00332FC4: ("memcpy", "xor", 199),
    0x0033301C: ("memset", "push_s", 153),
}

REQUIRED_SYMBOLS = (
    "open_cfw_em9305_metaware_memmove_candidate",
    "open_cfw_em9305_metaware_memcpy_candidate",
    "open_cfw_em9305_metaware_memset_candidate",
    "open_cfw_em9305_metaware_udiv64_candidate",
    "open_cfw_em9305_metaware_sdiv64_candidate",
    "open_cfw_em9305_metaware_shift_left64_candidate",
    "open_cfw_em9305_metaware_shift_right64_candidate",
    "open_cfw_em9305_metaware_stack_pointer_in_bounds",
    "open_cfw_em9305_metaware_stack_guard_candidate",
)

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(\S+)(.*)$")
TARGET_RE = re.compile(r";0x([0-9a-f]+)")


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


def parse_objdump(text: str) -> dict[int, tuple[str, str, int]]:
    instructions: dict[int, tuple[str, str, int]] = {}
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            instructions[int(match.group(1), 16)] = (
                match.group(3),
                match.group(4).strip(),
                2 * len(match.group(2).split()),
            )
    if not instructions:
        raise CandidateError("authenticated objdump decoded no instructions")
    return instructions


def references_to(
    instructions: dict[int, tuple[str, str, int]],
    target: int,
) -> list[int]:
    result = []
    for address, (mnemonic, rest, _size) in instructions.items():
        targets = {int(value, 16) for value in TARGET_RE.findall(rest)}
        if target in targets and mnemonic.split(".", 1)[0].startswith(("b", "j")):
            result.append(address)
    return sorted(result)


def provenance_rows(text: str) -> dict[int, dict[str, str]]:
    rows: dict[int, dict[str, str]] = {}
    fields = (
        "start", "end", "size", "sha256", "structural_class",
        "category", "family", "confidence", "evidence",
    )
    for values in csv.reader(text.splitlines(), delimiter="\t"):
        if not values or values[0].startswith("#") or values[0] == "start":
            continue
        if len(values) != len(fields):
            raise CandidateError("residual provenance schema drift")
        row = dict(zip(fields, values))
        rows[int(row["start"], 16)] = row
    return rows


def strip_comments(source: str) -> str:
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    return re.sub(r"//[^\n]*", "", source)


def run_audit() -> dict[str, Any]:
    inputs = {
        path: authenticate(path, expected)
        for path, expected in FILE_PINS.items()
    }
    image = inputs[IMAGE]
    instructions = parse_objdump(inputs[OBJDUMP].decode())
    rows = provenance_rows(inputs[PROVENANCE].decode())
    source = CANDIDATE.read_text()
    header = HEADER.read_text()

    combined_source = source + "\n" + header
    if combined_source.count("SPDX-License-Identifier: MIT") != 2:
        raise CandidateError("candidate sources must retain MIT SPDX declarations")
    for symbol in REQUIRED_SYMBOLS:
        if len(re.findall(rf"\b{symbol}\s*\(", combined_source)) < 2:
            raise CandidateError(f"candidate declaration/definition missing: {symbol}")
    implementation = strip_comments(source)
    if re.search(r"(?<![*/])/\s*(?![*/])", implementation):
        raise CandidateError("clean-room division candidate may not use C division")
    if re.search(r"%(?!=)", implementation):
        raise CandidateError("clean-room division candidate may not use C remainder")

    arc_build = json.loads(ARC_BUILD_SUMMARY.read_text(encoding="utf-8"))
    if (
        arc_build.get("status") != "arcv2-em-candidates-target-compiled"
        or arc_build.get("target") != "ARCv2 EM"
        or not str(arc_build.get("compiler", "")).startswith(
            "arc-linux-gnu-gcc (GCC) 16.1.1"
        )
        or arc_build.get("translation_unit_count") != 8
        or arc_build.get("undefined_symbols") != []
        or arc_build.get("forbidden_runtime_imports") != []
        or arc_build.get("hardware_operations") != []
        or arc_build.get("production_routed") is not False
    ):
        raise CandidateError("ARCv2 EM candidate-build receipt changed")
    arc_rows = {
        row.get("source"): row
        for row in arc_build.get("translation_units", [])
        if isinstance(row, dict)
    }
    for candidate_source in sorted(CANDIDATE.parent.glob("*.c")):
        relative = str(candidate_source.relative_to(ROOT))
        row = arc_rows.get(relative)
        if (
            row is None
            or row.get("source_size") != candidate_source.stat().st_size
            or row.get("source_sha256") != sha256(candidate_source.read_bytes())
            or row.get("undefined_symbols") != []
        ):
            raise CandidateError(f"ARCv2 EM source receipt changed: {relative}")

    island_results: dict[str, Any] = {}
    total = 0
    for start, facts in ISLANDS.items():
        offset = APP_FILE_OFFSET + start - APP_BASE
        body = image[offset:offset + facts["size"]]
        if len(body) != facts["size"] or sha256(body) != facts["sha256"]:
            raise CandidateError(f"0x{start:08x}: official island identity drift")
        row = rows.get(start)
        if row is None:
            raise CandidateError(f"0x{start:08x}: provenance row missing")
        expected_row = (
            f"0x{facts['end']:08X}", str(facts["size"]), facts["sha256"],
            "runtime_support_code", "toolchain_or_linker_generated",
            facts["family"], "high",
        )
        actual_row = (
            row["end"], row["size"], row["sha256"], row["structural_class"],
            row["category"], row["family"], row["confidence"],
        )
        if actual_row != expected_row:
            raise CandidateError(f"0x{start:08x}: provenance assignment drift")
        total += facts["size"]
        island_results[f"0x{start:08X}"] = {
            "end_exclusive": facts["end"],
            "bytes": facts["size"],
            "sha256": facts["sha256"],
            "family": facts["family"],
        }
    if total != 980:
        raise CandidateError("MetaWare runtime island total drift")

    entry_results: dict[str, Any] = {}
    for entry, (semantic, expected_mnemonic, expected_references) in ENTRY_FACTS.items():
        instruction = instructions.get(entry)
        if instruction is None or instruction[0] != expected_mnemonic:
            raise CandidateError(f"0x{entry:08x}: entry instruction drift")
        references = references_to(instructions, entry)
        if len(references) != expected_references:
            raise CandidateError(
                f"0x{entry:08x}: reference count drift: {len(references)}"
            )
        entry_results[f"0x{entry:08X}"] = {
            "semantic": semantic,
            "entry_mnemonic": expected_mnemonic,
            "reference_count": len(references),
            "reference_sha256": sha256(
                "".join(f"{address:08x}\n" for address in references).encode()
            ),
            "reference_addresses": references if len(references) <= 20 else [],
        }

    required_vocabulary = {"divu", "macdu", "mpy", "norm", "brk_s"}
    arith_vocabulary = {
        mnemonic.split(".", 1)[0]
        for address, (mnemonic, _rest, _size) in instructions.items()
        if ISLANDS[0x00302664]["end"] > address >= 0x00302664
    }
    if not required_vocabulary <= arith_vocabulary:
        raise CandidateError("arithmetic-runtime vocabulary drift")
    for limit in (0x0080E978, 0x0080F978):
        if not any(
            f"0x{limit:x}" in rest
            for address, (_mnemonic, rest, _size) in instructions.items()
            if 0x00302664 <= address < 0x0030299A
        ):
            raise CandidateError(f"stack limit 0x{limit:08x} disappeared")

    production = json.loads(PRODUCTION_REPORT.read_text(encoding="utf-8"))
    provider_record = production.get("provider", {})
    provider_path = ROOT / str(provider_record.get("path", ""))
    provider = provider_path.read_bytes()
    accounting = production.get("accounting", {})
    application = production.get("application", {})
    if (
        production.get("status") != "em9305-runtime-production-routed"
        or production.get("target") != "ARCv2 EM"
        or production.get("production_routed") is not True
        or production.get("undefined_symbols") != []
        or production.get("hardware_operations") != []
        or production.get("hardware_validation")
        != "blocked by unavailable physical evidence"
        or len(provider) != 212_984
        or sha256(provider)
        != "1a4ccc61cae6e9b90d0eb3d694179d726c935171788167d28ea45060d7431c42"
        or provider_record.get("size") != len(provider)
        or provider_record.get("sha256") != sha256(provider)
        or accounting != {
            "production_source_bytes": 1_174,
            "generated_or_reconstructible_bytes": 1_226,
            "candidate_source_not_routed_bytes": 0,
            "typed_retained_or_external_bytes": 210_584,
            "unclassified_bytes": 0,
        }
        or sum(accounting.values()) != len(provider)
        or application.get("metaware_implementation_bytes") != 748
        or application.get("source_end_exclusive") != 0x00335FD4
        or application.get("sector_end_exclusive") != 0x00336000
        or len(production.get("metaware_entry_patches", [])) != 8
        or production.get("metaware_interior_entries_replaced_with_generated_nops")
        != [0x003026A8, 0x00302844]
    ):
        raise CandidateError("EM9305 production route receipt changed")

    return {
        "status": "production-routed",
        "read_only": True,
        "hardware_operations": False,
        "license": "MIT",
        "stock_runtime": {
            "compiler": "Synopsys MetaWare ARC T-2022.09 build 004 / LLVM 14.0.6",
            "islands": island_results,
            "total_bytes": total,
            "entries": entry_results,
        },
        "candidate": {
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
            "symbols": list(REQUIRED_SYMBOLS),
            "uses_c_division_or_remainder": False,
            "arcv2_em_target_compiled": True,
            "arcv2_em_undefined_symbols": [],
            "arcv2_em_forbidden_runtime_imports": [],
            "arcv2_em_build_receipt": str(ARC_BUILD_SUMMARY.relative_to(ROOT)),
            "production_routed": True,
            "production_build_receipt": str(PRODUCTION_REPORT.relative_to(ROOT)),
            "provider_size": len(provider),
            "provider_sha256": sha256(provider),
            "production_source_bytes": accounting["production_source_bytes"],
            "generated_or_reconstructible_bytes": accounting[
                "generated_or_reconstructible_bytes"],
            "candidate_source_not_routed_bytes": 0,
        },
        "integration_blockers": [],
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_audit()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("EM9305 MetaWare runtime islands: production-routed")
        print("reconstructible stock bytes: 980")
        print("production routing: enabled in mixed-source EM9305 provider")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
