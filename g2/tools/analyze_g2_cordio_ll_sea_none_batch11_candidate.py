#!/usr/bin/env python3
"""Qualify the complete census-visible psconv/psobjs sequence in the 0x5D sea."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_none_batch11/runtime_cordio_ll_sea_none_batch11_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
PSAUX = ROOT / "third_party/freetype/src/psaux"
LOAD_BASE = 0x00437FE0
SOURCE_PINS = {
    "psconv.c": (12_574, "1770ebf41ef066333aeef2f3d0a30b765d3f649c2ac1e85fac9dd98802058f5d"),
    "psobjs.c": (75_816, "6054c46ea381596e3eec22f0c13f8aaff8a6390fa33bad619dadaae7c0cf578e"),
}

ROW_RE = re.compile(
    r'\{\s*(0x[0-9A-F]+)u,\s*(0x[0-9A-F]+)u,\s*(\d+)u,\s*'
    r'"([^"]+)",\s*"([^"]+)",\s*FT_LICENSE\s*\}'
)
EXPECTED = (
    ("psconv.c", "PS_Conv_Strtol"), ("psconv.c", "PS_Conv_ToInt"),
    ("psconv.c", "PS_Conv_ToFixed"), ("psconv.c", "PS_Conv_StringDecode"),
    ("psconv.c", "PS_Conv_ASCIIHexDecode"), ("psconv.c", "PS_Conv_EexecDecode"),
    ("psobjs.c", "shift_elements"), ("psobjs.c", "reallocate_t1_table"),
    ("psobjs.c", "ps_table_add"), ("psobjs.c", "ps_table_done"),
    ("psobjs.c", "skip_comment"), ("psobjs.c", "skip_spaces"),
    ("psobjs.c", "skip_literal_string"), ("psobjs.c", "skip_string"),
    ("psobjs.c", "skip_procedure"), ("psobjs.c", "ps_parser_skip_PS_token"),
    ("psobjs.c", "ps_parser_skip_spaces"), ("psobjs.c", "ps_parser_to_token"),
    ("psobjs.c", "ps_parser_to_token_array"), ("psobjs.c", "ps_tocoordarray"),
    ("psobjs.c", "ps_tofixedarray"), ("psobjs.c", "ps_tobool"),
    ("psobjs.c", "ps_parser_load_field"), ("psobjs.c", "ps_parser_load_field_table"),
    ("psobjs.c", "ps_parser_to_int"), ("psobjs.c", "ps_parser_to_bytes"),
    ("psobjs.c", "t1_builder_init"), ("psobjs.c", "t1_builder_done"),
    ("psobjs.c", "t1_builder_check_points"), ("psobjs.c", "t1_builder_add_point"),
    ("psobjs.c", "t1_builder_add_point1"), ("psobjs.c", "t1_builder_add_contour"),
    ("psobjs.c", "t1_builder_start_point"), ("psobjs.c", "cff_builder_init"),
    ("psobjs.c", "cff_check_points"), ("psobjs.c", "cff_builder_add_point"),
    ("psobjs.c", "cff_builder_add_point1"), ("psobjs.c", "cff_builder_add_contour"),
    ("psobjs.c", "cff_builder_start_point"), ("psobjs.c", "ps_builder_init"),
)

TOKENS = {
    0x005D008E: ("0x7fffffff / param_3", "DAT_005d070c", "cVar1 < param_3"),
    0x005D018A: ("FUN_005d008e(&local_18,param_2,10)", "*local_18 == '#'", "*param_1 = local_18"),
    0x005D01DE: ("0x3e9", "0x8000", "FUN_00524754"),
    0x005D0414: ("uVar6 = uVar1 | uVar6 << 4", "uVar6 << 0x17", "param_4 << 1"),
    0x005D049E: ("0xce6d", "0x58bf", "& 0xffff"),
    0x005D04E8: ("FUN_0052919c", "FUN_00439c04", "FUN_00529256"),
    0x005D0574: ("piVar2 = (int *)param_1[6]", "*piVar2 = *piVar2 + (iVar1 - param_2)"),
    0x005D0596: ("FUN_00529148", "FUN_005d0574", "param_1[2] = param_2"),
    0x005D05E6: ("0x400 & 0xfffffc00", "param_1[6] + param_2 * 4", "FUN_00439be4"),
    0x005D0682: ("FUN_00529148", "FUN_005d0574", "param_1[2] = param_1[1]"),
    0x005D071C: ("*pcVar1 != '\\r'", "*pcVar1 != '\\n'"),
    0x005D0736: ("*local_10 != '\\t'", "*local_10 != '\\f'", "*local_10 != '%'"),
    0x005D0794: ("bVar1 != 0x5c", "bVar1 != 0x28", "*pbVar5 - 0x30 < 8"),
    0x005D0814: ("*local_18 - 0x30 < 10", "*local_18 != 0x3e"),
    0x005D087C: ("cVar1 == '%'", "cVar1 == '('", "cVar1 == '{'"),
    0x005D08F6: ("*local_18 == '['", "*local_18 == '{'", "local_18[1] == '<'"),
    0x005D0A68: ("FUN_005d0736(param_1",),
    0x005D0A72: ("*(undefined1 *)(param_2 + 2) = 0", "cVar1 == '('", "cVar1 == '['"),
    0x005D0B7C: ("*param_4 = -1", "puVar1 = puVar1 + 3", "/ 0xc"),
    0x005D0C04: ("cVar3 = ']'", "cVar3 = '}'", "FUN_005d01de"),
    0x005D0CC2: ("cVar4 = ']'", "cVar4 = '}'", "FUN_005d01de"),
    0x005D0D84: ("*pcVar2 == 't'", "*pcVar2 == 'f'", "pcVar2 = pcVar2 + 6"),
    0x005D0DE0: ("FUN_005d0a72", "FUN_005d018a", "FUN_005d01de", "FUN_00529256"),
    0x005D10C4: ("local_1a0 [96]", "local_1c4 < 0", "FUN_005d0de0"),
    0x005D1190: ("FUN_005d0a68", "FUN_005d018a"),
    0x005D11A4: ("*local_20 != '<'", "FUN_005d0414", "*local_20 != '>'"),
    0x005D128C: ("param_1 + 0x13", "DAT_005d1e98", "param_1[0x12]"),
    0x005D1306: ("param_1 + 8", "+ 0x6c", "0x14"),
    0x005D131C: ("+ 0x3a", "+ 0x16", "FUN_00524cd6"),
    0x005D1348: ("param_1 + 0x41", "FUN_005244ee", "uVar2 = 2"),
    0x005D139E: ("FUN_005d131c(param_1,1)", "FUN_005d1348"),
    0x005D13C4: ("+ 0x38", "FUN_00524cd6", "psVar2[1] + -1"),
    0x005D142E: ("param_1 + 0x40", "FUN_005d13c4", "FUN_005d139e"),
    0x005D1512: ("param_1 + 0x13", "DAT_005d2138", "param_1[0x12]"),
    0x005D15B0: ("+ 0x3a", "+ 0x16", "FUN_00524cd6"),
    0x005D15DC: ("param_2 >> 10", "param_3 >> 10", "uVar3 = 2"),
    0x005D161A: ("FUN_005d15b0(param_1,1)", "FUN_005d15dc"),
    0x005D1640: ("+ 0x38", "FUN_00524cd6", "psVar2[1] + -1"),
    0x005D16A2: ("param_1 + 0x40", "FUN_005d1640", "FUN_005d161a"),
    0x005D176A: ("FUN_0043c0e4(param_1,0x3c,0)", "param_2 + 0xc", "param_2 + 0x10"),
}

GAPS = (
    (0x005D0570, 0x005D0574, "psconv/psobjs alignment", "1caf3298af304d0615bf5510daf4aca8cd3a86555222573eda9a243941a3451a"),
    (0x005D06C6, 0x005D071C, "ps_table_release boundary", "1c313c5f64b0c3d93d49a51144d145fe5904c29ecc82fff8e018997cf27b287e"),
    (0x005D121A, 0x005D128C, "parser scalar wrappers/init/done", "b643efd0daf72769213cd886d079a3197ebb8255818e42f098bec8b8f70a43a5"),
    (0x005D1460, 0x005D1512, "t1_builder_close_contour boundary", "1e3182f4427012fc1f130eafa10b56243f7f97b186c78ff3181138dd96d86bf0"),
    (0x005D159A, 0x005D15B0, "cff_builder_done boundary", "6e420cf515015c04dc7033829a09259f6b644576c1097f70e8a6ebaf15ace90e"),
    (0x005D16D0, 0x005D176A, "cff_builder_close_contour boundary", "17108b9188d0b6a5074714a05490e513004e72b41d96e79c8bbeff46b0457e42"),
    (0x005D1848, 0x005D185E, "ps_builder_done boundary", "5b77674d10f36c86519e78014b0880ca72141b341090a688cc0c5f25417441f7"),
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_prior():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch10_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_none_batch10_dependency", path)
    if spec is None or spec.loader is None:
        raise AuditError("could not load prior analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_audit() -> dict[str, Any]:
    prior_module = load_prior()
    prior = prior_module.run_audit()
    batch9 = prior_module.load_prior()
    batch8 = batch9.load_prior()
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
    log = hop2.authenticate(batch1.LOG).decode()

    sources: dict[str, str] = {}
    for module, pin in SOURCE_PINS.items():
        data = (PSAUX / module).read_bytes()
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
        (int(start, 16), int(end, 16), int(size), module, function)
        for start, end, size, module, function in ROW_RE.findall(candidate)
    ]
    if len(parsed) != 40 or tuple((row[3], row[4]) for row in parsed) != EXPECTED:
        raise AuditError("source identity/order drift")
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
    psaux_single = (PSAUX / "psaux.c").read_text()
    if psaux_single.find('#include "psconv.c"') > psaux_single.find('#include "psobjs.c"'):
        raise AuditError("psaux module order drift")

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
    if (len(exact), total) != (40, 5_516):
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
    if (external_functions, external_bytes) != (14, 796):
        raise AuditError("residual accounting drift")

    gaps = []
    for start, end, name, pin in GAPS:
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != end - start or sha256(body) != pin:
            raise AuditError(f"0x{start:08x}: uncatalogued cluster drift")
        gaps.append({
            "start": start, "end_exclusive": end, "bytes": end - start,
            "sha256": pin, "source_order_candidate": name,
            "disposition": "typed_external_not_in_none_census", "claimed_exact": False,
        })

    return {
        "status": "candidate-qualified-none-batch11",
        "read_only": True,
        "hardware_operations": False,
        "none_group": {
            "functions": 198, "bytes": 33_644,
            "upstream_freetype_source": {"functions": 184, "bytes": 32_848},
            "batch11_source_recovered": {"functions": 40, "bytes": 5_516},
            "typed_external": {"functions": external_functions, "bytes": external_bytes},
            "records": records,
        },
        "unsupported_remainder": {
            "before": prior["unsupported_remainder"]["after"],
            "source_recovered": {"functions": 40, "bytes": 5_516},
            "after": {"functions": external_functions, "bytes": external_bytes},
        },
        "uncatalogued_clusters": {
            "clusters": len(gaps), "bytes": sum(item["bytes"] for item in gaps), "records": gaps,
        },
        "source_pins": {
            module: {"path": str((PSAUX / module).relative_to(ROOT)), "bytes": pin[0], "sha256": pin[1]}
            for module, pin in SOURCE_PINS.items()
        },
        "adapter": {
            "license": "Apache-2.0", "production_routed": False,
            "upstream_implementation_license_retained": True,
            "source": str(CANDIDATE.relative_to(ROOT)), "header": str(HEADER.relative_to(ROOT)),
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
