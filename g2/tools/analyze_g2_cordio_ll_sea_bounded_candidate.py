#!/usr/bin/env python3
"""Qualify a bounded Apache-2.0 candidate tranche from the Apollo 0x5D sea.

The corrected census is a Cordio/LL-island topology hypothesis, not an LVGL
or per-module ownership proof.  This analyzer selects only the twelve
medium-confidence direct callees, reconstructs six mechanically exact leaf
semantics, and keeps the other six behind typed unsupported boundaries.
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
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CENSUS = ROOT / "tools/manifests/g2-cordio-ll-sea-census.tsv"
SUMMARY = ROOT / "tools/manifests/g2-cordio-ll-sea-census-summary.json"
CORPUS_SUMS = ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth/SHA256SUMS"
GHIDRA_LOG = ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth/logs/apollo-30.log"
CANDIDATE = ROOT / "components/shared/cordio/runtime_cordio_ll_sea_bounded_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")

FILE_PINS = {
    IMAGE: (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    CENSUS: (61_831, "84d4e94b8a4f85b46c426b89379cc21c07b247f488aa14fdf5b0c3298f4712e6"),
    SUMMARY: (3_442, "ea77fceadc82f0a9c241c053c719a84c8b5ff9fec28cb2d72685eedfb1773ae9"),
    CORPUS_SUMS: (11_402, "3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f"),
    GHIDRA_LOG: (399_186, "6ce2cec7688130ec2fe32ed33d7eb68097c3508d527f2e2f9389827496d44b4c"),
}
LOAD_BASE = 0x00437FE0
SEA_START = 0x005D0000
SEA_END = 0x005E0000
DECLARED_CENSUS_CORPUS_SHA256 = "87d0befa001f042918bd6af83b0f50e13dd95aab160b0e520f2cb0bc55c6404e"
CURRENT_CORPUS_SHA256 = FILE_PINS[CORPUS_SUMS][1]

# start: end, bytes, hash, disposition, semantic/evidence statement
FUNCTIONS = {
    0x005D2418: (0x005D280E, 1014, "4abad2e8a2bc331f0b27b8cc6e8f5055a4920cb29d765ff5ace44c257bf8ca6a", "typed_external", "large opaque direct anchor callee"),
    0x005D2A0A: (0x005D2A18, 14, "f698cb1a9821bc58874d7f2dfd24763310ae9497b9bd77f493b694411b56953d", "concrete", "write value only when non-null destination currently holds zero"),
    0x005D2A18: (0x005D2BAE, 406, "168f0182fe0d6b70cbcd703e8231cb6ec9b00e48b82553d2268e863673db9d5d", "typed_external", "opaque fixed-point interpolation body"),
    0x005D3238: (0x005D323E, 6, "1bc76aeda36dc81b7c84feb176c2b87b9aa468bd93987be30c2fe541dc8efa1b", "concrete", "load 32-bit field at offset 0x218"),
    0x005D323E: (0x005D3248, 10, "33c4bd7f4270155eba38cf7203ee8175635beb468fd9a097ce7eb25a7aa7fe03", "concrete", "load field 0x214 and add 0x0c28"),
    0x005D3252: (0x005D3268, 22, "7ce8ffee402aeb8feb8466c3c0e9a30fdf298da4d802b163177382ad2e68efd7", "typed_external", "six-argument indirect callback dispatch"),
    0x005D3268: (0x005D3272, 10, "270d1b3d304bd7ab807a8cf08186ce1e16e7c9efe3504039bd3c225d0bf42fe5", "concrete", "two-pointer halfword load shifted to Q16"),
    0x005D3272: (0x005D327E, 12, "8f0e566d34cd259342b2d2753de94c9231ae55d649f7cf92fc0689ec629190ab", "concrete", "nested word at offset 0x190 shifted to Q16"),
    0x005D327E: (0x005D328A, 12, "f7270e12b77a660cdefb5f4fd6d11c7b5849d544773a3e18803117f50a39773f", "concrete", "nested word at offset 0x18c shifted to Q16"),
    0x005D350C: (0x005D351C, 16, "8ea6f391830530c2ad52d4854cdfc6756a0912f1a2be710e1243152fc4dc025f", "typed_external", "state clear followed by unresolved callee"),
    0x005D351C: (0x005D352E, 18, "9a093499e92e7287c8704215ebfd29314122a5c0fbf46382c28032d6c5ca50f1", "typed_external", "two unresolved ordered calls"),
    0x005D4ED0: (0x005D6D98, 7880, "f511d49d334e960c2d714c529998d5de6d3663ddba6c84c5c73e17f3a48a6934", "typed_external", "largest opaque medium-confidence body"),
}

DECOMPILE_SIGNATURES = {
    0x005D2A0A: ("(param_1 != (int *)0x0)", "(*param_1 == 0)", "*param_1 = param_2"),
    0x005D3238: ("param_1 + 0x218",),
    0x005D323E: ("param_1 + 0x214", "+ 0xc28"),
    0x005D3252: ("+ 0x224", "+ 0x20", "param_2,0,param_3,0,param_4"),
    0x005D3268: ("param_1 + 4", "+ 0x58", "+ 0xe", "<< 0x10"),
    0x005D3272: ("param_1 + 0x218", "+ 400", "<< 0x10"),
    0x005D327E: ("param_1 + 0x218", "+ 0x18c", "<< 0x10"),
    0x005D350C: ("param_1 + 0x10", "FUN_00524ba8"),
    0x005D351C: ("FUN_005d1986", "FUN_00524e7a"),
    0x005D4ED0: ("Type propagation algorithm not settling", "FUN_005d4ed0"),
    0x005D2418: ("FUN_005d328a", "FUN_005d32c0"),
    0x005D2A18: ("param_5 / 2", "FUN_00524606"),
}

REQUIRED_SYMBOLS = (
    "open_cfw_cordio_ll_sea_external_evidence",
    "open_cfw_cordio_ll_sea_external_candidate",
    "open_cfw_cordio_ll_sea_write_once_u32_candidate",
    "open_cfw_cordio_ll_sea_load_field_218_candidate",
    "open_cfw_cordio_ll_sea_load_field_214_plus_c28_candidate",
    "open_cfw_cordio_ll_sea_nested_halfword_q16_candidate",
    "open_cfw_cordio_ll_sea_nested_word_190_q16_candidate",
    "open_cfw_cordio_ll_sea_nested_word_18c_q16_candidate",
)
BEGIN_RE = re.compile(r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+)", re.I)
END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.I)


class CandidateError(RuntimeError):
    """Raised when census, binary, decompilation, or candidate facts drift."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    actual = len(data), sha256(data)
    if actual != pin:
        raise CandidateError(f"{path}: identity drift: {actual} != {pin}")
    return data


