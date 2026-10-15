#!/usr/bin/env python3
"""Bounded differential check of Apollo MSPI transfer-async at 0x4c2208."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_mspi_queue_prepare_4bfcc0',0x4bfcc0),('display_driver_uled_irq_save_473940',0x473940),('g2_main_cq_commit_538fb4',0x538fb4),('g2_main_cq_rollback_538f82',0x538f82),('display_driver_uled_mspi_dma_start_4bfd44',0x4bfd44)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e){{return 0;}}' for name,at in callees))
 image=Path(directory)/'transfer.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_transfer_async.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def run(compiled,case):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  h=0x20001000;t=0x20002000
  u.mem_write(h,bytes(0x900));u.mem_write(t,bytes(32))
  put32(u,h,0x01bebebe if case['valid'] else 0x1234)
  put32(u,h+24,case['active']);u.mem_write(h+0x82c,bytes([case['state']]))
  u.mem_write(h+10,bytes([case['mode']]));u.mem_write(t+8,bytes([case['flags']]))
  put32(u,h+0x828,0x20003000);put32(u,h+0x838,0)
  put32(u,h+0x858,2);put32(u,h+0x85c,case['count'])
  put32(u,h+32,case['prior']);put32(u,h+0x830,9)
  calls=[]
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=uc.reg_read(UC_ARM_REG_SP)
   if name==callees[0][0]:calls.append(('prepare',regs, int.from_bytes(uc.mem_read(sp,4),'little')));result=case['prepare']
   elif name==callees[1][0]:calls.append(('irq',));result=0
   elif name==callees[2][0]:calls.append(('commit',regs[:2]));result=case['commit']
   elif name==callees[3][0]:calls.append(('rollback',regs[0]));result=0
   else:calls.append(('start',regs[0]));result=case['start']
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,value in ((UC_ARM_REG_R0,h),(UC_ARM_REG_R1,t),(UC_ARM_REG_R2,0x101),(UC_ARM_REG_R3,case['callback'])):u.reg_write(reg,value)
  put32(u,0x200ff000,0x20004000)
  u.emu_start((syms['display_driver_uled_transfer_async_4c2208'] if compiled else 0x4c2208)|1,0x600000,count=1000)
  memory=bytes(u.mem_read(h,0x900))
  return calls,u.reg_read(UC_ARM_REG_R0),memory
 cases=[]
 for valid,active,state,mode,flags in [(False,1,0,0,0),(True,0,0,0,0),(True,1,2,0,0),(True,1,0,10,1),(True,1,0,11,2),(True,1,0,10,0),(True,1,0,0,0)]:
  for callback in (0,0x12345):
   for count in (0,1):
    for prepare,commit,start,prior in [(0,0,0,0),(5,0,0,0),(0,6,0,0),(0,0,7,0),(0,0,0,2)]:
     cases.append(dict(valid=valid,active=active,state=state,mode=mode,flags=flags,callback=callback,count=count,prepare=prepare,commit=commit,start=start,prior=prior))
 for case in cases:
  native=run(False,case);source=run(True,case)
  assert native==source,(case,native[:2],source[:2])
 print('PASS_ULED_TRANSFER_ASYNC_NATIVE',len(cases))
