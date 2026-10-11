"""Actual compiled-C/stock FT_Vector_NormLen arithmetic fixtures."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'v.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_normlen',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_normlen.c'),'-o',str(elf)],check=True)
 sym=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(c,x,y):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for v,d in segs:u.mem_write(v,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(0x20010000,struct.pack('<ii',x,y))
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20010000)
  u.emu_start((sym['audio_uart_font_vector_normlen'] if c else 0x524902)|1,0x600000,count=10000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20010000,8))
 rng=random.Random(0x524902)
 cases=[(0,0),(0,100),(100,0),(-100,0),(0,-100),(1,1),(-1,1),(65536,65536),(-65536,12345)]
 cases += [(rng.randint(-1000000,1000000),rng.randint(-1000000,1000000)) for _ in range(120)]
 for p in cases:
  a=run(False,*p);b=run(True,*p)
  assert a==b,(p,a,b)
 print('PASS normlen',len(cases))
