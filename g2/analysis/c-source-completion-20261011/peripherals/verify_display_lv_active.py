"""Actual compiled-C/native LV display invalidation-enable getter."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
uint8_t audio_uart_display_lv_root[64];uint32_t log_calls;
void audio_uart_display_size_changed(void *p){(void)p;}
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,...){(void)a;(void)b;(void)c;(void)d;log_calls++;}
''')
 elf=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_display_has_active_window',str(ROOT/'components/audio/uart_thread_source_candidate/display_lv_active_window.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_lv_core_fields.c'),str(shim),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for provided,default,value in [(0,0,0),(0,1,-1),(0,1,0),(0,1,1),(1,0,-1),(1,0,0),(1,0,1)]:
  results=[]
  for c in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_map(0x20000000,0x100000);root=syms['audio_uart_display_lv_root'] if c else 0x2006f548;disp=0x20080000
   u.mem_write(disp,b'\0'*640);u.mem_write(disp+0x264,struct.pack('<i',value))
   u.mem_write(root+0x14,struct.pack('<I',disp if default else 0))
   logs=[0]
   if not c:
    def hook(uc,a,size,_):
     if a==0x44d25c:
      logs[0]+=1;uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,disp if provided else 0)
   u.emu_start((syms['audio_uart_lv_display_has_active_window'] if c else 0x44fed2)|1,0x600000,count=3000)
   if c:logs[0]=struct.unpack('<I',u.mem_read(syms['log_calls'],4))[0]
   results.append((u.reg_read(UC_ARM_REG_R0),logs[0]))
  assert results[0]==results[1],(provided,default,value,results)
  print('PASS LV active',provided,default,value)
