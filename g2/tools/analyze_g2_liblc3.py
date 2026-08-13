#!/usr/bin/env python3
"""Authenticate the stock Google liblc3 source/version boundary."""
import csv,hashlib,importlib.util,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-liblc3-public-entry-map.tsv";BM=ROOT/"tools/manifests/g2-liblc3-source-boundary.tsv"
PINS={FM:"91d52e123ab83b01abb3b9c4e6f3b477bd3afb0d44ee3fde5367685484a41bbb",BM:"a2ca1447f691bab4dfbba43f6da2a1a4dfa1e285d66ff565a83d8336fcaf47be",ROOT/"third_party/liblc3/PROVENANCE.json":"91b5daf8383c6985807ffda06ed9918ec11e17a805a384948fa66a09ef7a56b3"}
ENTRIES={0x590E64,0x590F78,0x591374,0x59138A};CALLS=[(0x57A938,0x591374),(0x57A9C2,0x590E64),(0x57A9CC,0x590F78),(0x57AA9E,0x591374),(0x57AB14,0x59138A)]
def sh(x):return hashlib.sha256(x).hexdigest()
def snapshot():
 p=ROOT/"third_party/liblc3/verify_snapshot.py";s=importlib.util.spec_from_file_location("verify_liblc3",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.verify()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f"manifest changed: {p.name}")
 snap=snapshot()
 if snap['selected_commit']!="96a3af0beb5487aca3b98a4b992a539a1f6d80d1" or snap['files']!=38:raise c.AuditError("liblc3 snapshot changed")
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if len(rows)!=4 or {int(r['stock_start'],0) for r in rows}!=ENTRIES:raise c.AuditError("public entry inventory changed")
 for r in rows:
  a,z=int(r['stock_start'],0),int(r['stock_end_exclusive'],0);raw=c._slice(b,a,z)
  if len(raw)!=int(r['stock_bytes']) or sh(raw)!=r['stock_sha256']:raise c.AuditError("public entry changed")
 # Two wrappers deliberately branch into shared primary-function tails.
 dec=q.Cs(q.CS_ARCH_ARM,q.CS_MODE_THUMB|q.CS_MODE_LITTLE_ENDIAN|q.CS_MODE_MCLASS);dec.detail=True
 tails=[]
 for a,z in ((0x590E64,0x590E6C),(0x590F78,0x590F84)):
  ii=list(dec.disasm(c._slice(b,a,z),a));tails.append((ii[-1].mnemonic,ii[-1].operands[-1].imm))
 if tails!=[('b',0x590DC8),('b',0x590F68)]:raise c.AuditError("shared-tail wrappers changed")
 ii,cc,ind=q._recover_function(b,0x591374,0x59138A)
 if len(ii)!=10 or cc!=[(0x591382,0x59123A)] or ind:raise c.AuditError("setup wrapper changed")
 ii,cc,ind=q._recover_function(b,0x59138A,0x5915A2)
 if len(ii)!=192 or len(cc)!=18 or len(ind)!=1 or c._uncovered((0x59138A,0x5915A2),ii):raise c.AuditError("encode graph changed")
 # v1.1.3 layout: setup stores dt/sr/sr_pcm at 0/1/2; encode reads dt/sr there.
 setup=list(dec.disasm(c._slice(b,0x5912B2,0x5912CE),0x5912B2));sig=[(i.address,i.mnemonic,i.op_str) for i in setup if i.mnemonic.startswith('strb')]
 if sig!=[(0x5912B6,'strb.w','r7, [sp]'),(0x5912BA,'strb.w','r8, [sp, #1]'),(0x5912C6,'strb.w','sb, [sp, #2]')]:raise c.AuditError("pre-9f1e206 encoder layout changed")
 if c._slice(b,0x59A9AC,0x59A9B0)!=(0x7F7FFFFF).to_bytes(4,'little'):raise c.AuditError("post-bb85f7d FLT_MAX discriminator changed")
 hits=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in ENTRIES:hits.append((a,y))
 if hits!=CALLS or c._pair_digest(hits)!="36909f9489dab1c8f1ef70c8e1e6734fd037f6bded774d1235c2065cc37857b6":raise c.AuditError("public entry callers changed")
 return {"schema_version":1,"family":"Google liblc3","origin":"https://github.com/google/liblc3","license":"Apache-2.0","selected":{"version":"v1.1.3","commit":"96a3af0beb5487aca3b98a4b992a539a1f6d80d1","tree":"d5613b74b5d271bb7b263d85d1b9b913b4dfb74b","exact_public_commit_recoverable":False,"exact_private_checkout_recoverable":False},"compatibility":{"earliest_proven_commit":"bb85f7dde4195bfc0fca9e9c7c2eed0f8694203c","latest_proven_commit":"1de85e2d9b8f8f3dffb50f70881b3475bbdfb803","first_excluded_successor":"9f1e206b34546e858e11065151ae38ff4efc4c77","sns_flt_max_present":True,"pre_ltpf_bypass_layout":True},"stock":{"public_entries":4,"direct_public_entry_calls":5,"encoder_field_offsets":{"dt":0,"sr":1,"sr_pcm":2},"lc3_encode_direct_calls":18,"lc3_encode_indirect_loader_calls":1},"snapshot":{"files":38,"byte_identical":True},"production":{"production_routed":False,"remaining_gates":["target build-profile closure","floating-point and performance validation","audio-buffer integration","LC3 interoperability validation"]}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
