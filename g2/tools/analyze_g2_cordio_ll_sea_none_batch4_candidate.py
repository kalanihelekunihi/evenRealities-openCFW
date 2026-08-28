#!/usr/bin/env python3
"""Qualify the coherent pshrec.c tranche from the Apollo 0x5D none group."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1];CANDIDATE=ROOT/"research/candidates/cordio_ll_sea_none_batch4/runtime_cordio_ll_sea_none_batch4_candidate.c";HEADER=CANDIDATE.with_suffix(".h");SOURCE=ROOT/"third_party/freetype/src/pshinter/pshrec.c"
SOURCE_PIN=(32_058,"0a639419fb8051eca8836be0eb1c1c9b7d9910ed4907670dde26de166bb33378");LOAD_BASE=0x00437FE0
ROW_RE=re.compile(r'\{(0x[0-9A-F]+)u,(0x[0-9A-F]+)u,(\d+)u,"([^"]+)","([^"]+)",FT_LICENSE\}')
FULL_ORDER=("ps_hint_table_done","ps_hint_table_ensure","ps_hint_table_alloc","ps_mask_done","ps_mask_ensure","ps_mask_test_bit","ps_mask_clear_bit","ps_mask_set_bit","ps_mask_table_done","ps_mask_table_ensure","ps_mask_table_alloc","ps_mask_table_last","ps_mask_table_set_bits","ps_mask_table_test_intersect","ps_mask_table_merge","ps_mask_table_merge_all","ps_dimension_done","ps_dimension_init","ps_dimension_end_mask","ps_dimension_reset_mask","ps_dimension_set_mask_bits","ps_dimension_add_t1stem","ps_dimension_add_counter","ps_dimension_end","ps_hints_done","ps_hints_init","ps_hints_open","ps_hints_stem","ps_hints_t1stem3","ps_hints_t1reset","ps_hints_t2mask","ps_hints_t2counter","ps_hints_close","t1_hints_open","t1_hints_stem","t1_hints_funcs_init","t2_hints_open","t2_hints_stems","t2_hints_funcs_init")
GAPS=((0x005D9254,0x005D9296,"ps_hints_t1reset","80d9852bbdc9c7f581f5b8628b9eb128d14144934d59e67d1b8b72112d610581"),(0x005D934A,0x005D9378,"ps_hints_close","62d7e020602db2cfd9267cdc5c9f7f7c06151a0900b5293c1a09e584028d4945"),(0x005D9378,0x005D9382,"t1_hints_open","60314bec35332200cfe6f3ea1ea156c11fb4338fee7f1446427e3bf22aff3705"),(0x005D9382,0x005D93AC,"t1_hints_stem","57ba9dd06f719688aeddfcc8d3b5de6653475c4fc051b114fb09f797e5b0a378"),(0x005D93D6,0x005D93E0,"t2_hints_open","7905eaa529326f65aa366aebd9fc0ba0a4b7f973ae78cbe4eacddbc32173d408"),(0x005D93E0,0x005D9462,"t2_hints_stems","6a0e297d368ddfd262a0b29398d5ea2da9c19244bbbc6b56bfb8029c138da6d4"))
TOKENS={
0x5D8B10:("param_1[2] = 0","param_1[1] = 0"),0x5D8B2A:("param_2 + 7 & 0xfffffff8","param_3,0xc"),0x5D8B60:("uVar3 * 0xc","FUN_005d8b2a"),0x5D8BA2:("param_1[3] = 0","FUN_00529256"),0x5D8BC0:("uVar3 << 3","param_3,1"),0x5D8C00:("0x80 >> (param_2 & 7)","param_2 >> 3"),0x5D8C1E:("~(0x80U >> (param_2 & 7))",),0x5D8C3E:("FUN_005d8bc0","| 0x80U >>"),0x5D8C76:("FUN_005d8ba2","iVar2 + 0x10"),0x5D8CA8:("param_3,0x10","param_2 + 7 &"),0x5D8CDE:("uVar3 * 0x10","FUN_005d8ca8"),0x5D8D18:("FUN_005d8cde","*param_1 * 0x10"),0x5D8D44:("FUN_005d8bc0","FUN_005d8d18","iVar1 = 0x80"),0x5D8DB4:("& ~(0xff >>","*pbVar1 & *pbVar4"),0x5D8E02:("FUN_005d8c1e","iVar1 * 0x10","*param_1 - 1"),0x5D8ED0:("FUN_005d8db4","FUN_005d8e02"),0x5D8F1C:("param_1 + 0x18","param_1 + 0xc","FUN_005d8b10"),0x5D8F40:("param_1[3] = 0","param_1[6] = 0"),0x5D8F4E:("param_1 + 0xc","* 0x10 + -4"),0x5D8F60:("FUN_005d8f4e","FUN_005d8cde"),0x5D8F7A:("FUN_005d8f60","FUN_005d8d44"),0x5D8FAE:("param_3 == -0x15","param_2 + -0x15","FUN_005d8c3e"),0x5D905C:("FUN_005d8c00","FUN_005d8cde","FUN_005d8c3e"),0x5D9100:("FUN_005d8f4e","FUN_005d8ed0"),0x5D9118:("param_1 + 4","param_1 + 0xd","FUN_005d8f1c"),0x5D913C:("param_1,0x58,0","*param_1 = param_2"),0x5D9152:("param_1 + 0x10","param_1 + 0x34","FUN_005d8f40"),0x5D916E:("param_1 + param_2 * 9 + 4","param_4 + 2","FUN_005d8fae"),0x5D91BC:("param_1 + param_2 * 9 + 4","FUN_005244ee","FUN_005d905c"),0x5D9296:("iVar3 + param_1[4]","FUN_005d8f7a(param_1 + 4","FUN_005d8f7a(param_1 + 0xd"),0x5D92F0:("iVar4 + iVar3","FUN_005d8f7a(param_1 + 4","FUN_005d8f7a(param_1 + 0xd"),0x5D93AC:("param_1,0x1c,0","PTR_FUN_005d91bc","PTR_FUN_005d82c8"),0x5D9462:("param_1,0x1c,0","PTR_FUN_005d9296","PTR_FUN_005d92f0")}
class AuditError(RuntimeError):pass
def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def load_prior():
 path=ROOT/"tools/analyze_g2_cordio_ll_sea_none_batch3_candidate.py";spec=importlib.util.spec_from_file_location("open_cfw_none_batch3_dependency",path)
 if spec is None or spec.loader is None:raise AuditError("could not load prior analyzer")
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def run_audit()->dict[str,Any]:
 pm=load_prior();prior=pm.run_audit();batch2=pm.load_prior();batch1=batch2.load_prior();hop4=batch1.load_prior();anchor=hop4.load_prior();hop2=anchor.load_hop2_analyzer();image=hop2.authenticate(hop4.IMAGE);log=pm.pinned(pm.LOG31).decode()
 data=SOURCE.read_bytes()
 if (len(data),sha256(data))!=SOURCE_PIN:raise AuditError("pshrec source drift")
 source=data.decode();candidate=CANDIDATE.read_text();header=HEADER.read_text()
 if (candidate+header).count("SPDX-License-Identifier: Apache-2.0")!=2 or "no upstream implementation copied" not in candidate:raise AuditError("adapter license/boundary drift")
 parsed=[(int(a,16),int(e,16),int(s),m,f) for a,e,s,m,f in ROW_RE.findall(candidate)]
 if len(parsed)!=33 or len({x[0] for x in parsed})!=33 or any(x[3]!="pshrec.c" for x in parsed):raise AuditError("batch evidence drift")
 selected=tuple(x[4] for x in parsed);expected=tuple(x for x in FULL_ORDER if x not in {g[2] for g in GAPS})
 if selected!=expected:raise AuditError("compiled source order drift")
 positions=[]
 for name in FULL_ORDER:
  match=re.search(rf"(?m)^  {re.escape(name)}\s*\(",source)
  if match is None:raise AuditError(f"pshrec.c:{name}: definition missing")
  positions.append(match.start())
 if positions!=sorted(positions) or "FreeType project" not in source or "LICENSE.TXT" not in source:raise AuditError("upstream order/terms drift")
 old_records=prior["none_group"]["records"];exact={};total=0
 for start,end,size,module,function in parsed:
  old=old_records.get(f"0x{start:08X}")
  if old is None or old["disposition"]!="typed_external" or old["end_exclusive"]!=end or old["bytes"]!=size:raise AuditError(f"0x{start:08x}: prior residual drift")
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if len(body)!=size:raise AuditError(f"0x{start:08x}: body missing")
  total+=size;exact[start]={"end_exclusive":end,"bytes":size,"sha256":sha256(body),"disposition":"upstream_freetype_source","upstream_module":module,"upstream_function":function,"upstream_license":"FreeType Project License; retained file-specific notices and grants"}
 if (len(exact),total)!=(33,2_124):raise AuditError("exact batch accounting drift")
 for address,tokens in TOKENS.items():
  begin=log.find(f"OPENCFW_FUNCTION_BEGIN entry={address:08x}");end=log.find("OPENCFW_FUNCTION_END",begin);body=log[begin:end]
  if begin<0 or any(token not in body for token in tokens):raise AuditError(f"0x{address:08x}: semantic signature drift")
 records={};ef=eb=0
 for key,old in old_records.items():
  address=int(key,16);records[key]=exact.get(address,old)
  if records[key]["disposition"]=="typed_external":ef+=1;eb+=records[key]["bytes"]
 if (ef,eb)!=(121,23_800):raise AuditError("residual accounting drift")
 gaps=[]
 for start,end,function,pin in GAPS:
  body=image[start-LOAD_BASE:end-LOAD_BASE]
  if sha256(body)!=pin:raise AuditError(f"0x{start:08x}: uncatalogued gap drift")
  gaps.append({"start":start,"end_exclusive":end,"bytes":end-start,"sha256":pin,"source_order_candidate":f"pshrec.c:{function}","disposition":"typed_external_not_in_none_census","claimed_exact":False})
 return {"status":"candidate-qualified-none-batch4","read_only":True,"hardware_operations":False,"none_group":{"functions":198,"bytes":33_644,"upstream_freetype_source":{"functions":77,"bytes":9_844},"batch4_source_recovered":{"functions":33,"bytes":2_124},"typed_external":{"functions":ef,"bytes":eb},"records":records},"unsupported_remainder":{"before":prior["unsupported_remainder"]["after"],"source_recovered":{"functions":33,"bytes":2_124},"after":{"functions":ef,"bytes":eb}},"uncatalogued_gaps":{"functions":6,"bytes":sum(x["bytes"] for x in gaps),"records":gaps},"source_pin":{"path":str(SOURCE.relative_to(ROOT)),"bytes":SOURCE_PIN[0],"sha256":SOURCE_PIN[1]},"adapter":{"license":"Apache-2.0","production_routed":False,"upstream_implementation_license_retained":True,"source":str(CANDIDATE.relative_to(ROOT)),"header":str(HEADER.relative_to(ROOT))}}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--pretty",action="store_true");a=p.parse_args();print(json.dumps(run_audit(),indent=2 if a.pretty else None,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
