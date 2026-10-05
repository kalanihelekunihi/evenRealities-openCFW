#!/usr/bin/env python3
"""Authenticate the MSPI-to-CMDQ disable and force-termination path."""
import hashlib,json,re,struct
from pathlib import Path
if not __debug__: raise SystemExit("run with assertions enabled")
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent
GH=ROOT/"g2/research/corpus/apollo-main/ghidra/open-2026-09-29"; BASE=0x438000
OTA=ROOT/"g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
TARGETS={0x4bfd62:(12,"102a9805750570707a8280660f1f121ad5073cf0a86058ff2409986dba84da65"),0x538e8c:(66,"e551b7b0af10daaeae0056297928d36e9754c6cb212984e37afc0d3bb7354651"),0x4bfc86:(58,"69478f026f1d9f7c23279db04edcfaaf1218e1b5da69e33f9cc3cb0771562865"),0x53909a:(98,"7b9043e48ae0dd5f4e067a1f0884e7696abcc0bbd570b345a76391a8de201bad"),0x538d18:(64,"b509adac0c08c9239aabb77c270b559aa76cd2b797bc473f2d0d01a22e3c2837")}
CALLERS={0x4c0ea8:(118,"ed26e7d54404bbf50b8edbe0b10fd5f264caef39b8aed9fe466f3d41233f794d"),0x4c240e:(712,"8c43c0d8fd418e04cf808e80d00867981dc2a3eaefb23ee0227ed39538484164"),0x4c26e0:(1014,"4567f43c1d695764bc62c881fbf0bc9c3766c06e9d16d66454f1b87ec4b0ae5b"),0x55c168:(12,"f5e30cdb754dc1742a5c599a405af2dff0a6ec4bfc20ae8786cc15ba9663e6c6"),0x55c11a:(32,"16672d60ac38e4b05ed2c1fc0964f41ae3e528f3b57c1455457da25eb60d7052"),0x538ece:(180,"74a57509503aa339dce2f40cdbff6d283585b7eac2f526c7d4939548e55baa3c"),0x53901a:(128,"54f4dd9239da03fdb828d767378d1650218cb59a76e2f1cc57e628ff0bac9cd4")}
def sha(b):return hashlib.sha256(b).hexdigest()
ota=OTA.read_bytes(); image=ota[32:]
assert len(ota)==3523396 and sha(ota)=="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
assert len(image)==3523364 and sha(image)=="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
run=json.loads((GH/"RUN.json").read_text()); assert run["base"]=="0x00438000" and run["image_sha256"]==sha(image)
records=[json.loads(l) for l in (GH/"functions-000.jsonl").read_text().splitlines() if l.strip()]; by={int(x["entry"],16):x for x in records}
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS); md.detail=True
alltargets=set(TARGETS); out={}; lines=[f"OTA {sha(ota)} ({len(ota)} bytes); decoded image {sha(image)} ({len(image)} bytes), base 0x{BASE:08x}; file payload starts +32."]
for a,(n,h) in TARGETS.items():
 b=image[a-BASE:a-BASE+n]; r=by[a]; assert len(b)==n and sha(b)==h and r["body_bytes"]==n and r["body_sha256"]==h and int(r["body_end_inclusive"],16)==a+n-1
 out[f"0x{a:08x}"]={"name":r["name"],"image_range":[f"0x{a-BASE:x}",f"0x{a-BASE+n:x}"],"ota_file_range":[f"0x{a-BASE+32:x}",f"0x{a-BASE+n+32:x}"],"size":n,"sha256":h,"bytes_hex":b.hex()}
 lines.append(f"\n{a:08x} {r['name']} [{a:08x},{a+n:08x}) {n}B sha256={h}")
 for i in md.disasm(b,a):
  s=f"{i.address:08x} {i.bytes.hex():<8} {i.mnemonic:<10} {i.op_str}"
  if i.mnemonic.startswith("ldr") and "[pc," in i.op_str:
   m=re.search(r"\[pc, #(-?0x[0-9a-f]+|-?\d+)\]",i.op_str)
   if m:
    lit=((i.address+4)&~3)+int(m.group(1),0); v=struct.unpack_from("<I",image,lit-BASE)[0]; s+=f" ; literal [0x{lit:08x}]=0x{v:08x}"
  lines.append(s)
for a,(n,h) in CALLERS.items():
 b=image[a-BASE:a-BASE+n];r=by[a];assert len(b)==n and sha(b)==h and r["body_bytes"]==n and r["body_sha256"]==h
 calls=[]
 for i in md.disasm(b,a):
  if i.mnemonic in ("bl","blx"):
   try:t=int(i.op_str.split()[0].lstrip("#"),0)
   except ValueError:continue
   if t in alltargets:calls.append({"pc":f"0x{i.address:08x}","target":f"0x{t:08x}","bytes":i.bytes.hex()})
 assert calls,(hex(a),"missing callsite")
 out[f"caller_0x{a:08x}"]={"name":r["name"],"size":n,"sha256":h,"callsites":calls}
source={"am_hal_cmdq.c":"60aa2126ca01cd72f746a92d6f34a13e909fdab24ebfab6d6b0a70b026d8fa83","am_hal_cmdq.h":"0113aed2f109c5f022d38055b83a75c2cf141e8621177296757fc8315926762f","am_hal_mspi.c":"5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f","am_hal_mspi.h":"2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b","apollo510.h":"b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797"}
for name,h in source.items():assert sha((ROOT/"g2/build/foundation/ambiq-upstream"/name).read_bytes())==h
result={"verification":"PASS","mapping":{"ota_sha256":sha(ota),"ota_size":len(ota),"decoded_sha256":sha(image),"decoded_size":len(image),"base":"0x00438000","preamble_bytes":32,"rule":"image offset=runtime-base; original-file offset=image offset+32"},"functions":out,"source_files":source,"scope_findings":{"mspi_disable_wrapper":"reads handle-local word +0x828 and passes it to CMDQ disable; return value forwarded unchanged","cmdq_disable":"validates CMDQ handle; if disabled returns success; if enabled clears hardware CQEN through pReg->regCQCfg and clears prefix bEnable; no wait or memory free occurs in this function","mspi_term_wrapper":"reads module +0x04, obtains handle at global state base + module*0x8d0 + 0x828 (literal base shown in disassembly), calls CMDQ term with force=1, then zeros that global pointer; return status ignored; wrapper returns success","cmdq_term_force_true":"calls update_indices first; force=true bypasses only the curIdx!=endIdx IN_USE return; then clears CMDQ bInit, disables CQ, and clears pause-enable bit. No wait loop or memory free occurs in inspected wrapper/term/update_indices bodies","update_indices":"critical section; reads current hardware index and CQ address registers, updates software curIdx and cmdQHead fields; no wait/free"},"limits":["This proves only the listed original bodies and source APIs; callees are not behaviorally expanded beyond directly inspected target functions.","No runtime/hardware behavior or compiled-source identity was tested."]}
(OUT/"disassembly.txt").write_text("\n".join(lines)+"\n")
with (OUT/"results.json").open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
print("PASS: five CMDQ/MSPI bodies, image mapping, Ghidra body records, selected caller references, and pinned source hashes")
