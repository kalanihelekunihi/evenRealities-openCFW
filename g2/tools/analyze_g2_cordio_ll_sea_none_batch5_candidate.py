#!/usr/bin/env python3
"""Qualify the PSNames/Adobe glyph-list tranche from the Apollo 0x5D none group."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];CANDIDATE=ROOT/"research/candidates/cordio_ll_sea_none_batch5/runtime_cordio_ll_sea_none_batch5_candidate.c";HEADER=CANDIDATE.with_suffix(".h");PSMODULE=ROOT/"third_party/freetype/src/psnames/psmodule.c";PSTABLES=ROOT/"third_party/freetype/src/psnames/pstables.h";LOAD_BASE=0x00437FE0
PINS={PSMODULE:(16_846,"d21c06ed3dee78cd85f1008275cb888f66099b1e3650e8c8dfdcf0406e7f1368"),PSTABLES:(268_872,"67a4dee05b7bb71f46e53026fa3fefd23ca26604ba46741accae82bc33fa9627")}
ROW_RE=re.compile(r'\{(0x[0-9A-F]+)u,(0x[0-9A-F]+)u,(\d+)u,"([^"]+)","([^"]+)",FT_LICENSE\}')
EXPECTED=(("pstables.h","ft_get_adobe_glyph_index"),("psmodule.c","ps_unicode_value"),("psmodule.c","ps_check_extra_glyph_name"),("psmodule.c","ps_check_extra_glyph_unicode"),("psmodule.c","ps_unicodes_init"),("psmodule.c","ps_unicodes_char_index"),("psmodule.c","ps_unicodes_char_next"))
TOKENS={0x5D94C0:("DAT_005d992c + 2 + uVar7 * 2","*pbVar4 & 0x7f","CONCAT11(pbVar4[2],pbVar4[3])"),0x5D9580:("*param_1 == 0x75","param_1[1] == 0x6e","param_1[2] == 0x69","| 0x80000000"),0x5D96B6:("9 < uVar2","FUN_0046cacc","param_4 + uVar2 * 4"),0x5D96F8:("9 < uVar1","param_2 + uVar1 * 4","= 2"),0x5D9716:("param_3 + 10","local_74 [10]","FUN_005d9580","0x7fffffff","local_78 = 0xa3"),0x5D9840:("0x7fffffff","puVar6 + 2","puVar4[1]"),0x5D9890:("*param_2 + 1","0x7fffffff","*param_2 = uVar2")}
class AuditError(RuntimeError):pass
def sha256(d:bytes)->str:return hashlib.sha256(d).hexdigest()
def load_prior():
 p=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch4_candidate.py";s=importlib.util.spec_from_file_location("open_cfw_none_batch4_dependency",p)
 if s is None or s.loader is None:raise AuditError("could not load prior analyzer")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run_audit()->dict[str,Any]:
 pm=load_prior();prior=pm.run_audit();batch3=pm.load_prior();batch2=batch3.load_prior();batch1=batch2.load_prior();hop4=batch1.load_prior();anchor=hop4.load_prior();hop2=anchor.load_hop2_analyzer();image=hop2.authenticate(hop4.IMAGE);log=batch3.pinned(batch3.LOG31).decode()
 sources={}
 for path,pin in PINS.items():
  data=path.read_bytes()
  if (len(data),sha256(data))!=pin:raise AuditError(f"source drift: {path.name}")
  sources[path.name]=data.decode()
 text=CANDIDATE.read_text();header=HEADER.read_text()
 if (text+header).count("SPDX-License-Identifier: Apache-2.0")!=2 or "no upstream implementation copied" not in text:raise AuditError("adapter license/boundary drift")
 parsed=[(int(a,16),int(e,16),int(n),m,f) for a,e,n,m,f in ROW_RE.findall(text)]
 if len(parsed)!=7 or tuple((x[3],x[4]) for x in parsed)!=EXPECTED:raise AuditError("source identity/order drift")
 for module,function in EXPECTED:
  if re.search(rf"(?m)^  {re.escape(function)}\s*\(",sources[module]) is None:raise AuditError(f"{module}:{function}: definition missing")
 if not (sources["psmodule.c"].find("ps_unicode_value")<sources["psmodule.c"].find("compare_uni_maps")<sources["psmodule.c"].find("ps_check_extra_glyph_name")<sources["psmodule.c"].find("ps_unicodes_char_next")):raise AuditError("psmodule compiled order drift")
 if any("FreeType project" not in s or "LICENSE.TXT" not in s for s in sources.values()):raise AuditError("upstream terms missing")
 old=prior["none_group"]["records"];exact={};total=0
 for start,end,size,module,function in parsed:
  row=old.get(f"0x{start:08X}")
  if row is None or row["disposition"]!="typed_external" or row["end_exclusive"]!=end or row["bytes"]!=size:raise AuditError(f"0x{start:08x}: residual drift")
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if len(body)!=size:raise AuditError("image body missing")
  total+=size;exact[start]={"end_exclusive":end,"bytes":size,"sha256":sha256(body),"disposition":"upstream_freetype_source","upstream_module":module,"upstream_function":function,"upstream_license":"FreeType Project License; retained file-specific notices and grants"}
 if (len(exact),total)!=(7,1_010):raise AuditError("batch accounting drift")
 for address,tokens in TOKENS.items():
  begin=log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}");end=log.find("OPENCFW_FUNCTION_END",begin);body=log[begin:end]
  if begin<0 or any(t not in body for t in tokens):raise AuditError(f"0x{address:08x}: semantic signature drift")
 records={};ef=eb=0
 for key,row in old.items():
  address=int(key,16);records[key]=exact.get(address,row)
  if records[key]["disposition"]=="typed_external":ef+=1;eb+=records[key]["bytes"]
 if (ef,eb)!=(114,22_790):raise AuditError("residual accounting drift")
 gap=image[0x005D9672-LOAD_BASE:0x005D96B6-LOAD_BASE]
 if (len(gap),sha256(gap))!=(68,"4e201d24f3034668ceb06bc6325811eea6ffe95790004757a6bdc9a894a1bad4"):raise AuditError("compare callback gap drift")
 return {"status":"candidate-qualified-none-batch5","read_only":True,"hardware_operations":False,"none_group":{"functions":198,"bytes":33_644,"upstream_freetype_source":{"functions":84,"bytes":10_854},"batch5_source_recovered":{"functions":7,"bytes":1_010},"typed_external":{"functions":ef,"bytes":eb},"records":records},"unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],"source_recovered":{"functions":7,"bytes":1_010},"after":{"functions":ef,"bytes":eb}},"uncatalogued_gap":{"start":0x005D9672,"end_exclusive":0x005D96B6,"bytes":68,"sha256":sha256(gap),"source_order_candidate":"psmodule.c:compare_uni_maps","disposition":"typed_external_not_in_none_census","claimed_exact":False},"source_pins":{p.name:{"bytes":v[0],"sha256":v[1]} for p,v in PINS.items()},"adapter":{"license":"Apache-2.0","production_routed":False,"upstream_implementation_license_retained":True,"source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--pretty",action="store_true");a=p.parse_args();print(json.dumps(run_audit(),indent=2 if a.pretty else None,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
