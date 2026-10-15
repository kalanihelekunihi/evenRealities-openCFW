#!/usr/bin/env python3
"""Differential check of NPMX watchdog callback and log contracts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3]
source=root/'components/main/npmx_watchdog_candidate_20261014/kick.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'kick.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def run(compiled,status,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  put(u,0x20070ffc,0x20005000);put(u,0x20005000,0x20006001);put(u,0x20005008,0x12345678)
  calls=[]
  def cstr(uc,addr):
   raw=bytes(uc.mem_read(addr,160));return raw.split(b'\0',1)[0]
  def callback(uc,at,size,user):
   r=tuple(uc.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   calls.append(('callback',r[0],r[1],bytes(uc.mem_read(r[2],r[3])),r[3]))
   uc.reg_write(UC_ARM_REG_R0,status);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,callback,begin=0x20006000,end=0x20006000)
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=uc.reg_read(UC_ARM_REG_SP)
   if name==callees[0][0]:result=flags
   elif name==callees[1][0]:
    extra=tuple(int.from_bytes(uc.mem_read(sp+4*i,4),'little') for i in range(4))
    calls.append(('detail',r[0],cstr(uc,r[1]),cstr(uc,r[2]),cstr(uc,r[3]),extra[0],cstr(uc,extra[1]),extra[2:]));result=0
   else:calls.append(('compact',r[0],cstr(uc,r[1]),cstr(uc,r[2]),r[3]));result=0
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,value in ((UC_ARM_REG_R0,0x11223344),(UC_ARM_REG_R1,0x55667788),(UC_ARM_REG_R2,0x99aabbcc),(UC_ARM_REG_R3,0xddeeff00)):u.reg_write(reg,value)
  u.emu_start((syms['audio_ble_npmx_kick_watchdog_5118e8'] if compiled else 0x5118e8)|1,0x600000,count=10000)
  return calls,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for status in (0,0x2bad0000,3,0xffffffff):
  for flags in (0,1,2,4,7):
   native=run(False,status,flags);source=run(True,status,flags)
   assert native==source,((status,flags),native,source)
   cases+=1
 print('PASS_NPMX_WATCHDOG_KICK_NATIVE',cases)
