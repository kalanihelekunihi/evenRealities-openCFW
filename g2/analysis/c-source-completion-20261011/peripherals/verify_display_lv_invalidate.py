"""Actual compiled-C/native LV object invalidation rect composition."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
int32_t observed[4]; uint32_t calls;
void audio_uart_display_invalidate_area(void *p,const int32_t *a){(void)p;calls++;for(unsigned i=0;i<4;i++)observed[i]=a[i];}
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,...){(void)a;(void)b;(void)c;(void)d;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_size_changed',str(ROOT/'components/audio/uart_thread_source_candidate/display_lv_invalidate.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for parent in [None,-3,0,7]:
  for rect in [(0,0,0,0),(-9,4,18,30)]:
   outputs=[]
   for c in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.mem_map(0x20000000,0x100000);obj=0x20080000;par=0x20081000
    u.mem_write(obj,b'\0'*128);u.mem_write(par,b'\0'*128)
    if parent is not None:
     u.mem_write(obj+8,struct.pack('<I',par));u.mem_write(par+0x2c,struct.pack('<i',parent))
    u.mem_write(obj+20,struct.pack('<4i',*rect));seen=[]
    if not c:
     def cut(uc,a,size,_):
      if a==0x4405d4:
       p=uc.reg_read(UC_ARM_REG_R1);seen.append(struct.unpack('<4i',uc.mem_read(p,16)))
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,cut)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
    u.emu_start((syms['audio_uart_display_size_changed'] if c else 0x440656)|1,0x600000,count=3000)
    if c:
     count=struct.unpack('<I',u.mem_read(syms['calls'],4))[0]
     assert count==1;seen=[struct.unpack('<4i',u.mem_read(syms['observed'],16))]
    outputs.append(seen)
   assert outputs[0]==outputs[1],(parent,rect,outputs)
   print('PASS LV invalidate',parent,rect)
