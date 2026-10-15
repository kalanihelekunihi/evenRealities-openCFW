#!/usr/bin/env python3
"""Compare Ambiq buffer destroy/flush/invalidate paths and assertion logs."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3];source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/coherency.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('audio_uart_ambiq_buffer_update_53cf8a',0x53cf8a),('audio_uart_ambiq_buffer_mask_53d006',0x53d006),('audio_uart_ambiq_buffer_layout_53d062',0x53d062)]
callees=[('audio_uart_lv_memzero_48949c',0x48949c),('audio_uart_nema_pool_contains_514148',0x514148),('audio_uart_nema_cl_buffer_destroy_5140c6',0x5140c6),('audio_uart_nema_buffer_flush_5140ea',0x5140ea),('audio_uart_nema_buffer_invalidate_51411a',0x51411a),('audio_uart_lvgl_log',0x44d25c)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'coherency.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,entry,pool,data,flag,contains):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,bytes_ in segments:u.mem_write(base,bytes_)
  draw=0x20005000;u.mem_write(draw,bytes(32))
  for offset,value in ((0,flag),(12,0x20007000),(16,0x20008000)):
   u.mem_write(draw+offset,value.to_bytes(4,'little'))
  calls=[]
  def cstr(uc,a):return bytes(uc.mem_read(a,180)).split(b'\0',1)[0]
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=uc.reg_read(UC_ARM_REG_SP)
   if name==callees[0][0]:uc.mem_write(r[0],bytes(r[1]));calls.append(('zero',r[1]));result=0
   elif name==callees[1][0]:calls.append(('contains',r[:2]));result=contains
   elif name in (callees[2][0],callees[3][0],callees[4][0]):calls.append((name,tuple(int.from_bytes(uc.mem_read(r[0]+4*i,4),'little') for i in range(4))));result=0
   else:
    extra=tuple(int.from_bytes(uc.mem_read(sp+4*i,4),'little') for i in range(3))
    calls.append(('log',r[0],cstr(uc,r[1]),r[2],cstr(uc,r[3]),*(cstr(uc,v) for v in extra)))
    result=0
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,value in ((UC_ARM_REG_R0,pool),(UC_ARM_REG_R1,data if entry==0 else draw),(UC_ARM_REG_R2,0xabcdef)):u.reg_write(reg,value)
  target=(syms[entries[entry][0]] if compiled else entries[entry][1])|1
  try:u.emu_start(target,0x600000,count=1000);terminal='returned'
  except UcError:terminal='fault'
  return calls,terminal
 cases=0
 for entry in range(3):
  for pool,data in ((0,0),(1,0x20008000),(3,0xffffffff)):
   for flag in (0,0x00100000,0xffffffff):
    for contains in (0,1):
     native=run(False,entry,pool,data,flag,contains);source=run(True,entry,pool,data,flag,contains)
     assert native==source,(entry,pool,data,flag,contains,native,source)
     cases+=1
 print('PASS_AMBIQ_BUFFER_COHERENCY_NATIVE',cases)
