#!/usr/bin/env python3
"""Differential check of Apollo Ambiq clip and scissor C bodies."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_clip_change_candidate_20261014/clip.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_ambiq_default_unit_4c791a',0x4c791a),('audio_uart_nema_child_514846',0x514846),('audio_uart_checksum_copy',0x439c04)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('unsigned audio_uart_nema_context_cell[1];\n'+'\n'.join(f'unsigned {name}(unsigned a,unsigned b,unsigned c,unsigned d){{return 0;}}' for name,at in callees))
 image=Path(directory)/'clip.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def put(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
 def run(compiled,case):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  unit=0x20001000;clip=0x20002000;state=0x20003000
  u.mem_write(unit,bytes(0x100));u.mem_write(clip,bytes(16));u.mem_write(state,bytes(0x100))
  put(u,syms['audio_uart_nema_context_cell'] if compiled else 0x20074efc,state)
  for i,v in enumerate(case['old']):put(u,unit+0x74+i*4,v)
  for i,v in enumerate(case['new']):put(u,clip+i*4,v)
  calls=[]
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   if name==callees[0][0]:calls.append(('default',));result=unit
   elif name==callees[1][0]:calls.append(('register',r[:2]));result=0
   else:
    calls.append(('copy',r[2],bytes(uc.mem_read(r[1],r[2]))));uc.mem_write(r[0],bytes(uc.mem_read(r[1],r[2])));result=r[0]
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,val in ((UC_ARM_REG_R0,0 if case['default'] else unit),(UC_ARM_REG_R1,clip),(UC_ARM_REG_R2,case['force'])):u.reg_write(reg,val)
  u.emu_start((syms['audio_uart_ambiq_clip_change_4b077e'] if compiled else 0x4b077e)|1,0x600000,count=1000)
  return calls,bytes(u.mem_read(unit+0x74,16)),bytes(u.mem_read(state,0x34))
 cases=[]
 for old in ((0,0,0,0),(1,2,10,20),(-4,-2,10,20)):
  for new in ((0,0,0,0),(1,2,10,20),(-4,-2,10,20),(-8,-6,-1,-1)):
   for force in (0,1,255):
    for default in (False,True):cases.append(dict(old=old,new=new,force=force,default=default))
 for case in cases:
  native=run(False,case);compiled=run(True,case)
  assert native==compiled,(case,native,compiled)
 print('PASS_AMBIQ_CLIP_CHANGE_NATIVE',len(cases))
