"""Compiled-C/stock glyph callback, controlled LV cache operations."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];S=ROOT/'components/audio/uart_thread_source_candidate'
FONT=0x20010000;GLYPH=0x20011000;DSC=0x20012000;CTX=0x20012500;CACHE=0x20012600;ENTRY=0x20013000;DATA=0x20014000
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'cache.c';shim.write_text(''.join('__attribute__((naked,used)) void *'+n+'(void){__asm__ volatile("bx lr");}\n' for n in ['audio_uart_font_cache_add','audio_uart_font_cache_info','audio_uart_font_cache_remove','audio_uart_lvgl_log']))
 elf=Path(td)/'g.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_cb_glyph',*(str(S/f) for f in ['display_font_callback_glyph_lookup.c','ring_init.c','byte_copy.c']),str(shim),'-o',str(elf)],check=True)
 syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,unicode,style,flag,miss):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for v,d in segs:u.mem_write(v,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(GLYPH,b'Z'*40)
  u.mem_write(FONT+24,struct.pack('<I',DSC));u.mem_write(DSC,struct.pack('<I',0x5f5f4654));u.mem_write(DSC+0x28,struct.pack('<I',24));u.mem_write(DSC+0x34,struct.pack('<I',CTX));u.mem_write(DSC+0x2c,bytes([style]));u.mem_write(CTX+24,struct.pack('<I',CACHE))
  data=bytearray(range(40));data[8+6:8+8]=struct.pack('<H',20);data[8+10:8+12]=struct.pack('<h',-3)
  u.mem_write(DATA,bytes(data))
  opaddr={((syms['audio_uart_font_cache_add']&~1) if candidate else 0x4d4f90):'add',((syms['audio_uart_font_cache_info']&~1) if candidate else 0x4d5396):'info',((syms['audio_uart_font_cache_remove']&~1) if candidate else 0x4d4e72):'remove'}
  trace=[]
  def hook(u,pc,size,_):
   op=opaddr.get(pc)
   if op is None:return
   r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1);r2=u.reg_read(UC_ARM_REG_R2)
   if op=='add':trace.append((op,r0,r2,bytes(u.mem_read(r1,40))));rv=0 if miss else ENTRY
   else:trace.append((op,r0) if op=='info' else (op,r0,r1,r2));rv=DATA if op=='info' else 0
   u.reg_write(UC_ARM_REG_R0,rv);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  for reg,val in ((UC_ARM_REG_R0,FONT),(UC_ARM_REG_R1,GLYPH),(UC_ARM_REG_R2,unicode),(UC_ARM_REG_R3,flag)):u.reg_write(reg,val)
  u.emu_start((syms['audio_uart_font_cb_glyph'] if candidate else 0x529460)|1,0x600000,count=100000)
  return u.reg_read(UC_ARM_REG_R0),trace,bytes(u.mem_read(GLYPH,40))
 cases=[(1,0,0,False),(31,0,0,False),(65,0,0,False),(65,1,0,False),(65,1,1,False)]
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  assert a==b,(case,a,b)
  print('PASS glyph callback',case)
