#!/usr/bin/env python3
"""Qualify the remaining census-visible FreeType ttcmap bodies in the 0x5D sea."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_none_batch9/runtime_cordio_ll_sea_none_batch9_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
SOURCE = ROOT / "third_party/freetype/src/sfnt/ttcmap.c"
SOURCE_PIN = (120_864, "e321c3d6cac43fa450698f5a98456fd8e84d7da0b37ea75531ad79c3cecfe5fb")
LOAD_BASE = 0x00437FE0

ROW_RE = re.compile(
    r'\{\s*(0x[0-9A-F]+)u,\s*(0x[0-9A-F]+)u,\s*(\d+)u,\s*'
    r'"([^"]+)",\s*"([^"]+)",\s*FT_LICENSE\s*\}'
)
EXPECTED = (
    "tt_cmap0_validate",
    "tt_cmap2_validate",
    "tt_cmap2_get_subheader",
    "tt_cmap8_validate",
    "tt_cmap8_char_index",
    "tt_cmap8_char_next",
    "tt_cmap12_validate",
    "tt_cmap12_next",
    "tt_cmap13_validate",
    "tt_cmap13_next",
    "tt_cmap14_ensure",
    "tt_cmap14_validate",
    "tt_cmap14_char_map_def_binary",
    "tt_cmap14_char_map_nondef_binary",
    "tt_cmap14_find_variant",
    "tt_cmap14_char_var_index",
    "tt_cmap14_def_char_count",
    "tt_cmap14_get_def_chars",
    "tt_cmap14_get_nondef_chars",
    "tt_cmap14_variant_chars",
)

TOKENS = {
    0x005DC542: ("uVar2 < 0x106", "uVar2 < 0x100", "FUN_00524f84(param_2,0x10)"),
    0x005DC600: ("uVar7 < 0x206", "CONCAT11(uVar3,bVar2) >> 3", "uVar12 * 8 + 8", "FUN_00524f84(param_2,9)"),
    0x005DC790: ("param_2 < 0x10000", "param_1 + 0x206", "param_2 >> 8", "& 0xfffffff8"),
    0x005DD584: ("param_1 + 0x2010U", "pbVar11 = (byte *)(param_1 + 0x2010)", "uVar12 >> 0x13", "0x80U >> (uVar12 & 7)"),
    0x005DD780: ("iVar1 + 0x200f", "pbVar4 = (byte *)(iVar1 + 0x2010)", "return (param_2 + uVar5) - uVar3"),
    0x005DD832: ("*param_2 == 0xffffffff", "iVar3 + 0x2010", "*param_2 = uVar5"),
    0x005DDB3A: ("param_1 + 0x10U", "(uVar5 - 0x10) / 0xc", "pbVar7 = pbVar7 + 0xc", "FUN_00524f84(param_2,0x10)"),
    0x005DDC74: ("param_1[7] != -1", "param_1[9]", "param_1[10]", "*(undefined1 *)(param_1 + 6) = 0"),
    0x005DDEF8: ("param_1 + 0x10U", "(uVar5 - 0x10) / 0xc", "uVar8 < uVar10", "*(uint *)(param_2 + 0x90) <="),
    0x005DE026: ("param_1[7] + 1", "param_1[8] = uVar2", "param_1[9] = uVar4", "*(undefined1 *)(param_1 + 6) = 0"),
    0x005DE270: ("*(uint *)(param_1 + 0x1c) < param_2", "FUN_0052919c(param_3,4", "*(uint *)(param_1 + 0x1c) = param_2"),
    0x005DE2CE: ("param_1 + 10U", "0x10ffff", "/ 5 < uVar6", "pbVar7 = pbVar7 + 0xb"),
    0x005DE590: ("param_1[uVar3 * 4 + 6]", "param_1[uVar3 * 4 + 7] + uVar4", "return 1"),
    0x005DE5EE: ("param_1[uVar3 * 5 + 6]", "return CONCAT11(param_1[uVar3 * 5 + 7],param_1[uVar3 * 5 + 8])"),
    0x005DE652: ("param_1[uVar3 * 0xb + 6]", "return param_1 + uVar3 * 0xb + 7"),
    0x005DE6AC: ("FUN_005de652", "FUN_005de590", "FUN_005de5ee", "*(code **)(*(int *)(param_2 + 0xc) + 0xc)"),
    0x005DE8C2: ("pbVar3 = param_1 + 7", "iVar1 = *pbVar3 + 1 + iVar1", "pbVar3 = pbVar3 + 4"),
    0x005DE8F6: ("FUN_005de8c2(param_2)", "FUN_005de270(param_1,iVar1 + 1", "*puVar3 = 0"),
    0x005DE970: ("FUN_005de270(param_1,uVar3 + 1)", "pbVar4 = pbVar4 + 5", "*(undefined4 *)(iVar1 + uVar2 * 4) = 0"),
    0x005DE9D2: ("FUN_005de652", "FUN_005de970", "FUN_005de8f6", "FUN_005de270", "return CONCAT44(local_28,iVar6)"),
}

GAPS = (
    (0x005DC5B4, 0x005DC600, "format-0 accessors/info/class before format 2", "c7fcfe303c1b717de2bb6cac4053e3b4336325dbb00458c120e7beb7f086845f"),
    (0x005DC7E2, 0x005DC99C, "format-2 tail/info/class plus format-4 init", "57b1c31f740f1b6693cc595c84d9e29d0fd42d09ebac24824b2afd8936811694"),
    (0x005DD3C6, 0x005DD584, "format-4 tail/class and format-6 bodies before format 8", "dafa42d604451c611de7270afc471c62a7bf735293fce58b9e43d37485a588e4"),
    (0x005DD934, 0x005DDB3A, "format-8 info/class, format-10 bodies, and format-12 init", "b213480e9a1c65574db89ee12ce253a8e70ad28d9774d34d3022d34fd91cae2c"),
    (0x005DDD38, 0x005DDEF8, "format-12 mapper/wrappers/info/class and format-13 init", "5e6e6e45dbab36edc08ba26bd221c3180eab1eba9c2cc6fac2e964129c4ed983"),
    (0x005DE0CA, 0x005DE270, "format-13 mapper/wrappers/info/class and format-14 done", "c91b20fbec66f407348d606dc9d92cb9c6af7560ab2aa8ff7b2081e5935c57fb"),
    (0x005DE2A8, 0x005DE2CE, "format-14 init", "4684c42647c5f14b91f337e21d4545165393ff79e328b379c907d25c08acc357"),
    (0x005DE576, 0x005DE590, "format-14 char-index/next/info stubs", "314a26aa593b50b07721fedb21d3efd359459974c846f1e1cbdd5dd7573b4cfd"),
    (0x005DE72A, 0x005DE8C2, "format-14 default/variant enumeration helpers", "e286e248ce80ed7984a3ef3b3764e796f72a792a7417824e88b7778eef2599ef"),
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_prior():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch8_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_none_batch8_dependency", path)
    if spec is None or spec.loader is None:
        raise AuditError("could not load prior analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_audit() -> dict[str, Any]:
    prior_module = load_prior()
    prior = prior_module.run_audit()
    batch7 = prior_module.load_prior()
    batch6 = batch7.load_prior()
    batch5 = batch6.load_prior()
    batch4 = batch5.load_prior()
    batch3 = batch4.load_prior()
    batch2 = batch3.load_prior()
    batch1 = batch2.load_prior()
    hop4 = batch1.load_prior()
    anchor = hop4.load_prior()
    hop2 = anchor.load_hop2_analyzer()
    image = hop2.authenticate(hop4.IMAGE)
    log = batch3.pinned(batch3.LOG31).decode()

    data = SOURCE.read_bytes()
    if (len(data), sha256(data)) != SOURCE_PIN:
        raise AuditError("ttcmap source drift")
    source = data.decode()
    candidate = CANDIDATE.read_text()
    header = HEADER.read_text()
    if (candidate + header).count("SPDX-License-Identifier: Apache-2.0") != 2:
        raise AuditError("adapter license drift")
    if "no upstream implementation copied" not in candidate:
        raise AuditError("adapter boundary drift")

    parsed = [
        (int(start, 16), int(end, 16), int(size), module, function)
        for start, end, size, module, function in ROW_RE.findall(candidate)
    ]
    if len(parsed) != 20 or tuple(row[4] for row in parsed) != EXPECTED:
        raise AuditError("source identity/order drift")
    if any(row[3] != "ttcmap.c" for row in parsed):
        raise AuditError("source module drift")

    positions = []
    for function in EXPECTED:
        match = re.search(rf"(?m)^  {re.escape(function)}\s*\(", source)
        if match is None:
            raise AuditError(f"ttcmap.c:{function}: definition missing")
        positions.append(match.start())
    if positions != sorted(positions):
        raise AuditError("upstream source order drift")
    if "FreeType project" not in source or "LICENSE.TXT" not in source:
        raise AuditError("upstream terms drift")

    old = prior["none_group"]["records"]
    exact: dict[int, dict[str, Any]] = {}
    total = 0
    for start, end, size, module, function in parsed:
        row = old.get(f"0x{start:08X}")
        if row is None or row["disposition"] != "typed_external":
            raise AuditError(f"0x{start:08x}: residual disposition drift")
        if row["end_exclusive"] != end or row["bytes"] != size or end - start != size:
            raise AuditError(f"0x{start:08x}: residual boundary drift")
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != size:
            raise AuditError(f"0x{start:08x}: image body missing")
        total += size
        exact[start] = {
            "end_exclusive": end,
            "bytes": size,
            "sha256": sha256(body),
            "disposition": "upstream_freetype_source",
            "upstream_module": module,
            "upstream_function": function,
            "upstream_license": "FreeType Project License; retained file-specific notices and grants",
        }
    if (len(exact), total) != (20, 4_542):
        raise AuditError("batch accounting drift")

    for address, tokens in TOKENS.items():
        begin = log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}")
        end = log.find("OPENCFW_FUNCTION_END", begin)
        body = log[begin:end]
        if begin < 0 or end < 0 or any(token not in body for token in tokens):
            raise AuditError(f"0x{address:08x}: semantic signature drift")

    records: dict[str, dict[str, Any]] = {}
    external_functions = 0
    external_bytes = 0
    for key, row in old.items():
        address = int(key, 16)
        records[key] = exact.get(address, row)
        if records[key]["disposition"] == "typed_external":
            external_functions += 1
            external_bytes += records[key]["bytes"]
    if (external_functions, external_bytes) != (73, 9_926):
        raise AuditError("residual accounting drift")

    gaps = []
    for start, end, name, pin in GAPS:
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != end - start or sha256(body) != pin:
            raise AuditError(f"0x{start:08x}: uncatalogued cluster drift")
        gaps.append({
            "start": start,
            "end_exclusive": end,
            "bytes": end - start,
            "sha256": pin,
            "source_order_candidate": f"ttcmap.c:{name}",
            "disposition": "typed_external_not_in_none_census",
            "claimed_exact": False,
        })

    return {
        "status": "candidate-qualified-none-batch9",
        "read_only": True,
        "hardware_operations": False,
        "none_group": {
            "functions": 198,
            "bytes": 33_644,
            "upstream_freetype_source": {"functions": 125, "bytes": 23_718},
            "batch9_source_recovered": {"functions": 20, "bytes": 4_542},
            "typed_external": {"functions": external_functions, "bytes": external_bytes},
            "records": records,
        },
        "unsupported_remainder": {
            "before": prior["unsupported_remainder"]["after"],
            "source_recovered": {"functions": 20, "bytes": 4_542},
            "after": {"functions": external_functions, "bytes": external_bytes},
        },
        "uncatalogued_clusters": {
            "clusters": len(gaps),
            "bytes": sum(item["bytes"] for item in gaps),
            "records": gaps,
        },
        "source_pin": {
            "path": str(SOURCE.relative_to(ROOT)),
            "bytes": SOURCE_PIN[0],
            "sha256": SOURCE_PIN[1],
        },
        "adapter": {
            "license": "Apache-2.0",
            "production_routed": False,
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
