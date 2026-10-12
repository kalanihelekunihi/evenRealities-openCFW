"""Actual ARM C/native LV child-count and grid-copy wrapper comparisons."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
BASE=ROOT/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text('''#include <stdint.h>
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...){(void)a;(void)b;(void)c;(void)d;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return a;}
''')
 elf=Path(td)/'child.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_child_count_44ddea',
                 str(BASE/'display_lv_child_count.c'),str(BASE/'display_lv_grid_copy.c'),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 total=0
 for has_spec,count in ((False,0),(True,0),(True,3),(True,65535)):
  out=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   obj,spec=0x20003000,0x20003100
   u.mem_write(obj+8,struct.pack('<I',spec if has_spec else 0))
   u.mem_write(spec+0x30,struct.pack('<H',count))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,obj)
   u.emu_start((syms['audio_uart_lv_child_count_44ddea'] if is_c else 0x44ddea)|1,0x600000,count=100)
   out.append(u.reg_read(UC_ARM_REG_R0))
  assert out[0]==out[1],(has_spec,count,out);total+=1
 for length in (0,1,4,11,16):
  out=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dst,src=0x20003000,0x20003100
   u.mem_write(dst,b'X'*32);u.mem_write(src,b'abcdefghijklmnopqrstuvwxzy012345')
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,src);u.reg_write(UC_ARM_REG_R2,length)
   target=(syms['audio_queue_copy_bytes']&~1) if is_c else 0x439be4
   calls=[]
   def hook(uc,a,size,_):
    if a!=target:return
    r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
    calls.append((r0,r1,r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
    uc.reg_write(UC_ARM_REG_R0,r0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_uart_lv_grid_copy_454738'] if is_c else 0x454738)|1,0x600000,count=100)
   out.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dst,32))))
  assert out[0]==out[1],(length,out);total+=1
 print(f'PASS {total} compiled-C/native LV child-count and grid-copy cases')
