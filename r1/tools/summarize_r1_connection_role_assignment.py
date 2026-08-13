#!/usr/bin/env python3
"""Pin symmetric R1 phone/glasses connection-handle assignment policy."""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path
from typing import Any
from summarize_r1_gomore_call_graph import direct_thumb_branches_to

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_IMAGE=ROOT/"research/decompilation/rebuild/rebuilt-application.bin"
BASE=0x27000
IMAGE_SHA="0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
R1_CONNECTION_ROLE_ASSIGNMENT_FUNCTIONS: tuple[dict[str,Any],...]=(
 {"entry":0x4D654,"end_exclusive":0x4D802,"size":430,"symbol":"r1_glasses_connection_role_assign","sha256":"443657cb657e3b72a0a20e7944f95a8f8c0758272157a9b0758ea0882e2c37ba","callers":((0x4F9E2,"BL"),(0x5D6D2,"BL"),(0x92C22,"BL")),"inventory":"ghidra_functions_csv","provider_family":"r1_product_specific","source_disposition":"clean_room_behavior_only"},
 {"entry":0x4DA28,"end_exclusive":0x4DBD6,"size":430,"symbol":"r1_phone_connection_role_assign","sha256":"51bdbf6412fad98d89416e28326a3735035b9d2e1b8c30d8d2c2edec3c93230e","callers":((0x84340,"BL"),),"inventory":"ghidra_functions_csv","provider_family":"r1_product_specific","source_disposition":"clean_room_behavior_only"},
)

def summarize(path:Path)->dict[str,Any]:
 b=path.read_bytes(); digest=hashlib.sha256(b).hexdigest()
 if digest!=IMAGE_SHA: raise ValueError("unexpected application image")
 out=[]
 for f in R1_CONNECTION_ROLE_ASSIGNMENT_FUNCTIONS:
  e=int(f["entry"]); body=b[e-BASE:int(f["end_exclusive"])-BASE]; callers=tuple(direct_thumb_branches_to(b,BASE,e))
  if len(body)!=f["size"] or hashlib.sha256(body).hexdigest()!=f["sha256"] or callers!=f["callers"]: raise ValueError(f"role assignment changed at 0x{e:08x}")
  out.append({**f,"entry":f"0x{e:08x}","end_exclusive":f"0x{int(f['end_exclusive']):08x}","callers":[{"callsite":f"0x{x:08x}","kind":k} for x,k in callers]})
 pointers=[struct.unpack_from("<I",b,a-BASE)[0] for a in (0x4D804,0x4DBD8)]
 if pointers!=[0x200064B2,0x200064B2]: raise ValueError("role state pointer changed")
 return {"analysis":"R1 symmetric connection-role assignment","image_sha256":digest,"function_count":2,"function_bytes":860,"functions":out,"behavior":{"invalid_handle":"0xffff","phone_offset":8,"glasses_offset":10,"assigns_only_empty_target":True,"cross_role_reuse_is_conflict":True,"successful_assignment_publishes_role":[1,2],"stock_cross_role_assertion_preserved":False},"boundary":{"provider_family":"r1_product_specific","source_disposition":"clean_room_behavior_only","nordic_connection_state_external":True,"logging_and_fatal_assert_external":True}}

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("image",nargs="?",type=Path,default=DEFAULT_IMAGE);print(json.dumps(summarize(p.parse_args().image),indent=2,sort_keys=True))
