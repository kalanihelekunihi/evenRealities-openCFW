#!/usr/bin/env python3
"""Compare mask rectangle packet and r0 return against native 0x522ae0."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
source=Path(__file__).resolve().parents[3]/'components/main/ambiq_buffer_handlers_candidate_20261014/nema_mask_rectangle.c'
blob=(Path(__file__).resolve().parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in
  ('audio_uart_nema_child_514846','audio_uart_nema_cl_get_space_514aec'))+
  '.bss\n.global audio_uart_nema_context_cell\naudio_uart_nema_context_cell: .space 4\n')
 image=d/'select_clear.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[('audio_uart_nema_mask_rectangle_522ae0',0x522ae0,args,ret)
           for args in ((0,0,0,1),(0,0,1,0),(0x12345678,0,0xffffffff,1),
                        (0,0,1,0x80000000),(0,0,1,1),(3,5,7,9),
                        (0xffffffff,0xfffffffe,2,3),(0x12345,0x23456,0x34567,0x45678))
           for ret in (0,1)]
 for i in range(64):
  x=(i*0x9e3779b9)&0xffffffff
  y=(i*0x7f4a7c15)&0xffffffff
  width=(0,1,2,0x7fff,0x80000000,0xffffffff,0x10000,0x7fffffff)[i%8]
  height=(0,1,3,0x80000000,0xffffffff,0x10000,0x7fffffff,0x8001)[(i//8)%8]
  for ret in (0,1):cases.append(('audio_uart_nema_mask_rectangle_522ae0',0x522ae0,(x,y,width,height),ret))
 count=0
 for name,native,args,allocate in cases:
  observations=[]
  for compiled in (False,True):
   cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
   cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
   for address,data in segments:cpu.mem_write(address,data)
   cell=syms['audio_uart_nema_context_cell'] if compiled else 0x20074efc
   cpu.mem_write(cell,(0x20088000).to_bytes(4,'little'))
   cpu.mem_write(0x20088018,(0x4a20).to_bytes(4,'little'))
   cpu.mem_write(0x20090000,bytes([0xcc])*24)
   cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):
    cpu.reg_write(reg,v)
   child=(syms['audio_uart_nema_child_514846'] if compiled else 0x514846)&~1
   alloc=(syms['audio_uart_nema_cl_get_space_514aec'] if compiled else 0x514aec)&~1
   events=[]
   def hook(u,address,_size,_user):
    if address==child:events.append(('child',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
    elif address==alloc:
     events.append(('alloc',u.reg_read(UC_ARM_REG_R0)))
     u.reg_write(UC_ARM_REG_R0,0x20090000 if allocate else 0)
    else:return
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   cpu.hook_add(UC_HOOK_CODE,hook)
   cpu.emu_start((syms[name] if compiled else native)|1,0x600000,count=100)
   observations.append((events,bytes(cpu.mem_read(0x20090000,24)).hex(),cpu.reg_read(UC_ARM_REG_R0)))
  assert observations[0]==observations[1],(name,args,allocate,observations)
  count+=1
print('PASS_NEMA_MASK_RECTANGLE_NATIVE_RETURN',count)
