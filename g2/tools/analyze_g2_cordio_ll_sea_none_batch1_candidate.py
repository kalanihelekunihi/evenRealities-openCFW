#!/usr/bin/env python3
"""Qualify the first positive-source batch from the remaining 0x5D none group."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "research/candidates/cordio_ll_sea_none_batch1/runtime_cordio_ll_sea_none_batch1_candidate.c"
HEADER = CANDIDATE.with_suffix(".h")
CENSUS = ROOT / "tools/manifests/g2-cordio-ll-sea-census.tsv"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOG = ROOT / "research/corpus/apollo-main/ghidra/full64-j64-auth/logs/apollo-30.log"
LOAD_BASE = 0x00437FE0
ROW_RE = re.compile(r'\{ (0x[0-9A-F]+)u, (0x[0-9A-F]+)u, (\d+)u, "([^"]+)", "([^"]+)", FT_LICENSE \}')
SIGNATURES = {
    0x005D188A: ("param_2 >> 10", "param_3 >> 10", "uVar3 = 2", "uVar3 = 1"),
    0x005D18C8: ("FUN_005d185e(param_1,1)", "FUN_005d188a"),
    0x005D18EE: ("param_1 + 0x2d", "FUN_00524cd6", "*psVar2 + 1"),
    0x005D1958: ("param_1 + 0x2c", "FUN_005d18ee", "FUN_005d18c8"),
    0x005D1A38: ("0x28c", "param_1 + 0x214", "param_1 + 0x244"),
    0x005D1F26: ("param_1 + 0x46c", "0xa0", "0xa1", "uVar7 - 0x1e"),
    0x005D20BC: ("0x5e8", "FUN_00527406", "param_1 + 0x5c4"),
    0x005D2170: ("param_2 < 0x4d8", "param_2 < 0x846c", "0x8000"),
    0x005D21E4: ("0x308", "FUN_005d2170", "param_1 + 0x2ec"),
    0x005D2250: ("param_1 + 0x2d8", "param_1 + 0x2e8", "FUN_005d2170"),
}

class AuditError(RuntimeError): pass
def sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def load_prior():
    path = ROOT / "tools/analyze_g2_cordio_ll_sea_hop4_residue_candidate.py"
    spec = importlib.util.spec_from_file_location("open_cfw_hop4_dependency", path)
    if spec is None or spec.loader is None: raise AuditError("could not load prior analyzer")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def parse_census():
    lines = [line for line in CENSUS.read_text().splitlines() if line and not line.startswith("#")]
    return {int(row["entry"], 16): row for row in csv.DictReader(lines, delimiter="\t")}

def run_audit() -> dict[str, Any]:
    prior_module = load_prior(); prior = prior_module.run_audit()
    anchor = prior_module.load_prior(); hop2 = anchor.load_hop2_analyzer()
    image = hop2.authenticate(IMAGE); log = hop2.authenticate(LOG).decode()
    census = parse_census(); candidate = CANDIDATE.read_text(); header = HEADER.read_text()
    if (candidate + header).count("SPDX-License-Identifier: Apache-2.0") != 2: raise AuditError("license declarations missing")
    if "no upstream implementation copied" not in candidate: raise AuditError("source boundary statement missing")
    sources = {}
    for path in hop2.FILE_PINS:
        if path.parent == anchor.PSAUX: sources[path.name] = hop2.authenticate(path).decode()
    for path, pin in anchor.PINS.items(): sources[path.name] = anchor.read_pinned(path, pin).decode()
    t1 = anchor.PSAUX / "t1decode.c"; data = t1.read_bytes()
    if (len(data), sha256(data)) != prior_module.T1_PIN: raise AuditError("t1decode source drift")
    sources[t1.name] = data.decode()

    parsed = [(int(a,16),int(e,16),int(s),m,f) for a,e,s,m,f in ROW_RE.findall(candidate)]
    if len(parsed) != 10 or len({x[0] for x in parsed}) != 10: raise AuditError("batch evidence drift")
    none = {a:r for a,r in census.items() if r["evidence"] == "none"}
    if (len(none), sum(int(r["official_opaque_bytes"]) for r in none.values())) != (198, 33_644):
        raise AuditError("none-group baseline drift")
    exact = {}; exact_bytes = 0
    for start,end,size,module,function in parsed:
        row = none.get(start)
        if row is None or int(row["body_end_exclusive"],16)!=end or int(row["official_opaque_bytes"])!=size:
            raise AuditError(f"0x{start:08x}: none census drift")
        source = sources.get(module, "")
        if re.search(rf"(?m)^  {re.escape(function)}\s*\(", source) is None: raise AuditError(f"{module}:{function}: definition missing")
        if "freetype project" not in source.lower() or "license" not in source.lower(): raise AuditError(f"{module}: terms missing")
        body=image[start-LOAD_BASE:end-LOAD_BASE]
        if len(body)!=size: raise AuditError(f"0x{start:08x}: body missing")
        exact_bytes += size
        exact[start]={"end_exclusive":end,"bytes":size,"sha256":sha256(body),"disposition":"upstream_freetype_source","upstream_module":module,"upstream_function":function,"upstream_license":"FreeType Project License; retained file-specific notices and grants"}
    if (len(exact),exact_bytes)!=(10,1364): raise AuditError("exact batch accounting drift")
    for address,tokens in SIGNATURES.items():
        begin=log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}"); end=log.find("OPENCFW_FUNCTION_END",begin); body=log[begin:end]
        if begin<0 or any(t not in body for t in tokens): raise AuditError(f"0x{address:08x}: semantic signature drift")
    records={}
    for address,row in sorted(none.items()):
        if address in exact: records[f"0x{address:08X}"]=exact[address]
        else: records[f"0x{address:08X}"]={"end_exclusive":int(row["body_end_exclusive"],16),"bytes":int(row["official_opaque_bytes"]),"disposition":"typed_external","policy":"unsupported unless a later bounded batch supplies positive source evidence"}
    return {"status":"candidate-qualified-none-batch1","read_only":True,"hardware_operations":False,
            "none_group":{"functions":198,"bytes":33_644,"upstream_freetype_source":{"functions":10,"bytes":1_364},"typed_external":{"functions":188,"bytes":32_280},"records":records},
            "unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],"source_recovered":{"functions":10,"bytes":1_364},"after":{"functions":188,"bytes":32_280}},
            "adapter":{"license":"Apache-2.0","production_routed":False,"upstream_implementation_license_retained":True,"source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--pretty",action="store_true"); a=p.parse_args()
    print(json.dumps(run_audit(),indent=2 if a.pretty else None,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
