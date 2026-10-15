#!/usr/bin/env python3
"""Compare valid Ambiq glyph bitmap calls and matrix payload with native."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
root=Path(__file__).resolve().parents[3]
source=root/'components/main/ambiq_buffer_handlers_candidate_20261014/label_glyph_blit.c'
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_lvgl_log',0x44d25c),('display_driver_gpu_enable_4b0748',0x4b0748),
 ('audio_uart_ambiq_image_alpha_513e2e',0x513e2e),('audio_uart_ambiq_texture_color_4b146c',0x4b146c),
 ('audio_uart_nema_matrix_identity_561810',0x561810),('display_driver_gpu_blit_4b1608',0x4b1608),
 ('audio_uart_nema_matrix_translate_561856',0x561856),('audio_uart_nema_matrix_upload_5226e8',0x5226e8),
 ('display_driver_nema_clear_522ae0',0x522ae0)]
F=lambda x:struct.pack('<f',x)
def rd(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def cstr(u,p):return bytes(u.mem_read(p,160)).split(b'\0')[0]
with tempfile.TemporaryDirectory() as temp:
 d=Path(temp);asm=d/'stubs.s'
 asm.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n,_ in callees))
 image=d/'glyph.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(source),str(asm),'-o',str(image)],check=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,depth,color,row_mode,compact,width,height,clip):
  cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
  cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
  for address,data in segments:cpu.mem_write(address,data)
  cp=0x20012000;bitmap=0x20013000;unit=0x20014000
  cpu.mem_write(cp,b''.join((v&0xffffffff).to_bytes(4,'little') for v in clip))
  cpu.reg_write(UC_ARM_REG_R0,unit);cpu.reg_write(UC_ARM_REG_R1,bitmap)
  cpu.reg_write(UC_ARM_REG_R2,width);cpu.reg_write(UC_ARM_REG_R3,height)
  sp=0x200ff000;cpu.reg_write(UC_ARM_REG_SP,sp);cpu.reg_write(UC_ARM_REG_LR,0x600001)
  cpu.mem_write(sp,b''.join(v.to_bytes(4,'little') for v in (cp,depth,color,row_mode,compact)))
  targets={((syms[n] if compiled else a)&~1):n for n,a in callees};events=[]
  def hook(u,address,_size,_user):
   n=targets.get(address)
   if n is None:return
   r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
   r2=u.reg_read(UC_ARM_REG_R2);r3=u.reg_read(UC_ARM_REG_R3)
   stack=u.reg_read(UC_ARM_REG_SP)
   if n=='audio_uart_lvgl_log':
    events.append((n,r0,cstr(u,r1),r2,cstr(u,r3),cstr(u,rd(u,stack))))
   elif n=='display_driver_gpu_enable_4b0748':events.append((n,r0,r1))
   elif n in ('audio_uart_ambiq_image_alpha_513e2e','audio_uart_ambiq_texture_color_4b146c'):
    events.append((n,r0))
   elif n=='audio_uart_nema_matrix_identity_561810':
    events.append((n,))
    u.mem_write(r0,b''.join(F(1.0 if i in (0,4,8) else 0.0) for i in range(9)))
   elif n=='display_driver_gpu_blit_4b1608':
    events.append((n,r0,r1,r2,r3,rd(u,stack),rd(u,stack+4)))
   elif n=='audio_uart_nema_matrix_translate_561856':
    events.append((n,u.reg_read(UC_ARM_REG_S0),u.reg_read(UC_ARM_REG_S1)))
   elif n=='audio_uart_nema_matrix_upload_5226e8':
    events.append((n,bytes(u.mem_read(r0,36)).hex()))
   elif n=='display_driver_nema_clear_522ae0':events.append((n,r0,r1,r2,r3))
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  cpu.hook_add(UC_HOOK_CODE,hook)
  try:cpu.emu_start((syms['audio_uart_ambiq_label_glyph_blit_53fb18'] if compiled else 0x53fb18)|1,0x600000,count=900)
  except Exception as error:raise RuntimeError((compiled,depth,color,row_mode,compact,width,height,hex(cpu.reg_read(UC_ARM_REG_PC)),events)) from error
  return events
 count=0
 for depth in (0,1,2,4,8,17,18,20,24,255):
  for color in (0xff123456,0x80123456):
   for row_mode,compact in ((1,0),(1,1)):
    for width,height in ((4,3),(5,2)):
     clip=(-2,3,7,9)
     native=run(False,depth,color,row_mode,compact,width,height,clip)
     compiled=run(True,depth,color,row_mode,compact,width,height,clip)
     assert native==compiled,(depth,hex(color),row_mode,compact,width,height,native,compiled)
     count+=1
 static_count=0
 for color in (0xff123456,0x80123456):
  for width,height in ((4,3),(5,2),(16,9),(31,11)):
   for clip in ((-2,3,7,9),(0,0,15,8),(2,-3,20,12)):
    events=run(True,8,color,0,0,width,height,clip)
    blits=[e for e in events if e[0]=='display_driver_gpu_blit_4b1608']
    assert len(blits)==1 and blits[0][2:]==(width*height,1,8,0,0),(color,width,height,clip,blits)
    packets=[e for e in events if e[0]=='audio_uart_nema_matrix_upload_5226e8']
    assert len(packets)==1
    words=bytes.fromhex(packets[0][1])
    offset=(0-clip[0]-width*clip[1])&0xffffffff
    if offset>=0x80000000:offset-=0x100000000
    assert words[4:8]==F(float(width))
    assert words[8:12]==F(float(offset)-float(width)*0.5)
    static_count+=1
 print('PASS_AMBIQ_LABEL_GLYPH_BLIT_NATIVE',count)
 print('PASS_AMBIQ_LABEL_GLYPH_BLIT_ROW_MODE_ZERO_INSTRUCTION_PROJECTION',static_count)
