#!/usr/bin/env python3
"""Bounded differential check of Apollo MSPI queue preparation at 0x4bfcc0."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('g2_main_cq_reserve_538ece',0x538ece),('display_driver_uled_mspi_descriptor_4bfa3c',0x4bfa3c),('g2_main_cq_rollback_538f82',0x538f82)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d){{return 0;}}' for name,at in callees))
 image=Path(directory)/'queue.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_queue_prepare.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def get(u,a):return int.from_bytes(u.mem_read(a,4),'little')
 def run(compiled,case):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  h=0x20001000;t=0x20003000;u.mem_write(h,bytes(0x900));u.mem_write(t,bytes(32))
  put(u,h+32,case['busy']);put(u,h+0x828,0x20004000)
  calls=[]
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   if name==callees[0][0]:
    calls.append(('reserve',r[:2],get(uc,r[2]),get(uc,r[3])))
    if case['reserve']==0:put(uc,r[2],0x20005000);put(uc,r[3],case['slot'])
    result=case['reserve']
   elif name==callees[1][0]:calls.append(('descriptor',r));result=case['descriptor']
   else:calls.append(('rollback',r[0]));result=0
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,value in ((UC_ARM_REG_R0,h),(UC_ARM_REG_R1,t),(UC_ARM_REG_R2,case['priority']),(UC_ARM_REG_R3,0x12345)):u.reg_write(reg,value)
  put(u,0x200ff000,0x20006000)
  u.emu_start((syms['display_driver_uled_mspi_queue_prepare_4bfcc0'] if compiled else 0x4bfcc0)|1,0x600000,count=1000)
  return calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(h,0x900))
 cases=[dict(busy=busy,priority=priority,reserve=reserve,descriptor=descriptor,slot=slot) for busy in (0,0x100) for priority in (0,1,2,255,256) for reserve,descriptor in ((0,0),(5,0),(0,7)) for slot in (0,1,255)]
 for case in cases:
  native=run(False,case);source=run(True,case)
  assert native==source,(case,native[:2],source[:2])
 print('PASS_ULED_MSPI_QUEUE_PREPARE_NATIVE',len(cases))
