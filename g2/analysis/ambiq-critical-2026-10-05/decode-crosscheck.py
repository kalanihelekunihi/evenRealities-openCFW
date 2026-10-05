#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute authenticated scatter decoder; bounds-check every packed input read."""
import hashlib,json,struct,argparse
from pathlib import Path
if not __debug__:raise RuntimeError('optimized Python rejected')
ROOT=Path(__file__).resolve().parents[2]
def main():
 import unicorn as u
 from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC,UC_ARM_REG_R6,UC_ARM_REG_R1,UC_CPU_ARM_CORTEX_M4
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 blob=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';image=blob[32:];base=0x438000
 body=image[0x43a11e-base:0x43a19c-base];assert sha(body)=='41e4a34428bb2c09774785d474f5209201f6551c823f0286eb66063dedc74a9d'
 cpu=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);cpu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for address,size in [(0,4096),(0x43a000,4096),(0x75d000,4096),(0x794000,4096),(0x2000e000,8192),(0x8000000,4096)]:cpu.mem_map(address,size)
 cpu.mem_write(0x43a11e,body);cpu.mem_write(0x75d3e4,image[0x75d3e4-base:0x75d3f0-base]);packed=image[0x79430e-base:0x794324-base];cpu.mem_write(0x79430e,packed);cpu.mem_write(0x30,b'\xcc'*64)
 reads=[];writes=[];pcs={};produced=0
 def memory(uc,kind,address,size,value,_):
  nonlocal produced
  if 0x794000<=address<0x795000:
   assert kind==u.UC_MEM_READ and size==1 and 0x79430e<=address<0x794324,('packed-bound',hex(address),size)
   reads.append(address)
  if 0<=address<4096:
   if kind==u.UC_MEM_WRITE:
    assert size==1 and address==0x40+produced;produced+=1;writes.append([address,value])
   else:assert size==1 and 0x40<=address<0x40+produced,('backref-bound',hex(address),produced)
 def code(uc,address,size,_):
  assert 0x43a11e<=address<address+size<=0x43a19c
  raw=bytes(uc.mem_read(address,size));assert raw==body[address-0x43a11e:address-0x43a11e+size];pcs[address]=raw.hex()
 def invalid(uc,access,address,size,value,_):
  raise AssertionError(('unmapped',hex(address),size,'pc',hex(uc.reg_read(UC_ARM_REG_PC)),'produced',produced))
 cpu.hook_add(u.UC_HOOK_MEM_INVALID,invalid)
 cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,memory);cpu.hook_add(u.UC_HOOK_CODE,code)
 cpu.reg_write(UC_ARM_REG_R0,0x75d3e4);cpu.reg_write(UC_ARM_REG_LR,0x8000001);cpu.reg_write(UC_ARM_REG_SP,0x2000f000);
 try:cpu.emu_start(0x43a11f,0x8000000,count=10000)
 except Exception as error:
  result=dict(status='INCONCLUSIVE',firmware_sha256=sha(blob),decoder_sha256=sha(body),script_sha256=sha(Path(__file__).read_bytes()),error=str(error),observed_output_bytes=produced,packed_reads_before_fault=reads,trace=pcs,limits='Original-instruction decoder run failed under installed Unicorn; no decoded output or initialization is dynamically proven. Separate original/results.json provides static mirror evidence only.')
  a.output.parent.mkdir(parents=True,exist_ok=True)
  with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
  print('INCONCLUSIVE decoder execution; no passing dynamic proof');raise SystemExit(1)
 assert cpu.reg_read(UC_ARM_REG_PC)==0x8000000 and cpu.reg_read(UC_ARM_REG_R0)==0x75d3f0
 expected=bytes.fromhex('0138fdd17047704750f8043b41f8043b013af9d170477047');assert produced==len(expected)==24 and bytes(cpu.mem_read(0x40,24))==expected
 assert reads==list(range(0x79430e,0x794324));assert bytes(cpu.mem_read(0x30,16))==b'\xcc'*16
 assert bytes(cpu.mem_read(0x58,24))==b'\xcc'*24
 result=dict(status='PASS',firmware_sha256=sha(blob),decoder_sha256=sha(body),script_sha256=sha(Path(__file__).read_bytes()),packed_bytes=22,packed_reads=reads,decoded_bytes=24,decoded_hex=expected.hex(),writes=writes,executed_instruction_bytes=sum(len(bytes.fromhex(v)) for v in pcs.values()),trace=pcs,limits='Executes one stored scatter decoder with its authentic record/input; all input and backreference reads checked in bounds, guard bytes preserved. Does not execute whole startup, prove clocks/ITCM setup, or measure elapsed delay.')
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print('PASS decoder:22 in-bounds input bytes ->24 bytes ITCM; delayloop complete')
if __name__=='__main__':main()
