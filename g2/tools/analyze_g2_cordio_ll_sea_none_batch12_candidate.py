#!/usr/bin/env python3
"""Close the final 14 bodies in the Apollo 0x5D none census."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_none_batch12/runtime_cordio_ll_sea_none_batch12_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
LOAD_BASE = 0x00437FE0
SOURCES = {
    "t1cmap.c": ROOT / "third_party/freetype/src/psaux/t1cmap.c",
    "psft.c": ROOT / "third_party/freetype/src/psaux/psft.c",
    "ttbdf.c": ROOT / "third_party/freetype/src/sfnt/ttbdf.c",
}
SOURCE_PINS = {
    "t1cmap.c": (11_693, "3543b52fe9bb45fd73d8cd5d4e7a9f60c0a71e08ce7f18602d32f314c4bf2d23"),
    "psft.c": (26_591, "20c152003634042eee20ffa17ab4a1280743bd6f9117725aee5534662a1a9e3f"),
    "ttbdf.c": (7_083, "ea44af46d27e96590681f72273273da12e146968d9c61711ca8fa73c6c99ed23"),
}
VENDOR_MANIFEST = REPO / "third-party/fetched/manifest.json"
VENDOR_MANIFEST_PIN = (26_671, "3881eb71e5092daad261908bcffc59dbb111eac5ce27162cfd2ea0e54e3e9bb5")

ROW_RE = re.compile(
    r'\{\s*(0x[0-9A-F]+)u,\s*(0x[0-9A-F]+)u,\s*(\d+)u,\s*'
    r'"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*(FT_LICENSE|RTT_LICENSE)\s*\}'
)
EXPECTED = (
    ("FreeType", "t1cmap.c", "t1_cmap_std_init", "FT_LICENSE"),
    ("FreeType", "t1cmap.c", "t1_cmap_std_char_index", "FT_LICENSE"),
    ("FreeType", "t1cmap.c", "t1_cmap_std_char_next", "FT_LICENSE"),
    ("FreeType", "t1cmap.c", "t1_cmap_unicode_char_index", "FT_LICENSE"),
    ("FreeType", "t1cmap.c", "t1_cmap_unicode_char_next", "FT_LICENSE"),
    ("FreeType/Adobe", "psft.c", "cf2_free_instance", "FT_LICENSE"),
    ("FreeType/Adobe", "psft.c", "cf2_builder_moveTo", "FT_LICENSE"),
    ("SEGGER", "SEGGER_RTT.c", "SEGGER_RTT_Init", "RTT_LICENSE"),
    ("SEGGER", "SEGGER_RTT.c", "_WriteBlocking", "RTT_LICENSE"),
    ("SEGGER", "SEGGER_RTT.c", "_WriteNoCheck", "RTT_LICENSE"),
    ("SEGGER", "SEGGER_RTT.c", "_GetAvailWriteSpace", "RTT_LICENSE"),
    ("SEGGER", "SEGGER_RTT.c", "SEGGER_RTT_WriteNoLock", "RTT_LICENSE"),
    ("SEGGER", "SEGGER_RTT.c", "SEGGER_RTT_Write", "RTT_LICENSE"),
    ("FreeType", "ttbdf.c", "tt_face_free_bdf_props", "FT_LICENSE"),
)

TOKENS = {
    0x005D1D2A: ("iVar2 + 0x1e8", "iVar2 + 0x1a4", "iVar1 + 0x18", "iVar1 + 0x1c"),
    0x005D1D64: ("param_2 < 0x100", "param_1 + 0x14", "param_1 + 0x18", "FUN_0046cacc"),
    0x005D1DAA: ("uVar2 = uVar2 + 1", "0xff < uVar2", "FUN_005d1d64"),
    0x005D1EB4: ("*(int *)(*param_1 + 0x1e8) + 8",),
    0x005D1EC2: ("*(int *)(*param_1 + 0x1e8) + 0xc",),
    0x005D2EFE: ("param_1[0x1b]", "param_1[0x1d]", "FUN_00529256"),
    0x005D2F22: ("FUN_005d1986", "iVar1 + 0x2c", "= 0"),
    0x005D9950: ("FUN_0043c0e4(DAT_005d9b58,0xa8,0)", "iVar1 + 0x20", "iVar1 + 0x68", "DataMemoryBarrier"),
    0x005D99C0: ("FUN_00439be4", "param_3 = param_3 - uVar4", "uVar3 == *(uint *)(param_1 + 8)", "DataMemoryBarrier"),
    0x005D9A44: ("param_3 < uVar1", "param_2 + uVar1", "param_3 - uVar1", "DataMemoryBarrier"),
    0x005D9AA2: ("param_1 + 0x10", "param_1 + 0xc", "param_1 + 8"),
    0x005D9ABC: ("param_1 * 0x18", "FUN_005d9aa2", "FUN_005d9a44", "FUN_005d99c0"),
    0x005D9B28: ("*DAT_005d9b58 != 'S'", "getBasePriority", "setBasePriority(0x20)", "FUN_005d9abc"),
    0x005DC266: ("param_1 + 0x32c", "param_1 + 0x318", "FUN_005289b0", "param_1 + 0x324"),
}

GAPS = (
    (0x005D1D52, 0x005D1D64, "t1_cmap_std_done", "6dc164b98bb8f7976a6d05951db3ef9a5a83912a42d3e42b046d53ee18f82ca5"),
    (0x005D1DD4, 0x005D1EB4, "remaining Type 1 cmap callbacks/classes", "6a5aa8e302a57b93efe5c15f47272f96af66c2ab2eef706b5482d832ae0b0e69"),
    (0x005D2F34, 0x005D2FEE, "CF2 line/cubic builder callbacks", "3112324a4e667639670e7863eef670f8a83f5ee1b4cba9a2628a80f805388cdb"),
    (0x005DC290, 0x005DC542, "remaining ttbdf load/find boundary", "2b6fed6648abf73406925f2818b9eb59043083e0a5cee0fcd1ecdd8e1b44d5a0"),
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_prior():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch11_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_none_batch11_dependency", path)
    if spec is None or spec.loader is None:
        raise AuditError("could not load prior analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_audit() -> dict[str, Any]:
    prior_module = load_prior()
    prior = prior_module.run_audit()
    batch10 = prior_module.load_prior()
    batch9 = batch10.load_prior()
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
    log30 = hop2.authenticate(batch1.LOG).decode()
    log31 = batch3.pinned(batch3.LOG31).decode()
    logs = log30 + "\n" + log31

    source_text: dict[str, str] = {}
    for module, path in SOURCES.items():
        data = path.read_bytes()
        if (len(data), sha256(data)) != SOURCE_PINS[module]:
            raise AuditError(f"{module}: source drift")
        source_text[module] = data.decode()
    vendor_data = VENDOR_MANIFEST.read_bytes()
    if (len(vendor_data), sha256(vendor_data)) != VENDOR_MANIFEST_PIN:
        raise AuditError("vendor manifest drift")
    vendor_manifest = json.loads(vendor_data)
    segger = next((row for row in vendor_manifest["components"] if row.get("id") == "segger-rtt"), None)
    if segger is None or segger.get("version") != "6.18a":
        raise AuditError("SEGGER provider/version drift")
    if segger.get("license") != "SEGGER RTT redistributable source license":
        raise AuditError("SEGGER license drift")
    if segger.get("source_sha256") != "52f9a10baa6cea801134e7eb87848631fd03232540366c407c2a9183641c9088":
        raise AuditError("SEGGER source pin drift")

    candidate = CANDIDATE.read_text()
    header = HEADER.read_text()
    if (candidate + header).count("SPDX-License-Identifier: Apache-2.0") != 2:
        raise AuditError("adapter license drift")
    if "no upstream implementation copied" not in candidate:
        raise AuditError("adapter boundary drift")
    if "SEGGER RTT redistributable source license" not in candidate:
        raise AuditError("vendor terms missing from adapter")
    parsed = [
        (int(start, 16), int(end, 16), int(size), provider, module, function, license_macro)
        for start, end, size, provider, module, function, license_macro in ROW_RE.findall(candidate)
    ]
    if len(parsed) != 14 or tuple((row[3], row[4], row[5], row[6]) for row in parsed) != EXPECTED:
        raise AuditError("source/provider identity order drift")
    for module in SOURCES:
        functions = [row[5] for row in parsed if row[4] == module]
        positions = []
        for function in functions:
            match = re.search(rf"(?m)^  {re.escape(function)}\s*\(", source_text[module])
            if match is None:
                raise AuditError(f"{module}:{function}: definition missing")
            positions.append(match.start())
        if positions != sorted(positions):
            raise AuditError(f"{module}: source order drift")
        lowered = source_text[module].lower()
        if "freetype project" not in lowered or "license" not in lowered:
            raise AuditError(f"{module}: upstream terms drift")

    old = prior["none_group"]["records"]
    exact: dict[int, dict[str, Any]] = {}
    freetype_functions = freetype_bytes = segger_functions = segger_bytes = 0
    for start, end, size, provider, module, function, license_macro in parsed:
        row = old.get(f"0x{start:08X}")
        if row is None or row["disposition"] != "typed_external":
            raise AuditError(f"0x{start:08x}: residual disposition drift")
        if row["end_exclusive"] != end or row["bytes"] != size or end - start != size:
            raise AuditError(f"0x{start:08x}: residual boundary drift")
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != size:
            raise AuditError(f"0x{start:08x}: image body missing")
        if license_macro == "FT_LICENSE":
            disposition = "upstream_freetype_source"
            license_name = "FreeType Project License; retained file-specific notices and grants"
            freetype_functions += 1
            freetype_bytes += size
        else:
            disposition = "upstream_segger_rtt_provider"
            license_name = "SEGGER RTT redistributable source license; upstream terms retained"
            segger_functions += 1
            segger_bytes += size
        exact[start] = {
            "end_exclusive": end, "bytes": size, "sha256": sha256(body),
            "disposition": disposition, "upstream_provider": provider,
            "upstream_module": module, "upstream_function": function,
            "upstream_license": license_name,
        }
    if (freetype_functions, freetype_bytes, segger_functions, segger_bytes) != (8, 276, 6, 520):
        raise AuditError("provider accounting drift")
    for address, tokens in TOKENS.items():
        begin = logs.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}")
        end = logs.find("OPENCFW_FUNCTION_END", begin)
        body = logs[begin:end]
        if begin < 0 or end < 0 or any(token not in body for token in tokens):
            raise AuditError(f"0x{address:08x}: semantic signature drift")

    records = {key: exact.get(int(key, 16), row) for key, row in old.items()}
    unclassified = [key for key, row in records.items() if row["disposition"] == "typed_external"]
    if unclassified or len(records) != 198 or sum(row["bytes"] for row in records.values()) != 33_644:
        raise AuditError("final census closure drift")
    freetype_total = [row for row in records.values() if row["disposition"] == "upstream_freetype_source"]
    segger_total = [row for row in records.values() if row["disposition"] == "upstream_segger_rtt_provider"]
    if (len(freetype_total), sum(row["bytes"] for row in freetype_total)) != (192, 33_124):
        raise AuditError("final FreeType accounting drift")
    if (len(segger_total), sum(row["bytes"] for row in segger_total)) != (6, 520):
        raise AuditError("final SEGGER accounting drift")

    gaps = []
    for start, end, name, pin in GAPS:
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != end - start or sha256(body) != pin:
            raise AuditError(f"0x{start:08x}: typed boundary drift")
        gaps.append({
            "start": start, "end_exclusive": end, "bytes": end - start,
            "sha256": pin, "source_order_candidate": name,
            "disposition": "typed_external_not_in_none_census",
            "reason": "complete callable record unavailable in authenticated decompiler corpus",
            "claimed_exact": False, "unclassified": False,
        })

    return {
        "status": "candidate-qualified-none-batch12-closed",
        "read_only": True, "hardware_operations": False,
        "none_group": {
            "functions": 198, "bytes": 33_644,
            "upstream_freetype_source": {"functions": 192, "bytes": 33_124},
            "upstream_segger_rtt_provider": {"functions": 6, "bytes": 520},
            "batch12_source_recovered": {"functions": 14, "bytes": 796},
            "classified": {"functions": 198, "bytes": 33_644},
            "unclassified": {"functions": 0, "bytes": 0},
            "records": records,
        },
        "unsupported_remainder": {
            "before": prior["unsupported_remainder"]["after"],
            "source_recovered": {"functions": 14, "bytes": 796},
            "after": {"functions": 0, "bytes": 0},
        },
        "typed_non_census_boundaries": {
            "clusters": len(gaps), "bytes": sum(row["bytes"] for row in gaps), "records": gaps,
            "unclassified": {"clusters": 0, "bytes": 0},
        },
        "source_pins": {
            module: {"path": str(path.relative_to(ROOT)), "bytes": SOURCE_PINS[module][0], "sha256": SOURCE_PINS[module][1]}
            for module, path in SOURCES.items()
        },
        "segger_provider_pin": {
            "manifest": str(VENDOR_MANIFEST.relative_to(REPO)),
            "manifest_sha256": VENDOR_MANIFEST_PIN[1], "version": segger["version"],
            "source_sha256": segger["source_sha256"], "license": segger["license"],
            "license_path": segger["license_path"], "production_routed": False,
        },
        "adapter": {
            "license": "Apache-2.0", "production_routed": False,
            "upstream_terms_retained": ["FreeType Project License", "SEGGER RTT redistributable source license"],
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
