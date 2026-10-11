"""Bounded actual ARM C/native ABI comparison of the two IAR variadic shells."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_format_scan_wrappers.c'
SHIM='''#include <stdint.h>
typedef void *(*put_fn)(void *,uint32_t);
int32_t g2_iar_general_format(put_fn p,void *c,const char *f,uint32_t **a,uint32_t m){(void)p;(void)c;(void)f;(void)a;(void)m;return 0;}
int32_t audio_ble_scan_core(int32_t (*g)(void *,uint32_t,uint32_t),void *c,const char *f,uint32_t **a,uint32_t m){(void)g;(void)c;(void)f;(void)a;(void)m;return 0;}
'''
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def write_word(u,a,v):u.mem_write(a,struct.pack('<I',v))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_format_to_buffer',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for kind in ('format','scan'):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20001000,b'abc\x00');u.mem_write(0x20001100,b'%d.%d.%d\x00');u.mem_write(0x20002000,b'XXXXXXXX')
   u.reg_write(UC_ARM_REG_R0,0x20002000 if kind=='format' else 0x20001000)
   u.reg_write(UC_ARM_REG_R1,0x20001100);u.reg_write(UC_ARM_REG_R2,0x11111111);u.reg_write(UC_ARM_REG_R3,0x22222222)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);write_word(u,0x200ff000,0x33333333)
   u.reg_write(UC_ARM_REG_LR,0x600001)
   core=(syms['g2_iar_general_format']&~1 if kind=='format' else syms['audio_ble_scan_core']&~1) if compiled else (0x481836 if kind=='format' else 0x4d1638)
   seen=[]
   def hook(uc,a,size,_):
    if a!=core:return
    ctx=uc.reg_read(UC_ARM_REG_R1);ap=uc.reg_read(UC_ARM_REG_R3);varp=word(uc,ap)
    seen.append((word(uc,varp),word(uc,varp+4),word(uc,varp+8),word(uc,uc.reg_read(UC_ARM_REG_SP))))
    if kind=='format':
     out=word(uc,ctx);uc.mem_write(out,b'OK');write_word(uc,ctx,out+2);uc.reg_write(UC_ARM_REG_R0,2)
    else:uc.reg_write(UC_ARM_REG_R0,3)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   entry=(syms['audio_ble_format_to_buffer'] if kind=='format' else syms['audio_ble_parse_version']) if compiled else (0x4b4728 if kind=='format' else 0x475fc0)
   u.emu_start(entry|1,0x600000,count=300)
   rows.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20002000,4)) if kind=='format' else None))
  assert rows[0]==rows[1],(kind,rows)
  print('PASS',kind,rows[0])