def parse_census(text: str) -> dict[int, dict[str, str]]:
    lines = [line for line in text.splitlines() if line and not line.startswith("#")]
    rows = {int(row["entry"], 16): row for row in csv.DictReader(lines, delimiter="\t")}
    if len(rows) != 300:
        raise CandidateError("corrected sea census row count drift")
    return rows


def parse_decompilations(text: str) -> dict[int, str]:
    result: dict[int, str] = {}
    current: int | None = None
    lines: list[str] = []
    for line in text.splitlines():
        begin = BEGIN_RE.search(line)
        if begin:
            current = int(begin.group(1), 16)
            lines = [line]
            continue
        if current is not None:
            lines.append(line)
            end = END_RE.search(line)
            if end:
                if int(end.group(1), 16) != current:
                    raise CandidateError("unbalanced Ghidra function markers")
                result[current] = "\n".join(lines)
                current = None
                lines = []
    if current is not None:
        raise CandidateError("unterminated Ghidra function")
    return result


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path, pin) for path, pin in FILE_PINS.items()}
    image = inputs[IMAGE]
    census = parse_census(inputs[CENSUS].decode("utf-8"))
    summary = json.loads(inputs[SUMMARY])
    decomp = parse_decompilations(inputs[GHIDRA_LOG].decode("utf-8", errors="strict"))
    source = CANDIDATE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    combined = source + "\n" + header

    if combined.count("SPDX-License-Identifier: Apache-2.0") != 2:
        raise CandidateError("candidate must retain Apache-2.0 SPDX declarations")
    for symbol in REQUIRED_SYMBOLS:
        if len(re.findall(rf"\b{symbol}\s*\(", combined)) < 2:
            raise CandidateError(f"candidate symbol missing: {symbol}")
    if "LVGL" in combined or "lvgl" in combined:
        raise CandidateError("bounded Cordio/LL candidate must not assert LVGL ownership")

    reconciliation = summary["reconciliation"]
    declared_corpus = summary["inputs"]["ghidra_sha256sums_sha256"]
    if declared_corpus != DECLARED_CENSUS_CORPUS_SHA256:
        raise CandidateError("checked-in corrected-census corpus epoch drift")
    if (
        reconciliation["sea_functions"] != 300 or
        reconciliation["sea_official_bytes"] != 52_866 or
        reconciliation["attributed_functions"] != 102 or
        reconciliation["attributed_official_bytes"] != 19_222
    ):
        raise CandidateError("corrected sea summary drift")

    records = {}
    concrete_functions = concrete_bytes = external_functions = external_bytes = 0
    for start, (end, size, digest, disposition, semantic) in FUNCTIONS.items():
        row = census.get(start)
        if row is None:
            raise CandidateError(f"0x{start:08x}: census row missing")
        if (
            int(row["body_end_exclusive"], 16) != end or
            int(row["official_opaque_bytes"]) != size or
            row["confidence"] != "medium" or
            row["evidence"] not in {"cordio-anchor-callee", "cordio-medium-callee"}
        ):
            raise CandidateError(f"0x{start:08x}: medium-confidence census drift")
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != size or sha256(body) != digest:
            raise CandidateError(f"0x{start:08x}: official function identity drift")
        decompiled = decomp.get(start)
        if decompiled is None or any(token not in decompiled for token in DECOMPILE_SIGNATURES[start]):
            raise CandidateError(f"0x{start:08x}: decompiled semantic signature drift")
        if disposition == "concrete":
            concrete_functions += 1
            concrete_bytes += size
        else:
            external_functions += 1
            external_bytes += size
            if digest not in source:
                raise CandidateError(f"0x{start:08x}: external descriptor missing")
        records[f"0x{start:08X}"] = {
            "end_exclusive": end,
            "bytes": size,
            "sha256": digest,
            "census_evidence": row["evidence"],
            "disposition": disposition,
            "semantic": semantic,
            "ownership_scope": "Cordio/LL-island topology only; per-module owner unresolved",
        }
    if (concrete_functions, concrete_bytes, external_functions, external_bytes) != (6, 64, 6, 9_356):
        raise CandidateError("bounded tranche partition drift")
    medium_rows = [row for row in census.values() if row["confidence"] == "medium"]
    if len(medium_rows) != 12 or sum(int(row["official_opaque_bytes"]) for row in medium_rows) != 9_420:
        raise CandidateError("medium-confidence census closure drift")
    if {int(row["entry"], 16) for row in medium_rows} != set(FUNCTIONS):
        raise CandidateError("bounded tranche does not cover every medium-confidence row")

    return {
        "status": "candidate-qualified-bounded",
        "read_only": True,
        "hardware_operations": False,
        "license": "Apache-2.0",
        "corrected_sea": {
            "functions": 300,
            "official_bytes": 52_866,
            "cordio_topology_functions": 102,
            "cordio_topology_bytes": 19_222,
            "lvgl_attribution": False,
            "per_module_source_attribution_proven": False,
            "checked_in_summary_corpus_sha256": declared_corpus,
            "current_authenticated_corpus_sha256": CURRENT_CORPUS_SHA256,
            "corpus_metadata_reconciled": declared_corpus == CURRENT_CORPUS_SHA256,
        },
        "medium_confidence_tranche": {
            "functions": 12,
            "bytes": 9_420,
            "concrete": {"functions": concrete_functions, "bytes": concrete_bytes},
            "typed_external": {"functions": external_functions, "bytes": external_bytes},
            "records": records,
        },
        "candidate": {
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
            "symbols": list(REQUIRED_SYMBOLS),
            "production_routed": False,
        },
        "unselected_sea_boundary": {
            "functions": 288,
            "bytes": 43_446,
            "policy": "unsupported external; not admitted by this tranche",
        },
        "integration_blockers": [
            "regenerate the corrected-census summary against the current authenticated Ghidra checksum manifest",
            "recover positive per-module source ownership for the Cordio/LL topology cluster",
            "identify exact structure ABI and bind the five reader-backed accessors",
            "replace the six opaque medium-confidence bodies before providing their boundary",
            "retain all 288 unselected sea functions as unsupported external until individually bounded",
            "authenticate Thumb placement, relocations, and every interior/function-pointer ingress before routing",
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
        print("Apollo Cordio/LL sea bounded tranche: candidate-qualified-bounded")
        print("medium-confidence: 12 functions / 9420 bytes")
        print("concrete: 6 / 64; typed external: 6 / 9356")
        print("production routing: disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
