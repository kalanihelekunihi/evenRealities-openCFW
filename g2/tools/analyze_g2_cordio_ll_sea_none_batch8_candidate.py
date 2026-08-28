#!/usr/bin/env python3
"""Qualify the complete TrueType cmap-format-4 engine from the Apollo 0x5D none group."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];CANDIDATE=ROOT/"research/candidates/cordio_ll_sea_none_batch8/runtime_cordio_ll_sea_none_batch8_candidate.c";HEADER=CANDIDATE.with_suffix(".h");SOURCE=ROOT/"third_party/freetype/src/sfnt/ttcmap.c";SOURCE_PIN=(120_864,"e321c3d6cac43fa450698f5a98456fd8e84d7da0b37ea75531ad79c3cecfe5fb");LOAD_BASE=0x00437FE0
ROW_RE=re.compile(r'\{(0x[0-9A-F]+)u,(0x[0-9A-F]+)u,(\d+)u,"([^"]+)","([^"]+)",FT_LICENSE\}');EXPECTED=("tt_cmap4_set_range","tt_cmap4_next","tt_cmap4_validate","tt_cmap4_char_map_linear","tt_cmap4_char_map_binary","tt_cmap4_char_index")
TOKENS={0x5DC99C:("param_1[8]","param_1[0xb]","param_1[0xc]","uVar3 != 0xffff","param_1[0xd]"),0x5DCA46:("param_1[6] + 1","0x10000 - iVar5","FUN_005dc99c","param_1[6] = -1"),0x5DCB16:("uVar4 >> 1","uVar6 != 1 << sVar1","uVar14 == 0xffff","FUN_00524f84(param_2,0x10","uVar13 | 2"),0x5DCE22:("uVar1 & 0xfffffffe","uVar1 >> 1","uVar8 < 0x10000","uVar8 == 0xffff","*param_2 = uVar8"),0x5DCFF6:("uVar1 & 0xfffe","uVar1 >> 1","uVar20 = 0xffff","FUN_005dc99c","FUN_005dca46"),0x5DD39E:("param_2 < 0x10000","FUN_005dce22","FUN_005dcff6")}
GAPS=((0x005DC7E2,0x005DC99C,"format-2 tail/classes plus tt_cmap4_init boundary","57b1c31f740f1b6693cc595c84d9e29d0fd42d09ebac24824b2afd8936811694"),(0x005DD3C6,0x005DD584,"tt_cmap4_char_next/get_info/class boundary","dafa42d604451c611de7270afc471c62a7bf735293fce58b9e43d37485a588e4"))
class AuditError(RuntimeError):pass
def sha256(d:bytes)->str:return hashlib.sha256(d).hexdigest()
def load_prior():
 p=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch7_candidate.py";s=importlib.util.spec_from_file_location("open_cfw_none_batch7_dependency",p)
 if s is None or s.loader is None:raise AuditError("could not load prior analyzer")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run_audit()->dict[str,Any]:
 pm=load_prior();prior=pm.run_audit();batch6=pm.load_prior();batch5=batch6.load_prior();batch4=batch5.load_prior();batch3=batch4.load_prior();batch2=batch3.load_prior();batch1=batch2.load_prior();hop4=batch1.load_prior();anchor=hop4.load_prior();hop2=anchor.load_hop2_analyzer();image=hop2.authenticate(hop4.IMAGE);log=batch3.pinned(batch3.LOG31).decode()
 data=SOURCE.read_bytes()
 if (len(data),sha256(data))!=SOURCE_PIN:raise AuditError("ttcmap source drift")
 source=data.decode();text=CANDIDATE.read_text();header=HEADER.read_text()
 if (text+header).count("SPDX-License-Identifier: Apache-2.0")!=2 or "no upstream implementation copied" not in text:raise AuditError("adapter license/boundary drift")
 parsed=[(int(a,16),int(e,16),int(n),m,f) for a,e,n,m,f in ROW_RE.findall(text)]
 if len(parsed)!=6 or tuple(x[4] for x in parsed)!=EXPECTED or any(x[3]!="ttcmap.c" for x in parsed):raise AuditError("source identity/order drift")
 positions=[]
 for function in EXPECTED:
  match=re.search(rf"(?m)^  {re.escape(function)}\s*\(",source)
  if match is None:raise AuditError(f"ttcmap.c:{function}: definition missing")
  positions.append(match.start())
 if positions!=sorted(positions) or "FreeType project" not in source or "LICENSE.TXT" not in source:raise AuditError("upstream order/terms drift")
 if not (source.find("tt_cmap4_init")<positions[0] and positions[-1]<source.find("tt_cmap4_char_next")<source.find("tt_cmap4_get_info")<source.find("tt_cmap6_validate")):raise AuditError("format boundary drift")
 old=prior["none_group"]["records"];exact={};total=0
 for start,end,size,module,function in parsed:
  row=old.get(f"0x{start:08X}")
  if row is None or row["disposition"]!="typed_external" or row["end_exclusive"]!=end or row["bytes"]!=size:raise AuditError(f"0x{start:08x}: residual drift")
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if len(body)!=size:raise AuditError("image body missing")
  total+=size;exact[start]={"end_exclusive":end,"bytes":size,"sha256":sha256(body),"disposition":"upstream_freetype_source","upstream_module":module,"upstream_function":function,"upstream_license":"FreeType Project License; retained file-specific notices and grants"}
 if (len(exact),total)!=(6,2_602):raise AuditError("batch accounting drift")
 for address,tokens in TOKENS.items():
  begin=log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}");end=log.find("OPENCFW_FUNCTION_END",begin);body=log[begin:end]
  if begin<0 or any(t not in body for t in tokens):raise AuditError(f"0x{address:08x}: semantic signature drift")
 records={};ef=eb=0
 for key,row in old.items():
  address=int(key,16);records[key]=exact.get(address,row)
  if records[key]["disposition"]=="typed_external":ef+=1;eb+=records[key]["bytes"]
 if (ef,eb)!=(93,14_468):raise AuditError("residual accounting drift")
 gaps=[]
 for start,end,name,pin in GAPS:
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if sha256(body)!=pin:raise AuditError("uncatalogued cluster drift")
  gaps.append({"start":start,"end_exclusive":end,"bytes":end-start,"sha256":pin,"source_order_candidate":f"ttcmap.c:{name}","disposition":"typed_external_not_in_none_census","claimed_exact":False})
 return {"status":"candidate-qualified-none-batch8","read_only":True,"hardware_operations":False,"none_group":{"functions":198,"bytes":33_644,"upstream_freetype_source":{"functions":105,"bytes":19_176},"batch8_source_recovered":{"functions":6,"bytes":2_602},"typed_external":{"functions":ef,"bytes":eb},"records":records},"unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],"source_recovered":{"functions":6,"bytes":2_602},"after":{"functions":ef,"bytes":eb}},"uncatalogued_clusters":{"clusters":2,"bytes":sum(x["bytes"] for x in gaps),"records":gaps},"source_pin":{"path":str(SOURCE.relative_to(ROOT)),"bytes":SOURCE_PIN[0],"sha256":SOURCE_PIN[1]},"adapter":{"license":"Apache-2.0","production_routed":False,"upstream_implementation_license_retained":True,"source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--pretty",action="store_true");a=p.parse_args();print(json.dumps(run_audit(),indent=2 if a.pretty else None,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
