#!/usr/bin/env python3
"""Compare Ambiq buffer render branch calls with Apollo S200 0x53d25a."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
root=Path(__file__).resolve().parents[3];source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/render.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_lv_area_width_451598',0x451598),('audio_uart_lv_area_height_4515a4',0x4515a4),('audio_uart_ambiq_bind_buffer_4b092a',0x4b092a),('audio_uart_ambiq_color_format_src_4b05a4',0x4b05a4),('audio_uart_nema_bind_tex_4b1298',0x4b1298),('display_driver_gpu_mode_lower_4b06c0',0x4b06c0),('audio_uart_ambiq_buffer_draw_4b1b0e',0x4b1b0e),('audio_uart_lv_memzero_48949c',0x48949c),('audio_uart_ambiq_clip_change_4b077e',0x4b077e),('display_driver_gpu_position_4b1b48',0x4b1b48),('audio_uart_ambiq_submit_4b0c8a',0x4b0c8a),('audio_uart_lvgl_log',0x44d25c)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'render.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,df,sf,dc,sc,same,bind):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  dest=0x20005000;src=0x20006000;dclip=0x20007000;sclip=0x20008000
  for addr in (dest,src):u.mem_write(addr,bytes(32))
  for addr,fmt in ((dest,df),(src,sf)):
   for off,val in ((0,fmt<<8),(4,0x00100020),(8,0x20),(16,0x20009000 if addr==dest else 0x2000a000)):
    u.mem_write(addr+off,val.to_bytes(4,'little'))
  for addr in (dclip,sclip):
   for i,val in enumerate((1,2,8 if same else (8 if addr==dclip else 9),7)):
    u.mem_write(addr+4*i,val.to_bytes(4,'little'))
  calls=[]
  def word(uc,a):return int.from_bytes(uc.mem_read(a,4),'little')
  def area(uc,a):return tuple(word(uc,a+4*i) for i in range(4))
  def cstr(uc,a):return bytes(uc.mem_read(a,180)).split(b'\0',1)[0]
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=uc.reg_read(UC_ARM_REG_SP);extra=tuple(word(uc,sp+4*i) for i in range(4))
   if name==callees[0][0]:calls.append(('width',area(uc,r[0])));value=area(uc,r[0])[2]-area(uc,r[0])[0]+1
   elif name==callees[1][0]:calls.append(('height',area(uc,r[0])));value=area(uc,r[0])[3]-area(uc,r[0])[1]+1
   elif name==callees[2][0]:calls.append(('bind',r[0]==dest, r[1]==dclip, r[2]));value=bind
   elif name==callees[3][0]:calls.append(('format',r[0]));value=8
   elif name==callees[4][0]:calls.append(('texture',r,extra[:3]));value=0
   elif name==callees[5][0]:calls.append(('mode',r,extra[:2]));value=0
   elif name==callees[6][0]:calls.append(('draw',r,extra[:2]));value=0
   elif name==callees[7][0]:calls.append(('zero',r[1]));uc.mem_write(r[0],bytes(r[1]));value=0
   elif name==callees[8][0]:calls.append(('clip',r[0],area(uc,r[1]),r[2]));value=0
   elif name==callees[9][0]:calls.append(('position',r[:2]));value=0
   elif name==callees[10][0]:calls.append(('submit',r[0]));value=0
   else:calls.append(('log',r[0],cstr(uc,r[1]),r[2],cstr(uc,r[3]),cstr(uc,extra[0]),cstr(uc,extra[1]),extra[2:] if r[2]==0xb5 else None));value=0
   uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,val in ((UC_ARM_REG_R0,dest),(UC_ARM_REG_R1,dclip if dc else 0),(UC_ARM_REG_R2,src),(UC_ARM_REG_R3,sclip if sc else 0)):u.reg_write(reg,val)
  try:u.emu_start((syms['audio_uart_ambiq_buffer_render_53d25a'] if compiled else 0x53d25a)|1,0x600000,count=2000);terminal='return'
  except UcError:terminal='fault'
  return calls,terminal
 cases=0
 for df,sf in ((7,7),(8,8),(9,9),(10,10),(20,20),(0,0),(7,8)):
  for dc,sc in ((False,False),(True,True),(True,False),(False,True)):
   for same in (False,True):
    for bind in (0,1,2):
     native=run(False,df,sf,dc,sc,same,bind);source=run(True,df,sf,dc,sc,same,bind)
     assert native==source,(df,sf,dc,sc,same,bind,native,source)
     cases+=1
 print('PASS_AMBIQ_BUFFER_RENDER_NATIVE',cases)
