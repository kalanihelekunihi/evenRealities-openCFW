#!/usr/bin/env python3
"""Qualify the third positive-source batch from the Apollo 0x5D none group."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
CANDIDATE=ROOT/"research/candidates/cordio_ll_sea_none_batch3/runtime_cordio_ll_sea_none_batch3_candidate.c"
HEADER=CANDIDATE.with_suffix(".h")
PSHALGO=ROOT/"third_party/freetype/src/pshinter/pshalgo.c"
PSHGLOB=ROOT/"third_party/freetype/src/pshinter/pshglob.c"
LOG31=ROOT/"research/corpus/apollo-main/ghidra/full64-j64-auth/logs/apollo-31.log"
PINS={PSHALGO:(59_738,"cbede1f596434c2348711a1ed12c60448ed14759b52a48c31cf1898564d69842"),PSHGLOB:(23_053,"0f22b4d604c977c377f0eb96c5b460fd74bf70c5a196aabc33ae1b94cdd99cbe"),LOG31:(277_768,"bc0d5ff78b077eedc7358cf9a8257a16bdb0fe1457b3d574240e57f35ebb4bd5")}
LOAD_BASE=0x00437FE0
ROW_RE=re.compile(r'\{ (0x[0-9A-F]+)u, (0x[0-9A-F]+)u, (\d+)u, "([^"]+)", "([^"]+)", FT_LICENSE \}')
EXPECTED={
 "pshalgo.c":("psh_hint_table_find_strong_points","psh_glyph_find_strong_points","psh_glyph_find_blue_points","psh_glyph_interpolate_strong_points","psh_glyph_interpolate_normal_points","psh_glyph_interpolate_other_points","ps_hints_apply"),
 "pshglob.c":("psh_globals_scale_widths","psh_blues_set_zones_0","psh_blues_set_zones","psh_blues_scale_zones","psh_calc_max_height","psh_blues_snap_stem","psh_globals_destroy","psh_globals_set_scale","psh_globals_funcs_init")}
SIGNATURES={
 0x005D7B62:("param_2 + 0x28","uVar2 = 0x80","uVar7 = 0x100","| 0x400"),
 0x005D7D1C:("iVar1 = 0x1e","FUN_005d72a8","FUN_005d7b62","uVar2 + 0x28"),
 0x005D7E1A:("param_1[0x207]","param_1[0x208]","| 0x20","iVar3 + 0x28"),
 0x005D7F04:("FUN_00524606","piVar3[3] + piVar3[2]","iVar5 + 0x28"),
 0x005D7F90:("uVar6 < 0x11","local_64 [16]","FUN_00524606","FUN_00529256"),
 0x005D816C:("uVar12 = 0x10000","FUN_00524754","uVar6 + puVar5[1] * 0x28","uVar3 + 0x24"),
 0x005D82C8:("iVar6 / 0x32","FUN_005d784a","FUN_005d7d1c","FUN_005d816c"),
 0x005D843A:("iVar3 < 0x80","param_1 + 0x14","puVar5 + 3","0xffffffc0"),
 0x005D849A:("FUN_00439c04","0x20","local_28 - 2","piVar7[1] = iVar6"),
 0x005D857C:("param_1 + 0x183","FUN_005d849a","iVar8 / 2 < param_6","puVar4 + 8"),
 0x005D868A:("param_2 * 0x7d","param_1[0x204] * 8","uVar5 < 4","iVar3 < 0x40"),
 0x005D87FA:("uVar1 = uVar1 + 2","param_2 + uVar1 * 2 + 2","param_3 = sVar2"),
 0x005D8828:("*param_4 | 1","*param_4 | 2","param_1[0x207]","param_1[0x206]"),
 0x005D88D4:("param_1[0x34] = 0","param_1[0x1ea] = 0","FUN_00529256"),
 0x005D8A48:("param_1 + 0x194","FUN_005d843a(param_1,1)","FUN_005d868a"),
}
class AuditError(RuntimeError): pass
def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def pinned(path:Path)->bytes:
 data=path.read_bytes()
 if (len(data),sha256(data))!=PINS[path]:raise AuditError(f"source/log drift: {path.name}")
 return data
def load_prior():
 path=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch2_candidate.py";spec=importlib.util.spec_from_file_location("open_cfw_none_batch2_dependency",path)
 if spec is None or spec.loader is None:raise AuditError("could not load prior analyzer")
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def run_audit()->dict[str,Any]:
 prior_module=load_prior();prior=prior_module.run_audit();batch1=prior_module.load_prior();hop4=batch1.load_prior();anchor=hop4.load_prior();hop2=anchor.load_hop2_analyzer()
 image=hop2.authenticate(hop4.IMAGE);log30=hop2.authenticate(hop4.LOG).decode();log31=pinned(LOG31).decode()
 sources={"pshalgo.c":pinned(PSHALGO).decode(),"pshglob.c":pinned(PSHGLOB).decode()}
 candidate=CANDIDATE.read_text();header=HEADER.read_text()
 if (candidate+header).count("SPDX-License-Identifier: Apache-2.0")!=2:raise AuditError("license declarations missing")
 if "no upstream implementation copied" not in candidate:raise AuditError("source boundary statement missing")
 parsed=[(int(a,16),int(e,16),int(s),m,f) for a,e,s,m,f in ROW_RE.findall(candidate)]
 if len(parsed)!=16 or len({x[0] for x in parsed})!=16:raise AuditError("batch evidence drift")
 for module,names in EXPECTED.items():
  actual=tuple(x[4] for x in parsed if x[3]==module)
  if actual!=names:raise AuditError(f"{module}: source-order identity drift")
  source=sources[module];positions=[]
  if "FreeType project" not in source or "LICENSE.TXT" not in source:raise AuditError(f"{module}: terms missing")
  for name in names:
   match=re.search(rf"(?m)^  {re.escape(name)}\s*\(",source)
   if match is None:raise AuditError(f"{module}:{name}: definition missing")
   positions.append(match.start())
  if positions!=sorted(positions):raise AuditError(f"{module}: order drift")
 glob=sources["pshglob.c"]
 if not (glob.find("psh_globals_destroy")<glob.find("psh_globals_new")<glob.find("psh_globals_set_scale")<glob.find("psh_globals_funcs_init")):raise AuditError("pshglob bridge order drift")
 prior_records=prior["none_group"]["records"];exact={};exact_bytes=0
 for start,end,size,module,function in parsed:
  old=prior_records.get(f"0x{start:08X}")
  if old is None or old["disposition"]!="typed_external" or old["end_exclusive"]!=end or old["bytes"]!=size:raise AuditError(f"0x{start:08x}: prior residual drift")
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if len(body)!=size:raise AuditError(f"0x{start:08x}: body missing")
  exact_bytes+=size;exact[start]={"end_exclusive":end,"bytes":size,"sha256":sha256(body),"disposition":"upstream_freetype_source","upstream_module":module,"upstream_function":function,"upstream_license":"FreeType Project License; retained file-specific notices and grants"}
 if (len(exact),exact_bytes)!=(16,3_606):raise AuditError("exact batch accounting drift")
 for address,tokens in SIGNATURES.items():
  begin=log30.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}");end=log30.find("OPENCFW_FUNCTION_END",begin);body=log30[begin:end]
  if begin<0 or any(token not in body for token in tokens):raise AuditError(f"0x{address:08x}: semantic signature drift")
 begin=log31.find("OPENCFW_FUNCTION_BEGIN entry=005d8aa4");end=log31.find("OPENCFW_FUNCTION_END",begin);tiny=log31[begin:end]
 for token in ("*param_1 = PTR_LAB_005d8908","param_1[1] = PTR_FUN_005d8a48","param_1[2] = PTR_FUN_005d88d4"):
  if begin<0 or token not in tiny:raise AuditError("0x005d8aa4: provider table signature drift")
 records={};external_functions=external_bytes=0
 for key,old in prior_records.items():
  address=int(key,16);records[key]=exact.get(address,old)
  if records[key]["disposition"]=="typed_external":external_functions+=1;external_bytes+=records[key]["bytes"]
 if (external_functions,external_bytes)!=(154,25_924):raise AuditError("residual accounting drift")
 bridge=image[0x005D8908-LOAD_BASE:0x005D8A48-LOAD_BASE]
 if (len(bridge),sha256(bridge))!=(320,"a06f5654c8da09df4594adb0640337110be76bcc802406ef175a8465ae7aae47"):raise AuditError("uncatalogued bridge drift")
 return {"status":"candidate-qualified-none-batch3","read_only":True,"hardware_operations":False,
  "none_group":{"functions":198,"bytes":33_644,"upstream_freetype_source":{"functions":44,"bytes":7_720},"batch3_source_recovered":{"functions":16,"bytes":3_606},"typed_external":{"functions":external_functions,"bytes":external_bytes},"records":records},
  "unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],"source_recovered":{"functions":16,"bytes":3_606},"after":{"functions":external_functions,"bytes":external_bytes}},
  "uncatalogued_bridge":{"start":0x005D8908,"end_exclusive":0x005D8A48,"bytes":320,"sha256":sha256(bridge),"disposition":"typed_external_not_in_none_census","source_order_candidate":"pshglob.c:psh_globals_new","claimed_exact":False},
  "source_pins":{p.name:{"bytes":v[0],"sha256":v[1]} for p,v in PINS.items()},
  "adapter":{"license":"Apache-2.0","production_routed":False,"upstream_implementation_license_retained":True,"source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--pretty",action="store_true");args=parser.parse_args();print(json.dumps(run_audit(),indent=2 if args.pretty else None,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
