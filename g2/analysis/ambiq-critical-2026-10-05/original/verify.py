#!/usr/bin/env python3
"""Bounded verification of PRIMASK helpers and scatter-loaded delay-loop prefix."""
import hashlib,json,re,struct
from pathlib import Path
if not __debug__: raise SystemExit("run with assertions enabled")
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent
GH=ROOT/"g2/research/corpus/apollo-main/ghidra/open-2026-09-29"; BASE=0x438000
OTA=ROOT/"g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
TARGETS={0x473934:(8,"6c169e0f7b32e9f34f42114fdbd5292b812805d62399aabd65f2299c040bd120"),0x473940:(8,"720733fcf19a5635fcab0791fcc2b007294712bb27536443ff79490821c168cf"),0x47394c:(6,"081c18c20c2470ed4c2a8de4ac105253647b86c92fad5b1dbe03b841d4a843e7"),0x4807a0:(80,"f95193c502160b469e1579e13223f1cdf488a2d8fab9ec07f686c9101fbed753"),0x43a11e:(126,"41e4a34428bb2c09774785d474f5209201f6551c823f0286eb66063dedc74a9d"),0x5e42b4:(32,"c18f6c848dedbb42dc53582eb239f9f59017656fafad4cc4c948827bb6c342bd"),0x5fa01e:(56,"8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67")}
CALLERS={0x538d18:(64,"b509adac0c08c9239aabb77c270b559aa76cd2b797bc473f2d0d01a22e3c2837"),0x44b0b6:(32,"0ea726bb021d4f4f5fd228701e2911434c9c181155d4390d0f25be39a15259f9"),0x44b0d6:(130,"78bb04a6f49c50c1dd0ab74ac70e8dab14b69fa88f7fea4693ff7533cd03aac3"),0x4446b4:(74,"d86b42c32df5568ab3d2eb0f492a24000573ff39a8ae11f23d74611ae5b3e7bd"),0x46fb0c:(812,"68c702cca39cea94a9650b5c456229c1fd46b884490bb97f04879c8b56326c21"),0x57a65c:(216,"1d8b81348af10ad6b18ebb670b86af5881325f1fa65b3004c75968214e5ff6a0"),0x4c0ea8:(118,"ed26e7d54404bbf50b8edbe0b10fd5f264caef39b8aed9fe466f3d41233f794d"),0x44ab42:(1318,"012c052f6ab7e829129ed966a94cfb1541605b2d05185115c1dfd06cbb9d2898"),0x4bfe60:(118,"b785510f3c3af451e03f6a6f76bfbe5508b9cf6f0246a9e608fccb10b65feb47")}
def sha(b):return hashlib.sha256(b).hexdigest()
ota=OTA.read_bytes(); image=ota[32:]
assert len(ota)==3523396 and sha(ota)=="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
assert len(image)==3523364 and sha(image)=="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
run=json.loads((GH/"RUN.json").read_text()); assert run["base"]=="0x00438000" and run["image_sha256"]==sha(image)
records=[json.loads(x) for x in (GH/"functions-000.jsonl").read_text().splitlines() if x.strip()]; by={int(x["entry"],16):x for x in records}
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
out={};lines=[f"OTA sha256={sha(ota)} size={len(ota)}; decoded image sha256={sha(image)} size={len(image)}, base=0x{BASE:08x}; OTA preamble=32 bytes."]
for a,(n,h) in TARGETS.items():
 b=image[a-BASE:a-BASE+n]; r=by[a]; assert len(b)==n and sha(b)==h and r["body_bytes"]==n and r["body_sha256"]==h and int(r["body_end_inclusive"],16)==a+n-1
 out[f"0x{a:08x}"]={"name":r["name"],"image_range":[f"0x{a-BASE:x}",f"0x{a-BASE+n:x}"],"ota_file_range":[f"0x{a-BASE+32:x}",f"0x{a-BASE+n+32:x}"],"size":n,"sha256":h,"bytes_hex":b.hex()}
 lines.append(f"\n{a:08x} {r['name']} [{a:08x},{a+n:08x}) {n}B sha256={h}")
 for i in md.disasm(b,a):
  s=f"{i.address:08x} {i.bytes.hex():<8} {i.mnemonic:<10} {i.op_str}"
  if i.mnemonic.startswith(("ldr","vldr")) and "[pc," in i.op_str:
   m=re.search(r"\[pc, #(-?0x[0-9a-f]+|-?\d+)\]",i.op_str)
   if m:
    lit=((i.address+4)&~3)+int(m.group(1),0); val=struct.unpack_from("<I",image,lit-BASE)[0];s+=f" ; literal [0x{lit:08x}]=0x{val:08x}"
  if i.mnemonic in ("bl","blx") and i.op_str.strip().lstrip("#")=="0x40":s+=" ; target is ITCM address 0x40 outside main-image mapping"
  lines.append(s)
for a,(n,h) in CALLERS.items():
 b=image[a-BASE:a-BASE+n];r=by[a];assert len(b)==n and sha(b)==h and r["body_bytes"]==n and r["body_sha256"]==h
 calls=[]
 for i in md.disasm(b,a):
  if i.mnemonic in ("bl","blx"):
   try:t=int(i.op_str.split()[0].lstrip("#"),0)
   except ValueError:continue
   if t in set(TARGETS)|{0x40}:calls.append({"pc":f"0x{i.address:08x}","target":f"0x{t:08x}","bytes":i.bytes.hex()})
 assert calls,(hex(a),"no selected helper callsite")
 out[f"caller_0x{a:08x}"]={"name":r["name"],"size":n,"sha256":h,"helper_callsites":calls}
