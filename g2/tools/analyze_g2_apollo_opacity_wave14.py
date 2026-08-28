#!/usr/bin/env python3
"""Audit Apollo opacity wave 14's FreeType CFF glyph-load closure.

SPDX-License-Identifier: MIT
"""
from __future__ import annotations

import argparse, csv, hashlib, importlib.util, json, re, struct
from collections import Counter, deque
from pathlib import Path
from typing import Any

G2 = Path(__file__).resolve().parents[1]
DECOMP = G2 / "research/corpus/apollo-main/ghidra/decomp"
FUNCTIONS = DECOMP / "functions.jsonl"
CORPORA = (DECOMP / "bundles/apollo-decomp-08.c", DECOMP / "bundles/apollo-decomp-13.c")
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCES = (G2 / "third_party/freetype/src/cff/cffgload.c", G2 / "third_party/freetype/src/cff/cffload.c", G2 / "third_party/freetype/src/base/ftobjs.c")
LICENSE = G2 / "third_party/freetype/LICENSE"
ADMISSION = G2 / "research/admission/apollo_opacity_wave14"
BOUNDARY, FRONTIER, SHARED, INDIRECT = (ADMISSION / name for name in ("source_boundaries.tsv","reconciled_frontier.tsv","shared_data.tsv","typed_indirect_interfaces.tsv"))
ROOT, LOAD_ADDRESS, OTA_HEADER_BYTES = 0x005AC66E, 0x00438000, 32
PINS = {
    FUNCTIONS:(3_270_703,"9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    CORPORA[0]:(981_479,"2873aee30b06913cf8425d3e990eca6411f245de9b1fb7bed0a5e46fcfce36a7"), CORPORA[1]:(731_098,"2acd0f0f7b1c9f736f6df76ac0800a76c1ad4da71298322ebe4b63b035dcf703"),
    IMAGE:(3_523_396,"36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"),
    SOURCES[0]:(24_674,"f3ede2b81f654f0c95dc5cf67e8f6962ceb68aa4e6c096c4ab1b81b57c29cd8f"), SOURCES[1]:(75_622,"f8ec69b219bfd0ced42da86e57448482d363d533934325fdeb287362f769b232"), SOURCES[2]:(150_798,"9f5533b64c0e1926346bbabb1107a319801ca677b19b6f236ffd379456a6e24e"),
    LICENSE:(6_743,"08c135755dd589039470f1fdbb400daaabaaa50d0b366d19cebff4d22986baa1"),
}
EXPECTED_SELECTED = {ROOT,0x00526A02,0x005AC5F0,0x005AC634,0x005ADDB8}

class WaveError(RuntimeError): pass
def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def pinned(path:Path)->bytes:
    data=path.read_bytes()
    if (len(data),sha256(data)) != PINS[path]: raise WaveError(f"pin drift: {path}")
    return data
def tsv_rows(path:Path)->list[dict[str,str]]:
    lines=[line for line in path.read_text().splitlines() if not line.startswith("#")]
    if not lines: raise WaveError(f"empty TSV: {path}")
    return list(csv.DictReader(lines,delimiter="\t"))
def load_module(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise WaveError(f"cannot load {path}")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def corpus_function(corpus:str,entry:int)->str:
    match=re.search(rf"/\* FUN 0x{entry:08x} .*?(?=/\* FUN 0x|\Z)",corpus,re.S)
    if match is None: raise WaveError(f"0x{entry:08X}: corpus body missing")
    return match.group(0)
def residual_before()->tuple[dict[int,dict[str,str]],set[int],dict[str,Any]]:
    w13=load_module(G2/"tools/analyze_g2_apollo_opacity_wave13.py","opacity_wave14_wave13"); report=w13.run_audit()
    if report["after"]!={"functions":1297,"bytes":136482} or report["largest_remaining"]!={"entry":"0x005AC66E","envelope_bytes":1684}: raise WaveError("wave-13 residual drift")
    parent,residual,_=w13.residual_before(); residual-=w13.EXPECTED_SELECTED
    return parent,residual,report

def run_audit()->dict[str,Any]:
    parent,residual,report13=residual_before(); before={"functions":len(residual),"bytes":sum(int(parent[e]["official_opaque_bytes"]) for e in residual)}
    if before!=report13["after"] or max((int(parent[e]["official_opaque_bytes"]),e) for e in residual)!=(1684,ROOT): raise WaveError("authoritative residual/root drift")
    local={path:pinned(path) for path in PINS}; payload=local[IMAGE][OTA_HEADER_BYTES:]
    functions={int(row["entry"],16):row for row in (json.loads(line) for line in local[FUNCTIONS].decode().splitlines())}; corpus="\n".join(local[p].decode(errors="ignore") for p in CORPORA)
    rows=tsv_rows(BOUNDARY); selected={int(row["entry"],16) for row in rows}
    derived={ROOT}; depth={ROOT:0}; queue=deque([ROOT])
    while queue:
        owner=queue.popleft()
        for text in functions[owner]["callees"]:
            target=int(text,16)
            if target in residual and target not in derived: derived.add(target); depth[target]=depth[owner]+1; queue.append(target)
    if derived!=EXPECTED_SELECTED or selected!=derived: raise WaveError(f"residual static closure drift: {derived ^ EXPECTED_SELECTED}")
    sources={str(path.relative_to(G2)):local[path].decode(errors="ignore") for path in SOURCES}
    records=[]
    for row in rows:
        entry=int(row["entry"],16); fn=functions[entry]; p=parent[entry]
        observed=(int(row["end_exclusive"],16),int(row["envelope_bytes"]),int(row["corpus_body_bytes"]),row["body_sha256"],int(row["closure_depth"]))
        expected=(int(p["body_end_exclusive"],16),int(p["official_opaque_bytes"]),int(fn["body_bytes"]),fn["body_sha256"],depth[entry])
        if observed!=expected or len(fn["ranges"])!=1: raise WaveError(f"0x{entry:08X}: body/range/depth drift")
        path=row["source_path"].removeprefix("g2/")
        if row["symbol"] not in sources[path] or row["provider_identity"]!="FreeType-2.9.1-VER-2-9-1" or row["license_status"]!="FTL" or row["disposition"]!="source-attributed-research-only": raise WaveError(f"0x{entry:08X}: source/license drift")
        if fn["body_sha256"] not in corpus_function(corpus,entry).splitlines()[0]: raise WaveError("corpus marker drift")
        records.append(dict(row,source_identity_authenticated=True))
    for token in ("0xffff","0x10000","0xbec","0xa4","0x100"):
        if token not in corpus_function(corpus,ROOT).lower(): raise WaveError(f"root anchor missing: {token}")
    if "FreeType Project LICENSE" not in local[LICENSE].decode(errors="ignore"): raise WaveError("FTL text drift")

    outbound=Counter()
    for entry in selected:
        for text in functions[entry]["callees"]:
            target=int(text,16)
            if target not in selected: outbound[target]+=1
    frontier=tsv_rows(FRONTIER)
    if {int(row["entry"],16):int(row["call_relations"]) for row in frontier} != dict(outbound) or any(int(row["wave14_additional_function_bytes"]) for row in frontier): raise WaveError("static frontier drift")
    interfaces=tsv_rows(INDIRECT)
    if len(interfaces)!=6 or {row["disposition"] for row in interfaces}!={"typed-source-provider-interface","typed-optional-external-interface"} or any(int(row["wave14_additional_function_bytes"]) for row in interfaces): raise WaveError("dynamic interface closure drift")
    body=corpus_function(corpus,ROOT); labels={int(value,16) for value in re.findall(r"\bDAT_([0-9a-f]{8})",body)}; shared=tsv_rows(SHARED)
    if labels!={int(row["address"],16) for row in shared}: raise WaveError("data graph membership drift")
    expected_values={0x005AD344:0x62697473,0x005AD348:0x6F75746C,0x005AD34C:0x005AC635,0x005AD350:0x005AC5F1}
    for row in shared:
        address=int(row["address"],16); physical=payload[address-LOAD_ADDRESS:address-LOAD_ADDRESS+4]; value=struct.unpack("<I",physical)[0]
        if (row["bytes_hex"],row["sha256"],row["value_or_target"],int(row["wave14_additional_function_bytes"]))!=(physical.hex(),sha256(physical),f"0x{value:08X}",0) or value!=expected_values[address]: raise WaveError("shared data drift")
    selected_bytes=sum(int(parent[e]["official_opaque_bytes"]) for e in selected)
    if selected_bytes!=2006: raise WaveError("selected byte delta drift")
    remaining=residual-selected; after={"functions":len(remaining),"bytes":sum(int(parent[e]["official_opaque_bytes"]) for e in remaining)}; largest_bytes,largest_entry=max((int(parent[e]["official_opaque_bytes"]),e) for e in remaining)
    if after!={"functions":1292,"bytes":134476}: raise WaveError(f"after residual drift: {after}")
    canonical=[{k:row[k] for k in ("entry","symbol","source_path","provider_identity","license_status","disposition","body_sha256")} for row in sorted(rows,key=lambda x:int(x["entry"],16))]
    return {"status":"opacity-wave14-freetype-cff-glyph-load-source-closure","wave13_residual":report13["after"],"before":before,
        "selected_root_range":{"start":"0x005AC66E","end_exclusive":"0x005ACD02"},"actionable_graph":{"source_functions":5,"source_bytes":2006,"closure_depth_max":1,"static_terminal_functions":len(frontier),"dynamic_interfaces":len(interfaces)},
        "source_attributed":{"functions":5,"bytes":2006,"provider":"FreeType-2.9.1-VER-2-9-1","license":"FTL"},"range_partition":{"functions":5,"interior_islands":0,"interior_physical_bytes":0},
        "shared_data":{"direct_cells":4,"physical_bytes":16,"additional_function_bytes":0},"after":after,"largest_remaining":{"entry":f"0x{largest_entry:08X}","envelope_bytes":largest_bytes},
        "records":records,"mapping_sha256":sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()),"production_routed":False,
        "production_blocker":"missing exact feature macros/object ABI plus reviewed dual-profile Cortex-M55 codegen, relocation, link-order, and placement proof","read_only":True,"hardware_operations":False}

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--pretty",action="store_true");args=parser.parse_args();print(json.dumps(run_audit(),indent=2 if args.pretty else None,sort_keys=True));return 0
if __name__=="__main__": raise SystemExit(main())
