"""Actual ARM C/native comparison for the BLE version grammar of scan 0x4d1638."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DIR=ROOT/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
typedef int32_t (*getter)(void *,uint32_t,uint32_t);
int32_t audio_ble_scan_core_full(getter g,void *c,const char *f,uint32_t **a,uint32_t m){(void)g;(void)c;(void)f;(void)a;(void)m;return -99;}
int32_t g2_iar_general_format(void *p,void *c,const char *f,uint32_t **a,uint32_t m){(void)p;(void)c;(void)f;(void)a;(void)m;return -99;}
'''
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_parse_version',str(DIR/'display_ble_format_scan_wrappers.c'),str(DIR/'display_ble_scan_core_version_candidate.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for sample in (b'2.2.6.10',b'1.2.3',b'2.2',b'X.2.3',b'-1.+2.3'):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20001000,sample+b'\x00');u.mem_write(0x20001100,b'%d.%d.%d\x00')
   u.mem_write(0x200ff000,struct.pack('<I',0x20002008))
   for r,v in [(UC_ARM_REG_R0,0x20001000),(UC_ARM_REG_R1,0x20001100),(UC_ARM_REG_R2,0x20002000),(UC_ARM_REG_R3,0x20002004),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(r,v)
   if not compiled:
    def hook(uc,a,size,_):
     if a in (0x4d58ae,0x4d58c2):
      x=uc.reg_read(UC_ARM_REG_R0)
      uc.reg_write(UC_ARM_REG_R0,1 if (x in (9,10,13,32) if a==0x4d58ae else 48<=x<=57) else 0)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     elif a==0x541e2c:
      ptr=uc.reg_read(UC_ARM_REG_R0);raw=bytes(uc.mem_read(ptr,32)).split(b'\0',1)[0]
      try:value=int(raw,10)
      except ValueError:value=0
      uc.reg_write(UC_ARM_REG_R0,value&0xffffffff);uc.reg_write(UC_ARM_REG_R1,0)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_parse_version'] if compiled else 0x475fc0)|1,0x600000,count=100000)
   rows.append((u.reg_read(UC_ARM_REG_R0),tuple(word(u,0x20002000+i*4) for i in range(3))))
  assert rows[0]==rows[1],(sample,rows)
  print('PASS',sample,rows[0])
