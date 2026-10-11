"""Actual compiled-C/native LV area invalidation branch and callback trace."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint32_t active,visible,trace[8],calls;int32_t output[4];
void *audio_uart_lv_display_for_object(void *p){(void)p;trace[calls++]=1;return (void *)0x20082000;}
uint32_t audio_uart_lv_display_has_active_window(void *p){(void)p;trace[calls++]=2;return active;}
uint32_t audio_uart_lv_visible_area(void *p,const int32_t *a){(void)p;(void)a;trace[calls++]=3;return visible;}
void audio_uart_lv_render_invalidate(void *p,const int32_t *a){(void)p;trace[calls++]=4;for(unsigned i=0;i<4;i++)output[i]=a[i];}
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,...){(void)a;(void)b;(void)c;(void)d;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_invalidate_area',str(ROOT/'components/audio/uart_thread_source_candidate/display_lv_invalidate_area.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for active,visible,expand in [(0,1,0),(1,0,0),(1,1,0),(1,1,1)]:
  results=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);obj=0x20080000;par=0x20081000;area=0x20083000
   u.mem_write(obj,b'\0'*128);u.mem_write(par,b'\0'*128);u.mem_write(area,struct.pack('<4i',-9,4,18,30))
   if expand:
    u.mem_write(obj+8,struct.pack('<I',par));u.mem_write(par+0x32,struct.pack('<H',2<<10))
   trace=[];output=[0,0,0,0]
   if c:
    u.mem_write(syms['active'],struct.pack('<I',active));u.mem_write(syms['visible'],struct.pack('<I',visible))
   else:
    def cut(uc,a,size,_):
     if a not in (0x44dc0a,0x44fed2,0x4406c4,0x4534be):return
     code={0x44dc0a:1,0x44fed2:2,0x4406c4:3,0x4534be:4}[a];trace.append(code)
     if code==1:uc.reg_write(UC_ARM_REG_R0,0x20082000)
     elif code==2:uc.reg_write(UC_ARM_REG_R0,active)
     elif code==3:uc.reg_write(UC_ARM_REG_R0,visible)
     else:output[:]=struct.unpack('<4i',uc.mem_read(uc.reg_read(UC_ARM_REG_R1),16))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,cut)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,area)
   u.emu_start((syms['audio_uart_display_invalidate_area'] if c else 0x4405d4)|1,0x600000,count=3000)
   if c:
    count=struct.unpack('<I',u.mem_read(syms['calls'],4))[0]
    trace=list(struct.unpack('<'+str(count)+'I',u.mem_read(syms['trace'],4*count)))
    output=list(struct.unpack('<4i',u.mem_read(syms['output'],16)))
   results.append((trace,output))
  assert results[0]==results[1],(active,visible,expand,results)
  print('PASS LV area',active,visible,expand)
