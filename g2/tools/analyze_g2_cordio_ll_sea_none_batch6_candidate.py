#!/usr/bin/env python3
"""Qualify the SFNT PostScript-name tranche from the Apollo 0x5D none group."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];CANDIDATE=ROOT/"research/candidates/cordio_ll_sea_none_batch6/runtime_cordio_ll_sea_none_batch6_candidate.c";HEADER=CANDIDATE.with_suffix(".h");SOURCE=ROOT/"third_party/freetype/src/sfnt/sfdriver.c";SOURCE_PIN=(34_308,"79c368e8d3a933bb1353295046aa991d342ee272fb9b3654fb852ced396b10be");LOAD_BASE=0x00437FE0
ROW_RE=re.compile(r'\{(0x[0-9A-F]+)u,(0x[0-9A-F]+)u,(\d+)u,"([^"]+)","([^"]+)",FT_LICENSE\}');EXPECTED=("fmix32","murmur_hash_3_128","get_win_string","get_apple_string","sfnt_get_name_id","fixed2float","sfnt_get_var_ps_name","sfnt_get_ps_name")
TOKENS={0x5DA1E8:("param_1 >> 0x10","uVar1 >> 0xd","uVar1 >> 0x10"),0x5DA202:("param_2 / 0x10","param_2 & 0xf","* 0x8000","FUN_005da1e8","param_4[3]"),0x5DA446:("param_3 + 8) >> 1","pcVar5 = pcVar5 + 2","FUN_00528a66","FUN_00529256"),0x5DA518:("param_3 + 8) + 1","pcVar5 = pcVar5 + 1","FUN_00528a66","FUN_00529256"),0x5DA5D6:("param_1 + 0x154","iVar2 * 0x14","psVar3[2] == 0x409","*param_3 = -1"),0x5DA656:("param_1 >> 0x10","param_1 & 0xffff","iVar1 / 0x10000","*param_2 = 0x2e"),0x5DA73A:("param_1 + 0x2c4","FUN_005da5d6(param_1,0x19","FUN_005da446","FUN_005da518","0x7fffffff"),0x5DAA9C:("param_1 + 0x2ac","FUN_005da5d6(param_1,6","FUN_005da73a","PTR_LAB_005da1a8")}
GAPS=((0x005DA1A8,0x005DA1E8,"sfnt_is_postscript + sfnt_is_alphanumeric","ae66aabc8ef5c1c064ec5cb4d2030c33227b8ca7a22577b866fb013bb8e6d96c"),(0x005DAB3A,0x005DAB8E,"sfnt_get_charset_id","60e66e74fe063a81d5d6577d8084e46159d92b37cacce7e438d9b4a292174d6c"))
class AuditError(RuntimeError):pass
def sha256(d:bytes)->str:return hashlib.sha256(d).hexdigest()
def load_prior():
 p=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch5_candidate.py";s=importlib.util.spec_from_file_location("open_cfw_none_batch5_dependency",p)
 if s is None or s.loader is None:raise AuditError("could not load prior analyzer")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run_audit()->dict[str,Any]:
 pm=load_prior();prior=pm.run_audit();batch4=pm.load_prior();batch3=batch4.load_prior();batch2=batch3.load_prior();batch1=batch2.load_prior();hop4=batch1.load_prior();anchor=hop4.load_prior();hop2=anchor.load_hop2_analyzer();image=hop2.authenticate(hop4.IMAGE);log=batch3.pinned(batch3.LOG31).decode()
 data=SOURCE.read_bytes()
 if (len(data),sha256(data))!=SOURCE_PIN:raise AuditError("sfdriver source drift")
 source=data.decode();text=CANDIDATE.read_text();header=HEADER.read_text()
 if (text+header).count("SPDX-License-Identifier: Apache-2.0")!=2 or "no upstream implementation copied" not in text:raise AuditError("adapter license/boundary drift")
 parsed=[(int(a,16),int(e,16),int(n),m,f) for a,e,n,m,f in ROW_RE.findall(text)]
 if len(parsed)!=8 or tuple(x[4] for x in parsed)!=EXPECTED or any(x[3]!="sfdriver.c" for x in parsed):raise AuditError("source identity/order drift")
 positions=[]
 for function in EXPECTED:
  match=re.search(rf"(?m)^  {re.escape(function)}\s*\(",source)
  if match is None:raise AuditError(f"sfdriver.c:{function}: definition missing")
  positions.append(match.start())
 if positions!=sorted(positions) or "FreeType project" not in source or "LICENSE.TXT" not in source:raise AuditError("upstream order/terms drift")
 if not (source.find("sfnt_is_postscript")<positions[0] and positions[-1]<source.find("sfnt_get_charset_id")):raise AuditError("omitted source boundary drift")
 old=prior["none_group"]["records"];exact={};total=0
 for start,end,size,module,function in parsed:
  row=old.get(f"0x{start:08X}")
  if row is None or row["disposition"]!="typed_external" or row["end_exclusive"]!=end or row["bytes"]!=size:raise AuditError(f"0x{start:08x}: residual drift")
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if len(body)!=size:raise AuditError("image body missing")
  total+=size;exact[start]={"end_exclusive":end,"bytes":size,"sha256":sha256(body),"disposition":"upstream_freetype_source","upstream_module":module,"upstream_function":function,"upstream_license":"FreeType Project License; retained file-specific notices and grants"}
 if (len(exact),total)!=(8,2_386):raise AuditError("batch accounting drift")
 for address,tokens in TOKENS.items():
  begin=log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}");end=log.find("OPENCFW_FUNCTION_END",begin);body=log[begin:end]
  if begin<0 or any(t not in body for t in tokens):raise AuditError(f"0x{address:08x}: semantic signature drift")
 records={};ef=eb=0
 for key,row in old.items():
  address=int(key,16);records[key]=exact.get(address,row)
  if records[key]["disposition"]=="typed_external":ef+=1;eb+=records[key]["bytes"]
 if (ef,eb)!=(106,20_404):raise AuditError("residual accounting drift")
 gaps=[]
 for start,end,name,pin in GAPS:
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if sha256(body)!=pin:raise AuditError("uncatalogued cluster drift")
  gaps.append({"start":start,"end_exclusive":end,"bytes":end-start,"sha256":pin,"source_order_candidate":f"sfdriver.c:{name}","disposition":"typed_external_not_in_none_census","claimed_exact":False})
 return {"status":"candidate-qualified-none-batch6","read_only":True,"hardware_operations":False,"none_group":{"functions":198,"bytes":33_644,"upstream_freetype_source":{"functions":92,"bytes":13_240},"batch6_source_recovered":{"functions":8,"bytes":2_386},"typed_external":{"functions":ef,"bytes":eb},"records":records},"unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],"source_recovered":{"functions":8,"bytes":2_386},"after":{"functions":ef,"bytes":eb}},"uncatalogued_clusters":{"clusters":2,"bytes":sum(x["bytes"] for x in gaps),"records":gaps},"source_pin":{"path":str(SOURCE.relative_to(ROOT)),"bytes":SOURCE_PIN[0],"sha256":SOURCE_PIN[1]},"adapter":{"license":"Apache-2.0","production_routed":False,"upstream_implementation_license_retained":True,"source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--pretty",action="store_true");a=p.parse_args();print(json.dumps(run_audit(),indent=2 if a.pretty else None,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
