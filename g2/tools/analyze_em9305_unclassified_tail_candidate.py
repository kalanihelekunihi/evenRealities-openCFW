#!/usr/bin/env python3
"""Exhaustively partition and qualify the 890-byte EM9305 residual tail.

The analyzer is read-only.  It authenticates all 36 formerly unclassified
spans and assigns each to either a mechanically reconstructible semantic
primitive or a fail-closed external/provider boundary.  It never promotes an
ownership claim from instruction shape alone and performs no hardware work.
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
CANDIDATE = ROOT / "components/shared/em9305/runtime_unclassified_tail_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")

FILE_PINS = {
    IMAGE: (211_948, "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"),
    OBJDUMP: (3_463_728, "13d1e9c7c0d2c2d3db9436d21ec6d90a39622446cb8ab96de5c2c01ba752916f"),
    PROVENANCE: (47_936, "2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36"),
}
APP_BASE = 0x00302400
APP_FILE_OFFSET = 0x424

# start: (end, bytes, sha256, decision, evidence-grounded semantic reason)
SPANS = {
    0x00302D80: (0x00302D82, 2, "5c36fa627b751f9f87419f9e6ed40beb9a3bab13ac1b5ec7506a34d0eb630bc4", "reconstructible_no_op", "single blink return"),
    0x00303E50: (0x00303E66, 22, "45bf7572700d4bbfc3fbc8e62e3ab40ff064cd3a27913b2c84099f5f8bb32ace", "reconstructible_accessor", "two byte-global loads"),
    0x00303F50: (0x00303F5A, 10, "8980ae8b46c457511a1acd551265be25d0ed4457161fb69592a6d08b1c860af7", "reconstructible_accessor", "byte-global load"),
    0x00303F68: (0x00303F72, 10, "dde433034095f84cff668b40e9e00b475a79d3ea4e8ebb5c8d5610c9250bb830", "reconstructible_accessor", "word-global load"),
    0x003047B0: (0x003047BE, 14, "dd355f9ea943bdb20f653513223a897ffce99fe5fb4831803483e427f5517392", "reconstructible_accessor", "byte load and equals-one normalization"),
    0x00304EB4: (0x00304EBA, 6, "e9e14747f4bb4cf4d5df295c464a409789386d829f7460a114faa12d1040af77", "reconstructible_no_op", "nop then blink return"),
    0x003069B8: (0x003069C2, 10, "23b873ad14c0a36f7037590d7dca004ec470d0f6aa37b3d478875f13d4d34793", "reconstructible_accessor", "word-global store"),
    0x00307C08: (0x00307C16, 14, "12058b627b6943f2186b687ce16539552cfd175fa2908b29cf30655799f14775", "reconstructible_accessor", "byte load and nonzero normalization"),
    0x00307D64: (0x00307D74, 16, "38561fc529c82682baff0731b072f5c8ece675e2dbbac44907e0eae4b41e4aee", "external_provider", "registers unresolved code pointer 0x00321150"),
    0x00307DD8: (0x00307DE6, 14, "52ca0e5ba9c863af57d8c8d57a18a47af3a18c1307ca3564cf76a03fde4ed7f5", "reconstructible_accessor", "byte load and nonzero normalization"),
    0x0030AE24: (0x0030AE8E, 106, "111cabb51a8da4d4b6e93bb3895ea2589a65928d1f4145f5268c1b8468a71bcf", "external_provider", "six unresolved controller callback registrations"),
    0x0030B1AC: (0x0030B1B0, 4, "524e4a6d405502d302a5d2914a638afd64fd710faf195d94cb9513cff832cf55", "external_provider", "tail branch into controller body 0x00306b70"),
    0x0030C094: (0x0030C098, 4, "ae3c1ff0998a3dd9cdc6edaccc1ca37e82a806821e9672e970522c0739ac0b51", "external_provider", "tail branch into controller body 0x00307158"),
    0x0030C228: (0x0030C2BA, 146, "3d156d34ec0a71749184874e8e7b4e1d292c4f40a54f276c584423da04b2d3c8", "external_provider", "multi-stage controller parser over eight callees"),
    0x0030F368: (0x0030F372, 10, "830b55163661d41ce8bb3f7f78cb814c8f2f94d0a8c52820ed4a17b9969d0475", "reconstructible_accessor", "halfword-global load"),
    0x0030F710: (0x0030F72E, 30, "b6fc573aff75dfb4d19d1c54c2556ca118c825fa0a2cf7f786056b908a376203", "reconstructible_mmio", "duplicate read-modify-write sets bit 23"),
    0x003100EC: (0x003100F0, 4, "f64115f823d5675ed59321d1edd7c76faddd893e7ed7914dec00cb156a6a8a04", "external_provider", "idle-hook veneer to unresolved 0x003119a8"),
    0x00310480: (0x00310496, 22, "e0ceb313ffbdbb673d630f31ce60559a3c0c75a7a6a8e864a7f0a1094fa02b1c", "reconstructible_accessor", "two byte-global stores"),
    0x003108F4: (0x003108FE, 10, "ed9b2957103a4064457232db686ebdb960b58dafa5938a1a5e9dcbc1be38458f", "reconstructible_accessor", "word-global load"),
    0x00311F84: (0x00311F8E, 10, "1bd31ce4179adf1311d0bbed749a1ebe349583d5c3f4b741a1f92e4352082a1d", "reconstructible_accessor", "halfword-global store"),
    0x003122F0: (0x003122FA, 10, "69afa780d3d2c7bc98e282585631a693838f8506b2ee6a71098de198e7dbc90c", "reconstructible_accessor", "byte-global store"),
    0x0031369C: (0x003136AA, 14, "3d5e74ca71d8c14c297c6fc5f8a0d2f1531fd4df2290278c0dc7bfc2bc47e1b3", "reconstructible_memory", "fixed 144-byte zero-fill tail call to authenticated memset"),
    0x00313760: (0x0031376A, 10, "c921eff203f0318d5b13a994876232e41fe21a222cea8af0e0cd378dd01d3cfe", "reconstructible_accessor", "halfword-global load"),
    0x00313778: (0x0031377A, 2, "5c36fa627b751f9f87419f9e6ed40beb9a3bab13ac1b5ec7506a34d0eb630bc4", "reconstructible_no_op", "single blink return"),
    0x003137F4: (0x003137FA, 6, "0cd5307fdecf41728f490ba23fc25d781b35fea1655f96143ec0a0214cf0ae1f", "reconstructible_no_op", "two adjacent blink returns"),
    0x00314728: (0x0031472C, 4, "76480290f1bed14bc2e72564d8cd92c60c121828769377b8e273db70826ccd34", "external_provider", "tail branch to unresolved shared target 0x0030fab4"),
    0x00314754: (0x00314758, 4, "656dbbb016eb58584b3cb5ce6b5ef6ac18bfcddbc473659e52b315a8acf4d563", "external_provider", "tail branch to unresolved shared target 0x0030fab4"),
    0x003151CC: (0x003151D4, 8, "15d7c55bcc02adb136a0a09e5faa4d0a06c22fbf9973583eef927924cb300f0b", "external_provider", "two tail branches to unresolved shared target 0x0030fab4"),
    0x00318200: (0x0031825A, 90, "9a49d807290a40e9bba88c523763357be2220f0f95900d0209e1bb000dceb1b6", "external_provider", "912-stride controller connection-table lookup"),
    0x0031A980: (0x0031A986, 6, "2bc255232d64dcd49926b2b18c42f157dff8aa7885cb8108394cbd8a6426b7a4", "external_provider", "zero-argument veneer to unresolved 0x0030e7f8"),
    0x0031B2F8: (0x0031B2FC, 4, "98424348882c80536c01314412424fd73d3cb362bfafed4c425d927fbfee1436", "reconstructible_accessor", "byte load at structure offset 23"),
    0x0031E8FC: (0x0031E93E, 66, "71d7d7e4bc037887bf7709e9ad44071bb4201ae3c3c8dac93d563e428e97ce36", "external_provider", "stride-24 callback-table dispatch and state advance"),
    0x003228A8: (0x003228E2, 58, "456db8aafcf0964daefa5eb57f320bfd18fb47ef039eca3ffa30e61dd052298b", "external_provider", "stride-20 callback-table dispatch and state advance"),
    0x00324AA0: (0x00324AA8, 8, "f46359ecc7aa1dce7c9df5725c518e7b0831a8b91104bda02a57225406775613", "external_provider", "field-load veneer to unresolved 0x0030e878"),
    0x0032CAC4: (0x0032CAE2, 30, "8d94fed9e19f242b548bb532e9e71c54633044a200cb03c986da614393876b72", "reconstructible_accessor", "four byte setters at structure offset 12"),
    0x00332CC0: (0x00332D2A, 106, "278b6770d19d7768fdf7a3e399aba046127b8a6ddc9f2ee0822dfdc1fb5ee4a5", "external_provider", "zero-fill entry plus unresolved controller statistics state machine"),
}

RECONSTRUCTIBLE = {start for start, facts in SPANS.items() if facts[3].startswith("reconstructible_")}
EXTERNAL = {start for start, facts in SPANS.items() if facts[3] == "external_provider"}

# Address, mnemonic, operand fragment. Exact stock hashes close the full body;
# these signatures establish the semantic fact used for each decision.
SIGNATURES = {
    0x00302D80: ((0x00302D80, "j_s", "blink"),),
    0x00303E50: ((0x00303E50, "mov_s", "0x80163b"), (0x00303E5C, "mov_s", "0x801639")),
    0x00303F50: ((0x00303F58, "ldb_s", "[r0,0]"),),
    0x00303F68: ((0x00303F70, "ld_s", "[r0,0]"),),
    0x003047B0: ((0x003047BA, "seteq", "0x1"),),
    0x00304EB4: ((0x00304EB4, "nop", ""), (0x00304EB8, "j_s", "blink")),
    0x003069B8: ((0x003069C0, "st_s", "[r1,0]"),),
    0x00307C08: ((0x00307C12, "setne", "r0,0"),),
    0x00307D64: ((0x00307D6A, "st", "0x321150"),),
    0x00307DD8: ((0x00307DE2, "setne", "r0,0"),),
    0x0030AE24: ((0x0030AE30, "st", "0x3319bc"), (0x0030AE7C, "st", "0x330ce0")),
    0x0030B1AC: ((0x0030B1AC, "b", ";0x306b70"),),
    0x0030C094: ((0x0030C094, "b", ";0x307158"),),
    0x0030C228: ((0x0030C228, "enter_s", "blink"), (0x0030C23C, "bl.d", ";0x30c094")),
    0x0030F368: ((0x0030F370, "ldh_s", "[r0,0]"),),
    0x0030F710: ((0x0030F718, "bset_s", "0x17"), (0x0030F728, "bset_s", "0x17")),
    0x003100EC: ((0x003100EC, "b", ";0x3119a8"),),
    0x00310480: ((0x00310488, "stb_s", "[r1,0]"), (0x00310494, "stb_s", "[r1,0]")),
    0x003108F4: ((0x003108FC, "ld_s", "[r0,0]"),),
    0x00311F84: ((0x00311F84, "sth", "0x805fdc"),),
    0x003122F0: ((0x003122F8, "stb_s", "[r1,0]"),),
    0x0031369C: ((0x003136A2, "mov_s", "r1,0"), (0x003136A4, "b.d", ";0x33301c"), (0x003136A8, "mov_s", "0x90")),
    0x00313760: ((0x00313768, "ldh_s", "[r0,0]"),),
    0x00313778: ((0x00313778, "j_s", "blink"),),
    0x003137F4: ((0x003137F4, "j_s", "blink"), (0x003137F8, "j_s", "blink")),
    0x00314728: ((0x00314728, "b", ";0x30fab4"),),
    0x00314754: ((0x00314754, "b", ";0x30fab4"),),
    0x003151CC: ((0x003151CC, "b", ";0x30fab4"), (0x003151D0, "b", ";0x30fab4")),
    0x00318200: ((0x0031824A, "ldb_s", "[r12,r3]"), (0x00318250, "add", "912")),
    0x0031A980: ((0x0031A980, "b.d", ";0x30e7f8"), (0x0031A984, "mov_s", "r0,0")),
    0x0031B2F8: ((0x0031B2FA, "ldb_s", "0x17"),),
    0x0031E8FC: ((0x0031E918, "mpyuw", "0x18"), (0x0031E928, "jl_s", "[r0]")),
    0x003228A8: ((0x003228BC, "mpyuw", "0x14"), (0x003228CC, "jl_s", "[r0]")),
    0x00324AA0: ((0x00324AA0, "ldb_s", "0x1"), (0x00324AA2, "b.d", ";0x30e878")),
    0x0032CAC4: ((0x0032CAC4, "mov_s", "0x28"), (0x0032CACC, "j_s.d", "blink"), (0x0032CADC, "mov_s", "0x22")),
    0x00332CC0: ((0x00332CC8, "b.d", ";0x33301c"), (0x00332CCC, "mov", "404"), (0x00332CD0, "enter_s", "r13-r15")),
}

REQUIRED_SYMBOLS = (
    "open_cfw_em9305_tail_external_evidence",
    "open_cfw_em9305_tail_external_candidate",
    "open_cfw_em9305_tail_no_op_candidate",
    "open_cfw_em9305_tail_load_u8_candidate",
    "open_cfw_em9305_tail_load_u16_candidate",
    "open_cfw_em9305_tail_load_u32_candidate",
    "open_cfw_em9305_tail_store_u8_candidate",
    "open_cfw_em9305_tail_store_u16_candidate",
    "open_cfw_em9305_tail_store_u32_candidate",
    "open_cfw_em9305_tail_load_u8_at_candidate",
    "open_cfw_em9305_tail_store_u8_at_candidate",
    "open_cfw_em9305_tail_u8_nonzero_candidate",
    "open_cfw_em9305_tail_u8_equals_candidate",
    "open_cfw_em9305_tail_set_bits32_candidate",
    "open_cfw_em9305_tail_zero_memory_candidate",
)
LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(\S+)(.*)$")


class CandidateError(RuntimeError):
    """Raised on input, partition, or candidate drift."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(path: Path, expected: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    actual = len(data), sha256(data)
    if actual != expected:
        raise CandidateError(f"{path}: identity drift: {actual} != {expected}")
    return data


