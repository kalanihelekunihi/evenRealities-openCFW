#!/usr/bin/env python3
"""Qualify the remaining source-visible SFNT single-object tail in the 0x5D sea."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_none_batch10/runtime_cordio_ll_sea_none_batch10_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
SFNT = ROOT / "third_party/freetype/src/sfnt"
LOAD_BASE = 0x00437FE0
SOURCE_PINS = {
    "ttcmap.c": (120_864, "e321c3d6cac43fa450698f5a98456fd8e84d7da0b37ea75531ad79c3cecfe5fb"),
    "ttkern.c": (8_081, "7df687ce36895754b3b3cec950409255bb1f00b26d0c2c8107743cef47112a26"),
    "ttload.c": (52_871, "fff297b78a470479cc41994f005a7ae5acba78ab50b1aa0fdfad7b1f7ec28ef7"),
    "ttmtx.c": (12_312, "0ccf75bfa5f2306be72650425bfae36a86f3fc92c80987cdc80d59deeabc589d"),
    "ttpost.c": (17_199, "9ff630ae5a4da8558507f40ac8cce5ee132117f017568c1e23398a3cb4764bc1"),
}

ROW_RE = re.compile(
    r'\{\s*(0x[0-9A-F]+)u,\s*(0x[0-9A-F]+)u,\s*(\d+)u,\s*'
    r'"([^"]+)",\s*"([^"]+)",\s*FT_LICENSE,\s*([01])u\s*\}'
)
EXPECTED = (
    ("ttcmap.c", "tt_get_glyph_name"),
    ("ttcmap.c", "tt_cmap_unicode_init"),
    ("ttcmap.c", "tt_cmap_unicode_done"),
    ("ttcmap.c", "tt_cmap_unicode_char_index"),
    ("ttcmap.c", "tt_cmap_unicode_char_next"),
    ("ttcmap.c", "tt_face_build_cmaps"),
    ("ttkern.c", "tt_face_done_kern"),
    ("ttkern.c", "tt_face_get_kerning"),
    ("ttload.c", "tt_face_lookup_table"),
    ("ttload.c", "tt_face_goto_table"),
    ("ttload.c", "check_table_dir"),
    ("ttload.c", "tt_face_load_font_dir"),
    ("ttload.c", "tt_face_load_any"),
    ("ttload.c", "tt_face_load_generic_header"),
    ("ttload.c", "tt_face_load_head"),
    ("ttload.c", "tt_face_load_name"),
    ("ttmtx.c", "tt_face_get_metrics"),
    ("ttpost.c", "load_format_20"),
    ("ttpost.c", "load_format_25"),
    ("ttpost.c", "load_post_names"),
)

TOKENS = {
    0x005DEC32: ("FUN_005e010e(param_1,param_2,&stack0xfffffff8)",),
    0x005DEC3E: ("*(int *)(iVar1 + 0x220) + 4", "*(undefined4 *)(iVar1 + 100)", "DAT_005df8ec,0,iVar1"),
    0x005DEC5C: ("FUN_00529256(*(undefined4 *)(*param_1 + 100),param_1[5])", "param_1[5] = 0", "param_1[4] = 0"),
    0x005DEC74: ("*(int *)(*param_1 + 0x220) + 8",),
    0x005DEC82: ("*(int *)(*param_1 + 0x220) + 0xc",),
    0x005DEC90: ("param_1 + 0x1fc", "param_1 + 0x200", "iVar2 + 0x28", "iVar2 + 0x2c", "FUN_00526e5a"),
    0x005DEFB6: ("param_1 + 0x304", "param_1 + 0x308", "param_1 + 0x30c", "param_1 + 0x314"),
    0x005DEFDE: ("param_1 + 0x304", "param_1 + 0x308", "param_1 + 0x310", "param_1 + 0x314", "uVar14 == uVar7"),
    0x005DF158: ("param_1 + 0x9c", "param_1 + 0x98", "piVar1[3] != 0"),
    0x005DF182: ("FUN_005df158", "uVar2 = 0x8e", "*(undefined4 *)(iVar1 + 0xc)", "FUN_005288e0"),
    0x005DF1AE: ("local_2c = *(int *)(param_1 + 0xc) + 0xc", "local_30 < 0x36", "local_3c[0] == DAT_005dfb80", "local_40 = 0x8e"),
    0x005DF2F2: ("FUN_005df1ae", "param_1 + 0x98", "FUN_0052919c(uVar4,0x10", "FUN_00439c04"),
    0x005DF484: ("FUN_005df158(param_1)", "return 0x8e", "FUN_00528936"),
    0x005DF4D4: ("*(code **)(param_1 + 0x204)", "FUN_00528c14", "param_1 + 0xa0"),
    0x005DF504: ("FUN_005df4d4(param_1,param_2,DAT_005dfb88)",),
    0x005DF5B6: ("param_1 + 0x158", "param_1 + 0x15c", "FUN_0052919c(local_30,0x14", "PTR_DAT_005e0084"),
    0x005DFB9C: ("param_1 + 0x330", "param_1 + 0x334", "param_1 + 0x2cc", "param_1 + 0x2d0", "*param_5 = (ushort)local_28"),
    0x005DFD20: ("param_1 + 0x108", "0x101", "FUN_0052919c(uVar7,2", "local_28 + 0x27c", "local_28 + 0x284"),
    0x005DFF5A: ("param_1 + 0x108", "0x101 < iVar2 - 1U", "FUN_0052919c(uVar6,1", "param_1 + 0x27c", "param_1 + 0x280"),
    0x005E0002: ("param_1 + 0x1dc", "iVar3 == 0x20000", "iVar3 == 0x25000", "FUN_005dfd20", "FUN_005dff5a", "param_1 + 0x278"),
}

GAPS = (
    (0x005DEE14, 0x005DEFB6, "ttcmap get-info/data boundary plus tt_face_load_kern", "b75655dd3975ae2fc8e903f736c1af72683ca35eff3d7034c1d498755d6e207a"),
    (0x005DF510, 0x005DF5B6, "ttload bhed/maxp boundary", "0cf85c035b2680dabbe5c38cdddcff6d75976e8158667f1e79e85dd65aec64b7"),
    (0x005DF832, 0x005DFB9C, "ttload remainder plus ttmtx table/header loaders", "4b0b0abe68f8dc7f55a249804d6ececad8fa90ede1b2e188aaac28ee69cdfb20"),
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_prior():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch9_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_none_batch9_dependency", path)
    if spec is None or spec.loader is None:
        raise AuditError("could not load prior analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_audit() -> dict[str, Any]:
    prior_module = load_prior()
    prior = prior_module.run_audit()
    batch8 = prior_module.load_prior()
    batch7 = batch8.load_prior()
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

    sources: dict[str, str] = {}
    for module, pin in SOURCE_PINS.items():
        data = (SFNT / module).read_bytes()
        if (len(data), sha256(data)) != pin:
            raise AuditError(f"{module}: source drift")
        sources[module] = data.decode()

    candidate = CANDIDATE.read_text()
    header = HEADER.read_text()
    if (candidate + header).count("SPDX-License-Identifier: Apache-2.0") != 2:
        raise AuditError("adapter license drift")
    if "no upstream implementation copied" not in candidate:
        raise AuditError("adapter boundary drift")
    parsed = [
        (int(start, 16), int(end, 16), int(size), module, function, flag == "1")
        for start, end, size, module, function, flag in ROW_RE.findall(candidate)
    ]
    if len(parsed) != 20 or tuple((row[3], row[4]) for row in parsed) != EXPECTED:
        raise AuditError("source identity/order drift")
    if sum(row[5] for row in parsed) != 19 or parsed[-1][5]:
        raise AuditError("census boundary flag drift")

    for module in SOURCE_PINS:
        functions = [row[4] for row in parsed if row[3] == module]
        positions = []
        for function in functions:
            match = re.search(rf"(?m)^  {re.escape(function)}\s*\(", sources[module])
            if match is None:
                raise AuditError(f"{module}:{function}: definition missing")
            positions.append(match.start())
        if positions != sorted(positions):
            raise AuditError(f"{module}: source order drift")
        if "FreeType project" not in sources[module] or "LICENSE.TXT" not in sources[module]:
            raise AuditError(f"{module}: upstream terms drift")
    sfnt_single = (SFNT / "sfnt.c").read_text()
    include_order = [sfnt_single.find(f'#include "{module}"') for module in SOURCE_PINS]
    if -1 in include_order or include_order != sorted(include_order):
        raise AuditError("sfnt single-object module order drift")

    old = prior["none_group"]["records"]
    exact: dict[int, dict[str, Any]] = {}
    outside: dict[str, Any] | None = None
    total = 0
    for start, end, size, module, function, in_census in parsed:
        if end - start != size:
            raise AuditError(f"0x{start:08x}: candidate boundary drift")
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != size:
            raise AuditError(f"0x{start:08x}: image body missing")
        record = {
            "end_exclusive": end,
            "bytes": size,
            "sha256": sha256(body),
            "disposition": "upstream_freetype_source",
            "upstream_module": module,
            "upstream_function": function,
            "upstream_license": "FreeType Project License; retained file-specific notices and grants",
        }
        if in_census:
            row = old.get(f"0x{start:08X}")
            if row is None or row["disposition"] != "typed_external":
                raise AuditError(f"0x{start:08x}: residual disposition drift")
            if row["end_exclusive"] != end or row["bytes"] != size:
                raise AuditError(f"0x{start:08x}: residual boundary drift")
            exact[start] = record
            total += size
        else:
            if (start, end, size, sha256(body)) != (0x005E0002, 0x005E0068, 102, "e3d561fcfe9683ba818211ed770f519a4b3fb2a57a357598874102b0abd5fd71"):
                raise AuditError("authenticated omitted wrapper drift")
            outside = {"start": start, **record, "in_none_census": False, "claimed_exact": True}
    if (len(exact), total) != (19, 3_614) or outside is None:
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
    if (external_functions, external_bytes) != (54, 6_312):
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
            "source_order_candidate": name,
            "disposition": "typed_external_not_in_none_census",
            "claimed_exact": False,
        })

    return {
        "status": "candidate-qualified-none-batch10",
        "read_only": True,
        "hardware_operations": False,
        "none_group": {
            "functions": 198,
            "bytes": 33_644,
            "upstream_freetype_source": {"functions": 144, "bytes": 27_332},
            "batch10_source_recovered": {"functions": 19, "bytes": 3_614},
            "typed_external": {"functions": external_functions, "bytes": external_bytes},
            "records": records,
        },
        "unsupported_remainder": {
            "before": prior["unsupported_remainder"]["after"],
            "source_recovered": {"functions": 19, "bytes": 3_614},
            "after": {"functions": external_functions, "bytes": external_bytes},
        },
        "authenticated_outside_none_census": {"functions": 1, "bytes": 102, "records": [outside]},
        "uncatalogued_clusters": {
            "clusters": len(gaps),
            "bytes": sum(item["bytes"] for item in gaps),
            "records": gaps,
        },
        "source_pins": {
            module: {"path": str((SFNT / module).relative_to(ROOT)), "bytes": pin[0], "sha256": pin[1]}
            for module, pin in SOURCE_PINS.items()
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
