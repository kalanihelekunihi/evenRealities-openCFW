#!/usr/bin/env python3
"""Qualify the SFNT object/name/WOFF tranche from the Apollo 0x5D none group."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];CANDIDATE=ROOT/"research/candidates/cordio_ll_sea_none_batch7/runtime_cordio_ll_sea_none_batch7_candidate.c";HEADER=CANDIDATE.with_suffix(".h");SOURCE=ROOT/"third_party/freetype/src/sfnt/sfobjs.c";SOURCE_PIN=(58_595,"87999f1d3183a70e406e28d93f6b77e9a158f0e635cb3fb725af0655b7e6c402");LOAD_BASE=0x00437FE0
ROW_RE=re.compile(r'\{(0x[0-9A-F]+)u,(0x[0-9A-F]+)u,(\d+)u,"([^"]+)","([^"]+)",FT_LICENSE\}');EXPECTED=("tt_name_ascii_from_utf16","tt_name_ascii_from_other","tt_face_get_name","sfnt_find_encoding","woff_open_font","sfnt_open_font","sfnt_init_face")
TOKENS={0x5DAB8E:("param_1 + 8) >> 1","CONCAT11(*puVar4,puVar4[1])","uVar2 = 0x3f"),0x5DABEE:("param_1 + 8","pbVar5 = pbVar5 + 1","bVar2 = 0x3f"),0x5DAC40:("param_1 + 0x164","puVar3 = puVar3 + 10","puVar3[2] & 0x3ff","FUN_0052919c","*param_3 = uVar2"),0x5DADF8:("DAT_005db934 + 0x21","piVar1[1] == -1","piVar1 = piVar1 + 3"),0x5DAE90:("local_48 * 0x14 + 0x2c","local_48 * 0x10 + 0xc","FUN_00567c4c","FUN_005bf004","0xfffffbff"),0x5DB3EC:("param_2 + 0x84","iVar2 == 0x10000","iVar2 == 0x20000","FUN_005dae90","param_2 + 0x90"),0x5DB578:("PTR_s_postscript_cmaps","PTR_s_multi_masters","PTR_s_metrics_variations","FUN_005db3ec","uVar3 == 0x14","uVar2 < 0x3fff")}
GAPS=((0x005DAE28,0x005DAE90,"sfnt_stream_close + compare_offsets","d37f822bbfb284437585f2a097938ae5b7436f0321b685c3ecd067c8e5785485"),(0x005DB92A,0x005DC266,"sfnt_load_face + sfnt_done_face region","46d764004deea33830749a2be63e6cfb2256bdd47706b64f85008fffae86ca3c"))
class AuditError(RuntimeError):pass
def sha256(d:bytes)->str:return hashlib.sha256(d).hexdigest()
def load_prior():
 p=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch6_candidate.py";s=importlib.util.spec_from_file_location("open_cfw_none_batch6_dependency",p)
 if s is None or s.loader is None:raise AuditError("could not load prior analyzer")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run_audit()->dict[str,Any]:
 pm=load_prior();prior=pm.run_audit();batch5=pm.load_prior();batch4=batch5.load_prior();batch3=batch4.load_prior();batch2=batch3.load_prior();batch1=batch2.load_prior();hop4=batch1.load_prior();anchor=hop4.load_prior();hop2=anchor.load_hop2_analyzer();image=hop2.authenticate(hop4.IMAGE);log=batch3.pinned(batch3.LOG31).decode()
 data=SOURCE.read_bytes()
 if (len(data),sha256(data))!=SOURCE_PIN:raise AuditError("sfobjs source drift")
 source=data.decode();text=CANDIDATE.read_text();header=HEADER.read_text()
 if (text+header).count("SPDX-License-Identifier: Apache-2.0")!=2 or "no upstream implementation copied" not in text:raise AuditError("adapter license/boundary drift")
 parsed=[(int(a,16),int(e,16),int(n),m,f) for a,e,n,m,f in ROW_RE.findall(text)]
 if len(parsed)!=7 or tuple(x[4] for x in parsed)!=EXPECTED or any(x[3]!="sfobjs.c" for x in parsed):raise AuditError("source identity/order drift")
 positions=[]
 for function in EXPECTED:
  match=re.search(rf"(?m)^  {re.escape(function)}\s*\(",source)
  if match is None:raise AuditError(f"sfobjs.c:{function}: definition missing")
  positions.append(match.start())
 if positions!=sorted(positions) or "FreeType project" not in source or "LICENSE.TXT" not in source:raise AuditError("upstream order/terms drift")
 if not (source.find("sfnt_stream_close")<source.find("compare_offsets")<source.find("woff_open_font") and source.find("sfnt_init_face")<source.find("sfnt_load_face")<source.find("sfnt_done_face")):raise AuditError("omitted source boundary drift")
 old=prior["none_group"]["records"];exact={};total=0
 for start,end,size,module,function in parsed:
  row=old.get(f"0x{start:08X}")
  if row is None or row["disposition"]!="typed_external" or row["end_exclusive"]!=end or row["bytes"]!=size:raise AuditError(f"0x{start:08x}: residual drift")
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if len(body)!=size:raise AuditError("image body missing")
  total+=size;exact[start]={"end_exclusive":end,"bytes":size,"sha256":sha256(body),"disposition":"upstream_freetype_source","upstream_module":module,"upstream_function":function,"upstream_license":"FreeType Project License; retained file-specific notices and grants"}
 if (len(exact),total)!=(7,3_334):raise AuditError("batch accounting drift")
 for address,tokens in TOKENS.items():
  begin=log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}");end=log.find("OPENCFW_FUNCTION_END",begin);body=log[begin:end]
  if begin<0 or any(t not in body for t in tokens):raise AuditError(f"0x{address:08x}: semantic signature drift")
 records={};ef=eb=0
 for key,row in old.items():
  address=int(key,16);records[key]=exact.get(address,row)
  if records[key]["disposition"]=="typed_external":ef+=1;eb+=records[key]["bytes"]
 if (ef,eb)!=(99,17_070):raise AuditError("residual accounting drift")
 gaps=[]
 for start,end,name,pin in GAPS:
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if sha256(body)!=pin:raise AuditError("uncatalogued cluster drift")
  gaps.append({"start":start,"end_exclusive":end,"bytes":end-start,"sha256":pin,"source_order_candidate":f"sfobjs.c:{name}","disposition":"typed_external_not_in_none_census","claimed_exact":False})
 return {"status":"candidate-qualified-none-batch7","read_only":True,"hardware_operations":False,"none_group":{"functions":198,"bytes":33_644,"upstream_freetype_source":{"functions":99,"bytes":16_574},"batch7_source_recovered":{"functions":7,"bytes":3_334},"typed_external":{"functions":ef,"bytes":eb},"records":records},"unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],"source_recovered":{"functions":7,"bytes":3_334},"after":{"functions":ef,"bytes":eb}},"uncatalogued_clusters":{"clusters":2,"bytes":sum(x["bytes"] for x in gaps),"records":gaps},"source_pin":{"path":str(SOURCE.relative_to(ROOT)),"bytes":SOURCE_PIN[0],"sha256":SOURCE_PIN[1]},"adapter":{"license":"Apache-2.0","production_routed":False,"upstream_implementation_license_retained":True,"source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--pretty",action="store_true");a=p.parse_args();print(json.dumps(run_audit(),indent=2 if a.pretty else None,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
