#!/usr/bin/env python3
"""Authenticate a typed boundary for the third-largest EM9305 residual."""
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
OBJDUMP=ROOT/"research/corpus/em9305/size-delta/opencfw-em9305-application-objdump.txt"
RESIDUAL=ROOT/"tools/manifests/em9305-residual-provenance-map.tsv"
CANDIDATE=ROOT/"components/shared/em9305/runtime_controller_master_connection_boundary.c"
HEADER=CANDIDATE.with_suffix(".h"); MANIFEST=ROOT/"tools/manifests/em9305-master-connection-boundary.tsv"
PINS={IMAGE:(211948,"91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"),
OBJDUMP:(3463728,"13d1e9c7c0d2c2d3db9436d21ec6d90a39622446cb8ab96de5c2c01ba752916f"),
RESIDUAL:(47936,"2ac24d2abf1f4a4fbce236a82f4591a38dfdb0a71c5ca5b2f8e88bcd9a722d36"),
CANDIDATE:(787,"202c74333ef77d29dfcb3d5be1dd0cc6f412ffa94354490aa24282d6189de4f8"),
HEADER:(1191,"186b4d7910d3939f52c30bdeaf8b2ea70622f0cb003be205ef4f2754bd962902"),
MANIFEST:(1625,"2b6237418c5034b0e778ee7c383ff3bd9ceffdfa50c1f67abd829906dc676d29")}
START,END=0x31DFD0,0x31E5EC; SHA="3a7f6643a63279e0867a3ca07b8b3fa9c1e73ece8ca7fdc04b9eaabde38dc079"
ENTRIES=((0x31DFD0,0x31E458,"541461772f74fba15389824540d274572e6740f3ef9c43f542bbe90e91422af2"),
(0x31E458,0x31E4A0,"f52862be21f2c761518a800a3c8907c36c8d4a0e389d1dcde6361152f54ca0dd"),
(0x31E4A0,0x31E5EC,"400e2b144c390c4774c717406926af3d91b9d69dc857ffaa7949c6c73a2954c2"))
class BoundaryError(RuntimeError): pass
def h(x:bytes)->str:return hashlib.sha256(x).hexdigest()
def run_audit()->dict[str,Any]:
 data={}
 for p,pin in PINS.items():
  b=p.read_bytes()
  if (len(b),h(b))!=pin: raise BoundaryError(f"{p}: identity drift")
  data[p]=b
 image=data[IMAGE]; base=0x302400; off=0x424
 segment=image[off+START-base:off+END-base]
 if h(segment)!=SHA: raise BoundaryError("master-connection segment drift")
 decisions=[]
 for start,end,sha in ENTRIES:
  body=image[off+start-base:off+end-base]
  if h(body)!=sha: raise BoundaryError("master-connection entry drift")
  decisions.append({"start":start,"end_exclusive":end,"bytes":end-start,"sha256":sha})
 text=data[OBJDUMP].decode("ascii")
 for address in (START,0x31E458,0x31E4A0):
  if not re.search(rf"^\s*{address:x}:.*\benter_s\b",text,re.M): raise BoundaryError("entry prologue drift")
 for source,target in ((0x31DC96,START),(0x31DFA0,0x31E458),(0x31DFC2,0x31E458),(0x31E83E,0x31E4A0),(0x31FA06,0x31E4A0),(0x322792,0x31E4A0)):
  if not re.search(rf"^\s*{source:x}:.*;0x{target:x}\b",text,re.M): raise BoundaryError("entry xref drift")
 combined=data[CANDIDATE].decode()+data[HEADER].decode()
 if combined.count("SPDX-License-Identifier: MIT")!=2 or combined.count("open_cfw_em9305_mst_conn_boundary(")!=2: raise BoundaryError("candidate API drift")
 rows=list(csv.DictReader(data[RESIDUAL].decode().splitlines(),delimiter="\t")); row=[r for r in rows if int(r["start"],16)==START]
 if len(row)!=1 or (int(row[0]["end"],16),int(row[0]["size"]),row[0]["sha256"],row[0]["ownership_category"])!=(END,END-START,SHA,"proprietary_modern_controller_source_unavailable"): raise BoundaryError("residual row drift")
 manifest=list(csv.DictReader(data[MANIFEST].decode().splitlines(),delimiter="\t"))
 if len(manifest)!=6 or manifest[-1]["name"]!="deferred by project direction": raise BoundaryError("manifest drift")
 return {"status":"candidate-qualified-fail-closed","read_only":True,"hardware_operations":False,"license":"MIT","decision":{"start":START,"end_exclusive":END,"bytes":END-START,"sha256":SHA,"readiness":"typed_unsupported_external_boundary","decision":"three_entry_master_connection_boundary"},"entries":decisions,"entry_count":3,"source_correlations":["probable lctrMstConnEndOp","probable lctrMstConnExecute","probable lctrMstConnExecuteSm"],"exact_source_available":False,"redistribution_authority_resolved":False,"candidate":{"production_routed":False},"hardware_validation":"deferred by project direction"}
def main()->int:
 a=argparse.ArgumentParser(description=__doc__);a.add_argument("--json",action="store_true");r=run_audit();print(json.dumps(r,indent=2,sort_keys=True) if a.parse_args().json else "EM9305 master connection: candidate-qualified-fail-closed");return 0
if __name__=="__main__":raise SystemExit(main())
