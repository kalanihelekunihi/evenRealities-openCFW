"""Connected actual compiled-C/stock FT_Outline_EmboldenXY rectangle fixtures."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=ROOT/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'e.elf';files=['display_font_freetype_embolden_xy.c','display_font_freetype_normlen.c','display_font_freetype_orientation.c','display_font_freetype_cbox.c','display_font_math.c','display_font_metric_scale.c']
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_embolden_xy',*(str(S/f) for f in files),str(ROOT/'components/audio/uart_power_config_offline/division_support.c'),'-o',str(elf)],check=True)
 sym=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,points,xs,ys):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for v,d in segs:u.mem_write(v,d)
  u.mem_map(0x20000000,0x100000)
  outline=0x20010000;vertices=0x20011000;contours=0x20012000
  u.mem_write(outline,struct.pack('<hhIII',1,len(points),vertices,0,contours))
  u.mem_write(vertices,b''.join(struct.pack('<ii',*p) for p in points));u.mem_write(contours,struct.pack('<h',len(points)-1))
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.reg_write(UC_ARM_REG_R0,outline);u.reg_write(UC_ARM_REG_R1,xs);u.reg_write(UC_ARM_REG_R2,ys)
  u.emu_start((sym['audio_uart_font_embolden_xy'] if candidate else 0x527bd6)|1,0x600000,count=100000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(vertices,8*len(points)))
 boxes=[[(0,0),(640,0),(640,640),(0,640)],[(0,0),(0,640),(640,640),(640,0)],[(0,0),(320,0),(320,160),(0,160)]]
 cases=[(b,x,y) for b in boxes for x,y in [(0,0),(64,64),(100,50),(-40,80)]]
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  assert a==b,(case,a,b)
 print('PASS embolden',len(cases))
