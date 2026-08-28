#!/usr/bin/env python3
"""Qualify the 0x5D hop-4, island-caller, and final hop-2 residue sources."""
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
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_hop4_residue/runtime_cordio_ll_sea_hop4_residue_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
CENSUS = ROOT / "tools/manifests/g2-cordio-ll-sea-census.tsv"
LOG = ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth/logs/apollo-30.log"
PSAUX = ROOT / "third_party/freetype/src/psaux"
LOAD_BASE = 0x00437FE0
T1_PIN = (63_382, "e1d93cb47d218ccb536084932b65896a6ead9aadfdc1b648485e65524580fb74")
ROW_RE = re.compile(
    r'\{ (0x[0-9A-F]+)u, (0x[0-9A-F]+)u, (\d+)u, '
    r'OPEN_CFW_SEA_RESIDUE_(HOP2|ISLAND_CALLER|HOP4), "([^"]+)", "([^"]+)", FT_LICENSE \}'
)
SIGNATURES = {
    0x005D185E: ("param_1 + 0xc", "+ 0x3a", "+ 0x16", "FUN_00524cd6"),
    0x005D1986: ("psVar1[1] + -1", "*piVar2 ==", "*psVar1 + -1"),
    0x005D1ED0: ("param_2 < 0x100", "param_1 + 0x244", "FUN_0046cacc", "0xffffffff"),
    0x005D3068: ("0x228", "FUN_005d3018", "FUN_005d2e0c", "FUN_005d2ee4"),
    0x005D3644: ("*param_1 != 0",),
    0x005D36F0: ("param_1 + 0x14", "uVar2 * 0x14", "FUN_005246f8"),
    0x005D40C0: ("param_1 + 0x2db4", "param_1 + 0x2db0", "FUN_00524754"),
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_prior():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_anchor_hop3_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_anchor_hop3_dependency", path)
    if spec is None or spec.loader is None:
        raise AuditError("could not load prior analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_census() -> dict[int, dict[str, str]]:
    lines = [line for line in CENSUS.read_text().splitlines()
             if line and not line.startswith("#")]
    return {int(row["entry"], 16): row
            for row in csv.DictReader(lines, delimiter="\t")}


def run_audit() -> dict[str, Any]:
    prior_module = load_prior()
    prior = prior_module.run_audit()
    hop2 = prior_module.load_hop2_analyzer()
    image = hop2.authenticate(IMAGE)
    log = hop2.authenticate(LOG).decode("utf-8")
    census = parse_census()
    candidate = CANDIDATE.read_text()
    header = HEADER.read_text()
    if (candidate + header).count("SPDX-License-Identifier: Apache-2.0") != 2:
        raise AuditError("Apache research adapter declarations missing")
    if "no upstream implementation copied" not in candidate:
        raise AuditError("upstream boundary statement missing")

    sources: dict[str, str] = {}
    for path in hop2.FILE_PINS:
        if path.parent == PSAUX:
            sources[path.name] = hop2.authenticate(path).decode("utf-8")
    for path, pin in prior_module.PINS.items():
        sources[path.name] = prior_module.read_pinned(path, pin).decode("utf-8")
    t1_data = (PSAUX / "t1decode.c").read_bytes()
    if (len(t1_data), sha256(t1_data)) != T1_PIN:
        raise AuditError("t1decode.c source drift")
    sources["t1decode.c"] = t1_data.decode("utf-8")

    rows = []
    for match in ROW_RE.finditer(candidate):
        start, end, size, group, module, function = match.groups()
        rows.append((int(start, 16), int(end, 16), int(size), group, module, function))
    if len(rows) != 12 or len({row[0] for row in rows}) != 12:
        raise AuditError("evidence row partition drift")
    counts = {"HOP2": [0, 0], "ISLAND_CALLER": [0, 0], "HOP4": [0, 0]}
    records = {}
    hop2_records = hop2.run_audit()["hop2_tranche"]["records"]
    expected_evidence = {
        "HOP2": "cordio-closure-hop-2", "ISLAND_CALLER": "cordio-island-caller",
        "HOP4": "cordio-closure-hop-4",
    }
    for start, end, size, group, module, function in rows:
        census_row = census.get(start)
        if census_row is None or census_row["evidence"] != expected_evidence[group]:
            raise AuditError(f"0x{start:08x}: census class drift")
        if int(census_row["body_end_exclusive"], 16) != end or int(census_row["official_opaque_bytes"]) != size:
            raise AuditError(f"0x{start:08x}: census range drift")
        if group == "HOP2" and hop2_records[f"0x{start:08X}"]["disposition"] != "typed_external":
            raise AuditError(f"0x{start:08x}: not a final hop-2 external")
        source = sources.get(module, "")
        if re.search(rf"(?m)^  {re.escape(function)}\s*\(", source) is None:
            raise AuditError(f"{module}:{function}: source definition missing")
        if "freetype project" not in source.lower() or "license" not in source.lower():
            raise AuditError(f"{module}: upstream terms missing")
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
    if counts != {"HOP2": [3, 308], "ISLAND_CALLER": [1, 448], "HOP4": [8, 948]}:
        raise AuditError(f"source partition drift: {counts}")
    for address, tokens in SIGNATURES.items():
        begin = log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}")
        end = log.find("OPENCFW_FUNCTION_END", begin)
        body = log[begin:end]
        if begin < 0 or any(token not in body for token in tokens):
            raise AuditError(f"0x{address:08x}: semantic signature drift")

    return {
        "status": "candidate-qualified-hop4-residue",
        "read_only": True, "hardware_operations": False,
        "source_attribution": {
            "hop2_residue": {"functions": 3, "bytes": 308},
            "island_caller": {"functions": 1, "bytes": 448},
            "hop4": {"functions": 8, "bytes": 948},
            "records": records,
        },
        "unsupported_remainder": {
            "before": prior["unsupported_remainder"]["after"],
            "source_recovered": {"functions": 12, "bytes": 1_704},
            "after": {"functions": 198, "bytes": 33_644},
            "typed_external_hop2": {"functions": 0, "bytes": 0},
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
