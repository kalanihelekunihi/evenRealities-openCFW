"""Actual compiled-C/native LV object screen/display registry branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_uart_display_lv_root[64];uint32_t log_calls;
void *audio_uart_lv_list_first(void *p){return (void *)(uintptr_t)*(uint32_t *)((uint8_t *)p+4);}
void *audio_uart_lv_list_next(void *p,void *n){return (void *)(uintptr_t)*(uint32_t *)(uintptr_t)(*(uint32_t *)p+(uintptr_t)n+4);}
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,...){(void)a;(void)b;(void)c;(void)d;log_calls++;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_display_for_object',str(ROOT/'components/audio/uart_thread_source_candidate/display_lv_object_display.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for child,match in [(False,True),(True,True),(False,False),(True,False)]:
  results=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);root=syms['audio_uart_display_lv_root'] if c else 0x2006f548
   screen,object,display,rows=(0x20080000,0x20081000,0x20082000,0x20083000)
   for a,n in ((screen,128),(object,128),(display,768),(rows,16)):u.mem_write(a,b'\0'*n)
   if child:u.mem_write(object+4,struct.pack('<I',screen))
   u.mem_write(root+8,struct.pack('<I',display));u.mem_write(display+0x2d4,struct.pack('<I',1));u.mem_write(display+0x2b8,struct.pack('<I',rows));u.mem_write(rows,struct.pack('<I',screen if match else 0x20084000))
   logs=[0]
   if not c:
    def cut(uc,a,size,_):
     if a==0x44d25c:
      logs[0]+=1;uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,cut)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,object if child else screen)
   u.emu_start((syms['audio_uart_lv_display_for_object'] if c else 0x44dc0a)|1,0x600000,count=5000)
   if c:logs[0]=struct.unpack('<I',u.mem_read(syms['log_calls'],4))[0]
   results.append((u.reg_read(UC_ARM_REG_R0),logs[0]))
  assert results[0]==results[1],(child,match,results)
  print('PASS LV object display',child,match)
