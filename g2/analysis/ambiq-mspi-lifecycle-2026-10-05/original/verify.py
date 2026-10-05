#!/usr/bin/env python3
"""Verify bounded MSPI disable/deinitialize firmware spans and named callers."""
import hashlib, json, re, struct
from pathlib import Path
if not __debug__: raise SystemExit("run with assertions enabled")
ROOT=Path(__file__).resolve().parents[4]
OTA=ROOT/"g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GH=ROOT/"g2/research/corpus/apollo-main/ghidra/open-2026-09-29"
OUT=Path(__file__).resolve().parent
BASE=0x438000
TARGETS={0x4c0ea8:(118,"ed26e7d54404bbf50b8edbe0b10fd5f264caef39b8aed9fe466f3d41233f794d"),0x4c0f24:(56,"17e2e38a57e5a1669a591cf61ad92ff4b5ca8a1747673512410737ac452d689b")}
CALLERS={0x46fb0c:(812,"68c702cca39cea94a9650b5c456229c1fd46b884490bb97f04879c8b56326c21"),0x470d7c:(258,"f892a262286d481a8a0eeec05aefc68475eb47f3e39bdecd97e75d1b1f9a14af"),0x593200:(136,"c6bf824363ffff362ae0a571e41a4d6e381679282365e4f3f2281340675e280c"),0x59c876:(266,"5e8785ffb95aadc3c3d35d60b19deb17c8e88bc3c4370d0097258ccec38d4d4b")}
def sha(x): return hashlib.sha256(x).hexdigest()
ota=OTA.read_bytes(); image=ota[32:]
assert len(ota)==3523396 and sha(ota)=="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
assert len(image)==3523364 and sha(image)=="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
run=json.loads((GH/"RUN.json").read_text()); assert run["base"]=="0x00438000" and run["image_sha256"]==sha(image)
records=[json.loads(x) for x in (GH/"functions-000.jsonl").read_text().splitlines() if x.strip()]
byaddr={int(x["entry"],16):x for x in records}
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS); md.detail=True
outfunc={}; lines=[f"OTA sha256={sha(ota)} size={len(ota)}; decoded image sha256={sha(image)} size={len(image)}, runtime base=0x{BASE:08x}, OTA preamble=32 bytes."]
for a,(n,h) in TARGETS.items():
 body=image[a-BASE:a-BASE+n]; rec=byaddr[a]
 assert len(body)==n and sha(body)==h and rec["body_bytes"]==n and rec["body_sha256"]==h and int(rec["body_end_inclusive"],16)==a+n-1
 outfunc[f"0x{a:08x}"]={"name":rec["name"],"image_range":[f"0x{a-BASE:x}",f"0x{a-BASE+n:x}"],"ota_file_range":[f"0x{a-BASE+32:x}",f"0x{a-BASE+n+32:x}"],"size":n,"sha256":h,"bytes_hex":body.hex()}
 lines.append(f"\n{a:08x} {rec['name']} [{a:08x},{a+n:08x}) {n}B sha256={h}")
 for ins in md.disasm(body,a):
  t=f"{ins.address:08x} {ins.bytes.hex():<8} {ins.mnemonic:<10} {ins.op_str}"
  if ins.mnemonic.startswith("ldr") and "[pc," in ins.op_str:
   m=re.search(r"\[pc, #(-?0x[0-9a-f]+|-?\d+)\]",ins.op_str)
   if m:
    lit=((ins.address+4)&~3)+int(m.group(1),0); val=struct.unpack_from("<I",image,lit-BASE)[0]
    t+=f" ; literal [0x{lit:08x}]=0x{val:08x}"
  lines.append(t)
for a,(n,h) in CALLERS.items():
 body=image[a-BASE:a-BASE+n]; rec=byaddr[a]
 assert len(body)==n and sha(body)==h and rec["body_bytes"]==n and rec["body_sha256"]==h
 calls=[]
 for ins in md.disasm(body,a):
  if ins.mnemonic in ("bl","blx"):
   try: target=int(ins.op_str.split()[0].lstrip("#"),0)
   except ValueError: continue
   if target in TARGETS: calls.append({"pc":f"0x{ins.address:08x}","target":f"0x{target:08x}","bytes":ins.bytes.hex()})
 assert calls, f"expected direct lifecycle call from {a:x}"
 outfunc[f"caller_0x{a:08x}"]={"name":rec["name"],"size":n,"sha256":h,"lifecycle_callsites":calls}
source_files={"am_hal_mspi.c":"5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f","am_hal_mspi.h":"2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b","apollo510.h":"b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797","am_hal_global.h":"05218d399ad4bb1338aa76d84f76bcc9e8f8585cf8c1530e262316cfddc6b075"}
for name,expected in source_files.items():
 assert sha((ROOT/"g2/build/foundation/ambiq-upstream"/name).read_bytes())==expected
result={"verification":"PASS","mapping":{"ota_sha256":sha(ota),"ota_size":len(ota),"image_sha256":sha(image),"image_size":len(image),"preamble_bytes":32,"base":"0x00438000","rule":"decoded offset=runtime-0x438000; OTA file offset=decoded offset+32"},"functions":outfunc,"decoded_field_accesses":{"disable":{"handle_prefix_word":"+0x00","enabled_test":"bit25 (negative after LSL #6)","module_index":"+0x04","pending_hp_count":"+0x840 (element 0x210)","pending_cq_count":"+0x20 (element 8)","pTCB":"+0x18 (element 6)","xip_off_min_delay":"+0x8cc (element 0x233)"},"deinitialize":{"handle_prefix_word":"+0x00","module_index":"+0x04","clears_prefix_mask":"0x01000000 (bInit bit per pinned SDK prefix definition)"}},"literals":{"0x004c0f68":"0x01bebebe","0x004c0f5c":"0x40060000"},"source_files":source_files,"limits":["Offsets are byte offsets inferred directly from authenticated word accesses; no complete private-structure layout is asserted.","Caller interpretations are static and limited to authenticated instructions/decompilation; no runtime state transition is tested.","Pinned-source behavioral correspondence is not compiler byte reproduction."]}
(OUT/"disassembly.txt").write_text("\n".join(lines)+"\n")
with (OUT/"results.json").open("x") as f: json.dump(result,f,indent=2,sort_keys=True); f.write("\n")
print("PASS: lifecycle body and caller hashes, mapping, Ghidra records, and direct callsites")
