#!/usr/bin/env python3
"""Bounded stock/source public-entry oracle for 0x57d024 I2S request."""
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,
    UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC)
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
body=blob[0x57d024-0x437fe0:0x57d1a0-0x437fe0]
assert hashlib.sha256(body).hexdigest()=='6e5ef908f7cfd9be7d1c5b73121758a4bc2f9a9dc00bbd0497e084dc456e04ea'
compiler=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
elf_path=Path('/tmp/audio_i2s_request.elf')
providers={'audio_send_transaction':0x57c513,'audio_release_transaction':0x57c641,
           'audio_log_flags':0x43d0cf,'audio_log_extended':0x43d575,
           'audio_log_simple':0x43ce9f}
flags=(['-mcpu=cortex-m55','-mthumb','-O0','-ffreestanding','-fno-builtin',
        '-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,audio_i2s_output_request']+
       [f'-Wl,--defsym={name}={address:#x}' for name,address in providers.items()])
subprocess.run([str(compiler),*flags,str(HERE/'i2s_request.c'),'-o',str(elf_path)],check=True)
with elf_path.open('rb') as stream:
  elf=ELFFile(stream)
  source_entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_i2s_output_request')
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']

OUTPUT=0x20030000;PACKET=0x20040000
def run(source,enable,timeout,statuses,length,payload,log_bits,null_output):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
  u.mem_write(0x437fe0,blob)
  u.mem_map(0x10000000,0x100000)
  for a,data in segments:u.mem_write(a,data)
  u.mem_map(0x20000000,0x800000)
  u.mem_write(OUTPUT,b'\xef')
  u.mem_write(PACKET,payload.to_bytes(1,'little'))
  u.reg_write(UC_ARM_REG_SP,0x207ff000)
  u.reg_write(UC_ARM_REG_LR,0x10000001)
  for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),
                     (enable,0 if null_output else OUTPUT,timeout)):u.reg_write(reg,val)
  calls=[];sends=0
  def word(address):return struct.unpack('<I',u.mem_read(address,4))[0]
  def string(address):
    out=bytearray()
    for i in range(256):
      c=u.mem_read(address+i,1)[0]
      if not c:return out.decode('ascii')
      out.append(c)
    raise AssertionError(hex(address))
  def hook(emu,pc,size,data):
    nonlocal sends
    r=[emu.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    sp=emu.reg_read(UC_ARM_REG_SP)
    if pc==0x57c512:
      tx=word(sp+4);initial=bytes(emu.mem_read(tx,26))
      selected=emu.mem_read(r[2],1)[0]
      calls.append(['send',r[0],r[1],selected,r[3],word(sp),word(sp+8),initial.hex()])
      status=statuses[min(sends,len(statuses)-1)];sends+=1
      if not status:
        emu.mem_write(tx+14,struct.pack('<I',PACKET))
        emu.mem_write(tx+18,struct.pack('<H',length))
      emu.reg_write(UC_ARM_REG_R0,status&0xffffffff)
      emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
    elif pc==0x57c640:
      calls.append(['release',bytes(emu.mem_read(r[0],26)).hex()])
      emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
    elif pc==0x43d0ce:
      calls.append(['flags'])
      emu.reg_write(UC_ARM_REG_R0,log_bits)
      emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
    elif pc==0x43d574:
      line=word(sp);fmt=string(word(sp+4));args=[word(sp+8)]
      if r[0]==2:args.append(word(sp+12))
      calls.append(['extended',r[0],string(r[1]),string(r[2]),string(r[3]),line,fmt,args])
      emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
    elif pc==0x43ce9e:
      fmt=string(r[1]);assert fmt==string(r[2])
      args=[r[3],word(sp)] if r[0]==0x08800000 else [r[3]]
      calls.append(['simple',r[0],fmt,args])
      emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((source_entry if source else 0x57d024)|1,0x10000000,count=30000)
  assert u.reg_read(UC_ARM_REG_PC)==0x10000000
  return dict(result=u.reg_read(UC_ARM_REG_R0),output=u.mem_read(OUTPUT,1).hex(),calls=calls)

rows=[]
status_patterns=((0,),(1,0),(1,1,0),(1,2,3),(-1,-2,-3))
for enable,timeout,statuses,length,payload,log_bits in itertools.product(
    (0,1,0x100,0x1ff),(0,1,200),status_patterns,(0,1,2,3),
    (0,0x12,0xab),(0,1,2,4,7)):
  original=run(False,enable,timeout,statuses,length,payload,log_bits,False)
  compiled=run(True,enable,timeout,statuses,length,payload,log_bits,False)
  assert original==compiled,(enable,timeout,statuses,length,payload,log_bits,original,compiled)
  rows.append(dict(enable=hex(enable),timeout=timeout,statuses=statuses,length=length,
                   payload=hex(payload),log_bits=log_bits,result=hex(original['result']),
                   output=original['output'],calls=original['calls']))
for enable in (0,1,0x100,0x1ff):
  original=run(False,enable,200,(0,),2,0xab,7,True)
  compiled=run(True,enable,200,(0,),2,0xab,7,True)
  assert original==compiled,(enable,original,compiled)
  rows.append(dict(enable=hex(enable),null_output=True,result=hex(original['result']),calls=original['calls']))
receipt=dict(status='PASS',cases=len(rows),image_sha256=SHA,body_sha256=hashlib.sha256(body).hexdigest(),
             source_sha256=hashlib.sha256((HERE/'i2s_request.c').read_bytes()).hexdigest(),
             elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),compiler=str(compiler),
             compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),flags=flags,
             provider_bindings={k:hex(v) for k,v in providers.items()},rows=rows,
             limits='Send/release/log/flags intercepted at ABI with coherent synthetic transaction. No live IPC or scheduler timeout. Pointer lifetime, aliases and logger formatting not proven.')
(HERE/'i2s-request-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows))
