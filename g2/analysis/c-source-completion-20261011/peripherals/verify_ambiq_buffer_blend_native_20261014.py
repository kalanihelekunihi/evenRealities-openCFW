#!/usr/bin/env python3
"""Compare Ambiq buffer blend call and area contracts against Apollo S200."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3];source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/blend.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_lv_memzero_48949c',0x48949c),('audio_uart_checksum_copy',0x439c04),('audio_uart_lv_area_intersect_450bcc',0x450bcc),('audio_uart_ambiq_bind_buffer_4b092a',0x4b092a),('display_driver_gpu_mode_lower_4b06c0',0x4b06c0),('display_driver_nema_select_522a16',0x522a16),('audio_uart_lv_area_width_451598',0x451598),('audio_uart_lv_area_height_4515a4',0x4515a4),('display_driver_nema_clear_522ae0',0x522ae0),('audio_uart_nema_bind_tex_4b1298',0x4b1298),('audio_uart_ambiq_clip_change_4b077e',0x4b077e),('audio_uart_ambiq_submit_4b0c8a',0x4b0c8a)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'blend.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,format,clip,intersect,bind):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  buf=0x20005000;area=0x20006000;u.mem_write(buf,bytes(40));u.mem_write(area,bytes(16))
  for off,val in ((0,format<<8),(4,0x00100020),(8,0x20),(16,0x20008000)):
   u.mem_write(buf+off,val.to_bytes(4,'little'))
  calls=[]
  def words(uc,at):return tuple(int.from_bytes(uc.mem_read(at+4*i,4),'little') for i in range(4))
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=uc.reg_read(UC_ARM_REG_SP);extra=tuple(int.from_bytes(uc.mem_read(sp+4*i,4),'little') for i in range(3))
   if name==callees[0][0]:calls.append(('zero',r[1]));uc.mem_write(r[0],bytes(r[1]));value=0
   elif name==callees[1][0]:calls.append(('copy',r[2],words(uc,r[1])));uc.mem_write(r[0],bytes(uc.mem_read(r[1],r[2])));value=r[0]
   elif name==callees[2][0]:calls.append(('intersect',r[1]==area,words(uc,r[2])));uc.mem_write(r[0],b'\x01\0\0\0\x02\0\0\0\x06\0\0\0\x08\0\0\0');value=intersect
   elif name==callees[3][0]:calls.append(('bind',r[0]==buf,r[1]==area,r[2]));value=bind
   elif name==callees[4][0]:calls.append(('mode',r,extra[:2]));value=0
   elif name==callees[5][0]:calls.append(('select',r[0]));value=0
   elif name==callees[6][0]:calls.append(('width',words(uc,r[0])));value=words(uc,r[0])[2]-words(uc,r[0])[0]+1
   elif name==callees[7][0]:calls.append(('height',words(uc,r[0])));value=words(uc,r[0])[3]-words(uc,r[0])[1]+1
   elif name==callees[8][0]:calls.append(('clear',r));value=0
   elif name==callees[9][0]:calls.append(('texture',r,extra));value=0
   elif name==callees[10][0]:calls.append(('clip',r[0],words(uc,r[1]),r[2]));value=0
   else:calls.append(('submit',r[0]));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.reg_write(UC_ARM_REG_R0,buf);u.reg_write(UC_ARM_REG_R1,area if clip else 0)
  u.emu_start((syms['audio_uart_ambiq_buffer_blend_53d0b6'] if compiled else 0x53d0b6)|1,0x600000,count=1000)
  return calls
 cases=0
 for format in (0,7,8,9,10,11,20):
  for clip in (False,True):
   for intersect in (0,1):
    for bind in (0,1,2):
     native=run(False,format,clip,intersect,bind);source=run(True,format,clip,intersect,bind)
     assert native==source,(format,clip,intersect,bind,native,source)
     cases+=1
 print('PASS_AMBIQ_BUFFER_BLEND_NATIVE',cases)
