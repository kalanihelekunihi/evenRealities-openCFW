#!/usr/bin/env python3
"""Qualify exact FreeType identities in the 0x5D anchors and hop-3 closure."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_anchor_hop3/runtime_cordio_ll_sea_anchor_hop3_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
CENSUS = ROOT / "tools/manifests/g2-cordio-ll-sea-census.tsv"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOG = ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth/logs/apollo-30.log"
PSAUX = ROOT / "third_party/freetype/src/psaux"
LOAD_BASE = 0x00437FE0

PINS = {
    PSAUX / "cffdecode.c": (71_404, "315e935a933a775666da68062c6f61f1fd9beeb23d98da3b12ed4ba3d0b42d91"),
    PSAUX / "psblues.c": (20_978, "cdd88702b10e3eca64d80596452a8f0716769a8739786792cea416dee60047ec"),
    PSAUX / "pserror.c": (3_013, "5ef50adbc937e4b3601b5205dbad4919e8d6bd90a6c666621efb555c0747b990"),
    PSAUX / "psfont.c": (20_822, "1a06c6bfeedfdf30c82700afe235fb5966f7eb57511fe0ae50c83ed66492a97a"),
    PSAUX / "pshints.c": (67_010, "6e71b7fabb76d6609f38622c65c4f86f6acd53513958950bf3a53c4faca7ee42"),
}
ROW_RE = re.compile(
    r'\{ (0x[0-9A-F]+)u, (0x[0-9A-F]+)u, (\d+)u, '
    r'OPEN_CFW_SEA_(ANCHOR|HOP2_REFINEMENT|HOP3), "([^"]+)", "([^"]+)", FT_LICENSE \}'
)

SIGNATURES = {
    0x005D2196: ("param_2 < 0x100", "param_1 + 0x4a4", "return 0xffffffff"),
    0x005D232C: ("FUN_005d232c",),
    0x005D2418: ("FUN_005d328a", "FUN_005d32c0"),
    0x005D2828: ("uVar4 * 0x14", "FUN_005d3644", "FUN_005d36ae"),
    0x005D2A0A: ("param_1 != (int *)0x0", "*param_1 == 0", "*param_1 = param_2"),
    0x005D2A18: ("param_5 / 2", "FUN_00524606"),
    0x005D352E: ("param_4 - param_2", "param_3 - param_1", ">> 0x10"),
    0x005D36B8: ("0xf1c", "param_2 + 0xb8"),
    0x005D4B24: ("param_2 < 0x61", "+ 7 >> 3", "0x12"),
    0x005D4B78: ("0xff", "-param_2 & 7U"),
    0x005D4ED0: ("Type propagation algorithm not settling", "FUN_005d4ed0"),
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_hop2_analyzer():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_hop2_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_hop2_dependency", path)
    if spec is None or spec.loader is None:
        raise AuditError("could not load hop-2 dependency")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    if (len(data), sha256(data)) != pin:
        raise AuditError(f"{path}: upstream source drift")
    return data


def parse_census() -> dict[int, dict[str, str]]:
    lines = [line for line in CENSUS.read_text().splitlines()
             if line and not line.startswith("#")]
    return {int(row["entry"], 16): row
            for row in csv.DictReader(lines, delimiter="\t")}


def run_audit() -> dict[str, Any]:
    hop2 = load_hop2_analyzer()
    prior = hop2.run_audit()
    image = hop2.authenticate(IMAGE)
    log = hop2.authenticate(LOG).decode("utf-8")
    census = parse_census()
    candidate = CANDIDATE.read_text()
    header = HEADER.read_text()
    if (candidate + header).count("SPDX-License-Identifier: Apache-2.0") != 2:
        raise AuditError("research adapter Apache declarations missing")
    if "no upstream body is copied" not in candidate:
        raise AuditError("upstream boundary statement missing")

    sources = {path.name: read_pinned(path, pin).decode("utf-8")
               for path, pin in PINS.items()}
    for path in hop2.FILE_PINS:
        if path.parent == PSAUX:
            sources[path.name] = hop2.authenticate(path).decode("utf-8")
    for module, source in sources.items():
        if "freetype project" not in source.lower() or "license" not in source.lower():
            raise AuditError(f"{module}: retained upstream terms missing")

    parsed = []
    for match in ROW_RE.finditer(candidate):
        start, end, size, group, module, function = match.groups()
        parsed.append((int(start, 16), int(end, 16), int(size), group, module, function))
    if len(parsed) != 45 or len({row[0] for row in parsed}) != 45:
        raise AuditError("research adapter evidence partition drift")

    counts = {"ANCHOR": [0, 0], "HOP2_REFINEMENT": [0, 0], "HOP3": [0, 0]}
    records: dict[str, Any] = {}
    prior_records = prior["hop2_tranche"]["records"]
    for start, end, size, group, module, function in parsed:
        row = census.get(start)
        if row is None or int(row["body_end_exclusive"], 16) != end or int(row["official_opaque_bytes"]) != size:
            raise AuditError(f"0x{start:08x}: census range drift")
        if group == "ANCHOR" and row["evidence"] not in {"cordio-anchor-callee", "cordio-medium-callee"}:
            raise AuditError(f"0x{start:08x}: anchor class drift")
        if group == "HOP2_REFINEMENT":
            if row["evidence"] != "cordio-closure-hop-2":
                raise AuditError(f"0x{start:08x}: hop-2 class drift")
            if prior_records[f"0x{start:08X}"]["disposition"] != "typed_external":
                raise AuditError(f"0x{start:08x}: not a prior external refinement")
        if group == "HOP3" and row["evidence"] != "cordio-closure-hop-3":
            raise AuditError(f"0x{start:08x}: hop-3 class drift")
        source = sources.get(module)
        if source is None or re.search(rf"(?m)^  {re.escape(function)}\s*\(", source) is None:
            raise AuditError(f"{module}:{function}: upstream definition missing")
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != size or f"OPENCFW_FUNCTION_BEGIN entry={start:08x}" not in log:
            raise AuditError(f"0x{start:08x}: authenticated body missing")
        counts[group][0] += 1
        counts[group][1] += size
        records[f"0x{start:08X}"] = {
            "end_exclusive": end, "bytes": size, "sha256": sha256(body),
            "source_class": group.lower(), "upstream_module": module,
            "upstream_function": function,
            "upstream_license": "FreeType Project License; retained file-specific notices and grants",
        }
    if counts != {"ANCHOR": [12, 9_420], "HOP2_REFINEMENT": [11, 2_854], "HOP3": [22, 3_400]}:
        raise AuditError(f"source partition drift: {counts}")
    for address, tokens in SIGNATURES.items():
        begin = log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}")
        end = log.find("OPENCFW_FUNCTION_END", begin)
        body = log[begin:end]
        if begin < 0 or any(token not in body for token in tokens):
            raise AuditError(f"0x{address:08x}: semantic signature drift")

    return {
        "status": "candidate-qualified-anchor-hop3",
        "read_only": True,
        "hardware_operations": False,
        "source_attribution": {
            "anchors": {"functions": 12, "bytes": 9_420},
            "hop2_refinement": {"functions": 11, "bytes": 2_854},
            "hop3": {"functions": 22, "bytes": 3_400},
            "records": records,
        },
        "unsupported_remainder": {
            "before": {"functions": 243, "bytes": 41_602},
            "source_recovered": {"functions": 33, "bytes": 6_254},
            "after": {"functions": 210, "bytes": 35_348},
            "unselected_after_hop3": {"functions": 207, "bytes": 35_040},
            "typed_external_hop2": {"functions": 3, "bytes": 308},
        },
        "adapter": {
            "license": "Apache-2.0", "production_routed": False,
            "upstream_implementation_license_retained": True,
            "source": str(CANDIDATE.relative_to(ROOT)),
            "header": str(HEADER.relative_to(ROOT)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