def parse_objdump(text: str) -> dict[int, tuple[str, str]]:
    result: dict[int, tuple[str, str]] = {}
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            result[int(match.group(1), 16)] = match.group(3), match.group(4).strip()
    if not result:
        raise CandidateError("authenticated objdump decoded no instructions")
    return result


def provenance_rows(text: str) -> dict[int, dict[str, str]]:
    rows = {}
    for row in csv.DictReader(text.splitlines(), delimiter="\t"):
        rows[int(row["start"], 16)] = row
    return rows


def run_audit() -> dict[str, Any]:
    inputs = {path: authenticate(path, pin) for path, pin in FILE_PINS.items()}
    image = inputs[IMAGE]
    instructions = parse_objdump(inputs[OBJDUMP].decode("ascii"))
    rows = provenance_rows(inputs[PROVENANCE].decode("ascii"))
    source = CANDIDATE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    combined = source + "\n" + header

    if combined.count("SPDX-License-Identifier: MIT") != 2:
        raise CandidateError("candidate sources must retain MIT SPDX declarations")
    for symbol in REQUIRED_SYMBOLS:
        if len(re.findall(rf"\b{symbol}\s*\(", combined)) < 2:
            raise CandidateError(f"candidate symbol missing: {symbol}")
    for marker in (
        "OPEN_CFW_EM9305_TAIL_UNSUPPORTED_EXTERNAL",
        "OPEN_CFW_EM9305_TAIL_RECONSTRUCTIBLE_BYTES 260u",
        "OPEN_CFW_EM9305_TAIL_EXTERNAL_BYTES 630u",
    ):
        if marker not in combined:
            raise CandidateError(f"candidate boundary marker missing: {marker}")

    if len(SPANS) != 36 or set(SIGNATURES) != set(SPANS):
        raise CandidateError("tail partition is not exhaustive")
    if len(RECONSTRUCTIBLE) != 21 or len(EXTERNAL) != 15:
        raise CandidateError("tail decision-count drift")

    decisions: dict[str, Any] = {}
    total = reconstructible_bytes = external_bytes = 0
    for start, (end, size, digest, decision, reason) in SPANS.items():
        offset = APP_FILE_OFFSET + start - APP_BASE
        body = image[offset:offset + size]
        if end - start != size or len(body) != size or sha256(body) != digest:
            raise CandidateError(f"0x{start:08x}: span identity drift")
        row = rows.get(start)
        if row is None:
            raise CandidateError(f"0x{start:08x}: provenance row missing")
        if (
            row["end"] != f"0x{end:08X}" or row["size"] != str(size) or
            row["sha256"] != digest or
            row["ownership_category"] != "unclassified_insufficient_evidence" or
            row["confidence"] != "low"
        ):
            raise CandidateError(f"0x{start:08x}: source provenance drift")
        for address, mnemonic, fragment in SIGNATURES[start]:
            observed = instructions.get(address)
            if observed is None or observed[0] != mnemonic or fragment not in observed[1]:
                raise CandidateError(f"0x{start:08x}: semantic signature drift at 0x{address:08x}")
        if decision == "external_provider" and digest not in source:
            raise CandidateError(f"0x{start:08x}: external descriptor missing")
        total += size
        if decision.startswith("reconstructible_"):
            reconstructible_bytes += size
        else:
            external_bytes += size
        decisions[f"0x{start:08X}"] = {
            "end_exclusive": end,
            "bytes": size,
            "sha256": digest,
            "decision": decision,
            "reason": reason,
            "ownership_claim": "unchanged-unclassified",
        }
    if (total, reconstructible_bytes, external_bytes) != (890, 260, 630):
        raise CandidateError("tail decision-byte totals drift")

    return {
        "status": "candidate-qualified-exhaustive",
        "read_only": True,
        "hardware_operations": False,
        "license": "MIT",
        "tail": {
            "span_count": len(SPANS),
            "total_bytes": total,
            "decisions": decisions,
            "partition": {
                "reconstructible": {"spans": len(RECONSTRUCTIBLE), "bytes": reconstructible_bytes},
                "unsupported_external": {"spans": len(EXTERNAL), "bytes": external_bytes},
            },
        },
        "candidate": {
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
            "symbols": list(REQUIRED_SYMBOLS),
            "production_routed": False,
            "absolute_stock_addresses_embedded_in_executable_primitives": False,
        },
        "integration_blockers": [
            "bind reconstructible primitives to reviewed EM9305 RAM/MMIO symbols and exact ARC ABI veneers",
            "identify or independently replace the unavailable controller registration/parser/dispatch/statistics bodies",
            "resolve every external veneer target and prove argument/return preservation before providing it",
            "split the mixed 0x00332cc0 span so its zero-fill entry cannot imply replacement of the unresolved statistics body",
            "authenticate final link placement and all interior entry references before production routing",
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
        print("EM9305 residual tail: candidate-qualified-exhaustive")
        print("partition: 21 / 260 bytes reconstructible; 15 / 630 bytes external")
        print("production routing: disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
