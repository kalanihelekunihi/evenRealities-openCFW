#!/usr/bin/env python3
"""Qualify the second positive-source batch from the Apollo 0x5D none group."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_none_batch2/runtime_cordio_ll_sea_none_batch2_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
PSHALGO = ROOT / "third_party/freetype/src/pshinter/pshalgo.c"
PSHALGO_PIN = (59_738, "cbede1f596434c2348711a1ed12c60448ed14759b52a48c31cf1898564d69842")
LOAD_BASE = 0x00437FE0
ROW_RE = re.compile(r'\{ (0x[0-9A-F]+)u, (0x[0-9A-F]+)u, (\d+)u, "([^"]+)", "([^"]+)", FT_LICENSE \}')
EXPECTED = (
    "psh_hint_overlap", "psh_hint_table_done", "psh_hint_table_deactivate",
    "psh_hint_table_record", "psh_hint_table_record_mask", "psh_hint_table_init",
    "psh_hint_table_activate_mask", "psh_dimension_quantize_len",
    "psh_hint_snap_stem_side_delta", "psh_hint_align",
    "psh_hint_table_align_hints", "psh_glyph_compute_inflections", "psh_glyph_done",
    "psh_compute_dir", "psh_glyph_load_points", "psh_glyph_save_points",
    "psh_glyph_init", "psh_glyph_compute_extrema",
)
SIGNATURES = {
    0x005D70A4: ("param_1[1] + *param_1", "param_2[1] + *param_2"),
    0x005D70C6: ("param_1[6] = 0", "param_1[3] = 0", "param_1[2] = 0"),
    0x005D7106: ("0xfffffffb", "0xffffffff", "iVar1 + 0x1c"),
    0x005D7124: ("param_2 * 0x1c", "FUN_005d70a4", "param_1[1] = uVar2 + 1"),
    0x005D718A: ("uVar1 = 0x80", "FUN_005d7124", "uVar1 >> 1"),
    0x005D71C4: ("0x1c", "uVar5 * 2 + 1", "FUN_005d718a", "FUN_005d7124"),
    0x005D72A8: ("FUN_005d7106", "param_1[1] = uVar9", "*piVar4 <= *piVar5"),
    0x005D7340: ("iVar2 < 0x28", "param_2 = 0x30", "uVar1 < 0x36", "0xffffffc0"),
    0x005D739C: ("param_1 + 0x20U", "param_2 + param_1 + 0x20U", "if (iVar2 < iVar3)"),
    0x005D73D0: ("param_3 * 0xcc", "FUN_005d8828", "FUN_005d7340", "FUN_005d739c"),
    0x005D75EE: ("FUN_005d73d0", "iVar2 + 0x1c"),
    0x005D761A: ("FUN_00524a30", "uVar6 ^ uVar2", "piVar9[3] | 4"),
    0x005D7742: ("param_1 + 0x11", "param_1 + 7", "param_1[4] = 0"),
    0x005D7782: ("iVar3 * 0xc < iVar2", "iVar2 * 0xc < iVar3", "0xfffffffe"),
    0x005D77CA: ("iVar3 + 0x1c", "iVar3 + 0x20", "puVar2 + 2"),
    0x005D7802: ("uVar1 + 0x24", "bVar5 = 0x20", "bVar5 = 0x40"),
    0x005D784A: ("FUN_0043c0e4(param_1,0x80,0)", "iVar5 * 0x28", "FUN_005d7782", "FUN_005d71c4"),
    0x005D7A6C: ("piVar4[4] | 0x40", "piVar4[4] | 0x80", "piVar4[4] | 0x100"),
}

class AuditError(RuntimeError): pass
def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def load_prior():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_none_batch1_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_none_batch1_dependency", path)
    if spec is None or spec.loader is None: raise AuditError("could not load prior analyzer")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def run_audit() -> dict[str, Any]:
    prior_module = load_prior(); prior = prior_module.run_audit()
    hop4 = prior_module.load_prior(); anchor = hop4.load_prior(); hop2 = anchor.load_hop2_analyzer()
    image = hop2.authenticate(hop4.IMAGE)
    log = hop2.authenticate(hop4.LOG).decode()
    source_data = PSHALGO.read_bytes()
    if (len(source_data), sha256(source_data)) != PSHALGO_PIN: raise AuditError("pshalgo source drift")
    source = source_data.decode(); candidate = CANDIDATE.read_text(); header = HEADER.read_text()
    if (candidate + header).count("SPDX-License-Identifier: Apache-2.0") != 2: raise AuditError("license declarations missing")
    if "no upstream implementation copied" not in candidate: raise AuditError("source boundary statement missing")
    if "FreeType project" not in source or "LICENSE.TXT" not in source: raise AuditError("upstream terms missing")

    parsed = [(int(a,16),int(e,16),int(s),m,f) for a,e,s,m,f in ROW_RE.findall(candidate)]
    if len(parsed) != 18 or len({x[0] for x in parsed}) != 18: raise AuditError("batch evidence drift")
    if tuple(x[4] for x in parsed) != EXPECTED or any(x[3] != "pshalgo.c" for x in parsed):
        raise AuditError("pshalgo source-order identity drift")
    positions = []
    for function in EXPECTED:
        match = re.search(rf"(?m)^  {re.escape(function)}\s*\(", source)
        if match is None: raise AuditError(f"pshalgo.c:{function}: definition missing")
        positions.append(match.start())
    if positions != sorted(positions) or len(set(positions)) != len(positions): raise AuditError("source ordering drift")
    if "#if 0  /* not used for now, experimental */" not in source or "#ifdef DEBUG_ZONES" not in source:
        raise AuditError("expected compiled-out source gaps missing")

    prior_records = prior["none_group"]["records"]
    exact = {}; exact_bytes = 0
    for start,end,size,module,function in parsed:
        old = prior_records.get(f"0x{start:08X}")
        if old is None or old["disposition"] != "typed_external" or old["end_exclusive"] != end or old["bytes"] != size:
            raise AuditError(f"0x{start:08x}: prior residual drift")
        body = image[start-LOAD_BASE:end-LOAD_BASE]
        if len(body) != size: raise AuditError(f"0x{start:08x}: body missing")
        exact_bytes += size
        exact[start] = {"end_exclusive":end,"bytes":size,"sha256":sha256(body),
                        "disposition":"upstream_freetype_source","upstream_module":module,
                        "upstream_function":function,
                        "upstream_license":"FreeType Project License; retained file-specific notices and grants"}
    if (len(exact), exact_bytes) != (18, 2_750): raise AuditError("exact batch accounting drift")
    for address,tokens in SIGNATURES.items():
        begin=log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}"); end=log.find("OPENCFW_FUNCTION_END",begin)
        body=log[begin:end]
        if begin < 0 or any(token not in body for token in tokens): raise AuditError(f"0x{address:08x}: semantic signature drift")

    records={}; external_functions=external_bytes=0
    for key,old in prior_records.items():
        address=int(key,16)
        if address in exact: records[key]=exact[address]
        else:
            records[key]=old
            if old["disposition"] == "typed_external": external_functions += 1; external_bytes += old["bytes"]
    if (external_functions,external_bytes)!=(170,29_530): raise AuditError("residual accounting drift")
    return {"status":"candidate-qualified-none-batch2","read_only":True,"hardware_operations":False,
            "none_group":{"functions":198,"bytes":33_644,
                          "upstream_freetype_source":{"functions":28,"bytes":4_114},
                          "batch2_source_recovered":{"functions":18,"bytes":2_750},
                          "typed_external":{"functions":external_functions,"bytes":external_bytes},"records":records},
            "unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],
                                     "source_recovered":{"functions":18,"bytes":2_750},
                                     "after":{"functions":external_functions,"bytes":external_bytes}},
            "source_pin":{"path":str(PSHALGO.relative_to(ROOT)),"bytes":PSHALGO_PIN[0],"sha256":PSHALGO_PIN[1]},
            "adapter":{"license":"Apache-2.0","production_routed":False,
                       "upstream_implementation_license_retained":True,
                       "source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--pretty",action="store_true"); args=parser.parse_args()
    print(json.dumps(run_audit(),indent=2 if args.pretty else None,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
