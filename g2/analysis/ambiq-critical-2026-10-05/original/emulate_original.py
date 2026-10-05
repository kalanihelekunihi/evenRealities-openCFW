#!/usr/bin/env python3
"""Execute the authenticated original IAR-style scatter decoder under Unicorn."""
import hashlib,json
from pathlib import Path
if not __debug__: raise SystemExit("run with assertions enabled")
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent
ota=(ROOT/"g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes(); image=ota[32:]
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(ota)=="36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
decoder=image[0x43a11e-0x438000:0x43a11e-0x438000+126]
assert sha(decoder)=="41e4a34428bb2c09774785d474f5209201f6551c823f0286eb66063dedc74a9d"
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R9,UC_ARM_REG_SP,UC_ARM_REG_LR
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
BASE=0x438000; src=0x79430e; end=0x794324; entry=0x43a11e; sentinel=0x439000
mapping=((len(image)+0xfff)//0x1000)*0x1000
uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
uc.mem_map(BASE,mapping);uc.mem_write(BASE,image)
uc.mem_map(0,0x1000);uc.mem_map(0x20000000,0x10000)
uc.reg_write(UC_ARM_REG_R0,0x75d3e4);uc.reg_write(UC_ARM_REG_R9,0);uc.reg_write(UC_ARM_REG_SP,0x20008000);uc.reg_write(UC_ARM_REG_LR,sentinel|1)
md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS)
ins={x.address:x.bytes.hex() for x in md.disasm(decoder,entry)};trace=[];source_reads=[];violations=[]
def on_code(emu,addr,size,data):
 if entry<=addr<entry+len(decoder):
  b=bytes(emu.mem_read(addr,size)).hex();assert ins.get(addr)==b
  trace.append({"pc":f"0x{addr:08x}","bytes":b})
 elif addr!=sentinel: violations.append(f"0x{addr:08x}")
def on_read(emu,access,address,size,value,data):
 if src-4<=address<=end+4:source_reads.append({"address":f"0x{address:08x}","size":size})
uc.hook_add(UC_HOOK_CODE,on_code);uc.hook_add(UC_HOOK_MEM_READ,on_read)
uc.emu_start(entry|1,sentinel,count=10000)
decoded=bytes(uc.mem_read(0x40,24));ret=uc.reg_read(UC_ARM_REG_R0)
assert not violations and ret==0x75d3f0
assert decoded.hex()=="0138fdd17047704750f8043b41f8043b013af9d170477047"
assert all(src<=int(r["address"],16)<end for r in source_reads if src-4<=int(r["address"],16)<end+4)
assert not any(int(r["address"],16)==end for r in source_reads)
result={"execution":"PASS","engine":"Unicorn 2.x, ARM Thumb M-class","entry":"0x0043a11e","original_body_sha256":sha(decoder),"input_record":"0x0075d3e4","input_runtime_range":[hex(src),hex(end)],"input_bytes_hex":image[src-BASE:end-BASE].hex(),"destination_range":["0x00000040","0x00000058"],"output_hex":decoded.hex(),"output_sha256":sha(decoded),"return_r0":hex(ret),"executed_instruction_count":len(trace),"executed_original_instruction_trace":trace,"source_read_addresses":source_reads,"read_at_exclusive_end":False,"limits":["Only the original decoder body was executed with the authenticated record/source and synthetic stack; startup loader and physical hardware were not run.","Unicorn CPU semantics are not a physical Apollo timing measurement."]}
with (OUT/"emulation.json").open("x") as f:json.dump(result,f,indent=2,sort_keys=True);f.write("\n")
print("PASS original decoder emulation; decoded",len(decoded),"bytes to",decoded.hex(),"with",len(trace),"executed instruction steps")