# Validate startup's relative bounds and the compressed relocation record.
word=lambda addr:struct.unpack_from("<I",image,addr-BASE)[0]
table_start=0x5e42d4+word(0x5e42d4);table_end=0x5e42d8+word(0x5e42d8)
assert (table_start,table_end)==(0x75d3c8,0x75d410)
record=0x75d3e4; handler_rel=word(0x75d3e0); handler_target=(0x75d3e0+struct.unpack("<i",struct.pack("<I",handler_rel))[0])&0xffffffff
src_offset,packed_len,dst=struct.unpack_from("<III",image,record-BASE)
src=record+src_offset; src_len=packed_len>>1; stream=image[src-BASE:src-BASE+src_len]
assert handler_target==0x43a11f and (src_offset,packed_len,dst)==(0x36f2a,0x2c,0x40)
assert src==0x79430e and src_len==22 and src+src_len==0x794324==BASE+len(image)
assert stream.hex()=="100b0138fdd17047704750f8043b41043001013af910"
def decode_as_machine(stream):
 """Mirror the verified original decoder's literal/match loop bounds."""
 p=0;out=bytearray();trace=[]
 while p<len(stream):
  tok=stream[p];p+=1;lit_n=tok&3
  if lit_n==0:lit_n=stream[p]+3;p+=1
  literal_start=p;lit_copies=lit_n-1
  for _ in range(lit_copies):out.append(stream[p]);p+=1
  trace.append({"token":f"0x{tok:02x}","literal_count_field":lit_n,"literal_bytes_copied":lit_copies,"literal_source_indices":[literal_start,literal_start+lit_copies]})
  match_n=tok>>4
  if match_n==15:match_n+=stream[p]+15;p+=1
  if match_n:
   off_hi=(tok&0xf)>>2;off_lo=stream[p];p+=1
   if off_hi==3:off_hi=stream[p];p+=1
   dist=off_lo+(off_hi<<8);match_copies=match_n+2
   assert 0<dist<=len(out)
   for _ in range(match_copies):out.append(out[-dist])
   trace[-1].update({"backref_distance":dist,"backref_bytes_copied":match_copies})
 return bytes(out),trace,p
decoded,decoder_trace,consumed=decode_as_machine(stream)
assert consumed==len(stream)==22 and len(decoded)==24
assert decoded.hex()=="0138fdd17047704750f8043b41f8043b013af9d170477047"
assert decoded[:6]==bytes.fromhex("0138fdd17047")
assert [i.mnemonic for i in md.disasm(decoded[:6],0x40)]==["subs","bne","bx"]
result={"verification":"PASS","mapping":{"ota_sha256":sha(ota),"ota_size":len(ota),"decoded_image_sha256":sha(image),"decoded_size":len(image),"base":"0x00438000","payload_preamble_bytes":32,"runtime_image_range":["0x00438000","0x00794324"]},"functions":out,"startup_scatter":{"loader_entry":"0x005e42b4","loader_sha256":TARGETS[0x5e42b4][1],"relative_table_bounds":{"start_anchor":"0x005e42d4","start_displacement":hex(word(0x5e42d4)),"computed_start":hex(table_start),"end_anchor":"0x005e42d8","end_displacement":hex(word(0x5e42d8)),"computed_end":hex(table_end)},"decoder_entry":"0x0043a11e","decoder_sha256":TARGETS[0x43a11e][1],"decoder_behavior":"source start is record base + field0; source bound is field1 >> 1 bytes; field1 bit0 enables destination relocation; destination is field2","record_address":"0x0075d3e0","record_handler_relative_word":hex(handler_rel),"record_handler_thumb_target":hex(handler_target),"record_fields":{"record_base":"0x0075d3e4","source_offset":hex(src_offset),"packed_length":hex(packed_len),"packed_source_bytes":src_len,"source_runtime_range":[hex(src),hex(src+src_len)],"source_ota_file_range":[hex(src-BASE+32),hex(src-BASE+32+src_len)],"destination":"0x00000040"},"stored_stream_hex":stream.hex(),"decoded_output_hex":decoded.hex(),"decoded_output_bytes":len(decoded),"decoder_trace":decoder_trace,"decoded_loop_first6_hex":decoded[:6].hex(),"loop_instructions":["0x40: subs r0, #1","0x42: bne 0x40","0x44: bx lr"],"full_extent_status":"24-byte output is completely decoded from the 22-byte input; no input read is made at the exclusive image end"},"caller_index_counts":{"0x00473940_direct_callers":sum(1 for x in records if "00473940" in x.get("callees",[])),"0x00473934_direct_callers":sum(1 for x in records if "00473934" in x.get("callees",[])),"0x0047394c_direct_callers":sum(1 for x in records if "0047394c" in x.get("callees",[])),"0x004807a0_direct_callers":sum(1 for x in records if "004807a0" in x.get("callees",[]))},"limits":["The caller index counts are Ghidra direct-callee metadata counts; selected caller bodies/call instructions are separately hash-verified above.","The delay loop prefix and complete 24-byte decoder output are recovered; no physical cycle timing was measured.","The stored image includes the scatter record and compressed loop input; execution at 0x40 depends on startup scatter initialization into ITCM.","Delay wrapper floating-point scaling is disassembled but not reimplemented or claimed as complete source behavior."]}
lines.append(f"\nScatter-decoded ITCM[0x40:0x58] from source 0x{src:08x} ({src_len} input bytes): {decoded.hex()}")
for i in md.disasm(decoded,0x40): lines.append(f"{i.address:08x} {i.bytes.hex():<8} {i.mnemonic:<10} {i.op_str}")
(OUT/"disassembly.txt").write_text("\n".join(lines)+"\n")
with (OUT/"results.json").open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
print("PASS: PRIMASK/delay code hashes, selected callers, scatter record, stored input, and bounded delay-loop prefix")
