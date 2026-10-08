#!/usr/bin/env python3
"""Fail closed on the Google liblc3 v1.1.3 source snapshot."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MANIFEST_SHA256="082385608437fbb327afd891c85ca678d2b23f20ac6fe647c3f3079f7e4ca3c5"
COMMIT="96a3af0beb5487aca3b98a4b992a539a1f6d80d1";TREE="d5613b74b5d271bb7b263d85d1b9b913b4dfb74b"
LOWER="bb85f7dde4195bfc0fca9e9c7c2eed0f8694203c";UPPER="1de85e2d9b8f8f3dffb50f70881b3475bbdfb803";EXCLUDED="9f1e206b34546e858e11065151ae38ff4efc4c77"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 m=ROOT/"SNAPSHOT.sha256"
 if sha(m)!=MANIFEST_SHA256:raise RuntimeError("liblc3 hash manifest changed")
 expected={}
 for line in m.read_text().splitlines():
  digest,rel=line.split("  ",1)
  if rel in expected or len(digest)!=64:raise RuntimeError("invalid liblc3 hash manifest")
  expected[rel]=digest
 for rel,digest in expected.items():
  p=ROOT/rel
  if not p.is_file() or sha(p)!=digest:raise RuntimeError(f"liblc3 snapshot changed: {rel}")
 p=json.loads((ROOT/"PROVENANCE.json").read_text())
 if p["upstream"]["selected_commit"]!=COMMIT or p["upstream"]["selected_tree"]!=TREE:raise RuntimeError("liblc3 source selection changed")
 s=p["selection"]
 if (s["earliest_proven_compatible_commit"],s["latest_proven_compatible_commit"],s["first_excluded_successor"])!=(LOWER,UPPER,EXCLUDED):raise RuntimeError("liblc3 compatibility interval changed")
 sns=(ROOT/"src/sns.c").read_text();lc3=(ROOT/"src/lc3.c").read_text();private=(ROOT/"include/lc3_private.h").read_text()
 if "float mse_min = FLT_MAX;" not in sns or "float cmse_min = FLT_MAX;" not in sns:raise RuntimeError("post-bb85f7d SNS discriminator missing")
 if "lc3_setup_encoder(" not in lc3 or "lc3_encode(" not in lc3 or "lc3_frame_samples(" not in lc3 or "lc3_frame_bytes(" not in lc3:raise RuntimeError("public LC3 surface missing")
 if "ltpf_bypass" in private or "lc3_encoder_disable_ltpf" in lc3:raise RuntimeError("post-9f1e206 layout unexpectedly present")
 return {"schema_version":1,"selected_tag":"v1.1.3","selected_commit":COMMIT,"selected_tree":TREE,"files":len(expected),"byte_identical":True,"lower_discriminator":True,"upper_discriminator":True,"exact_private_checkout_proven":False}
if __name__=="__main__":print(json.dumps(verify(),indent=2,sort_keys=True))
