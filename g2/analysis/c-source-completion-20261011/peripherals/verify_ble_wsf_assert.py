"""Actual ARM compiled-C/native bounded WsfAssert nonnull-file branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_wsf_assert.c'
SHIM='''#include <stdint.h>
uintptr_t audio_ble_wsf_assert_hook;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void g2_log_fatal_idle(void){for(;;){}}
'''
def cstr(u,a):return bytes(u.mem_read(a,160)).split(b'\0')[0].decode('latin1')
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_wsf_assert',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for flags,file_present,hook_present in ((0,1,0),(1,1,0),(2,1,0),(4,1,0),(7,1,0),(0,0,0),(0,0,1)):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x300000,0x1000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20005000,b'file.c\0')
   u.mem_write(syms['audio_ble_wsf_assert_hook'] if compiled else 0x2007456c,struct.pack('<I',0x300001 if hook_present else 0))
   u.reg_write(UC_ARM_REG_R0,0x20005000 if file_present else 0);u.reg_write(UC_ARM_REG_R1,137)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   cuts={(syms['audio_log_flags']&~1 if compiled else 0x43d0ce):'flags',
         (syms['audio_log_extended']&~1 if compiled else 0x43d574):'log',
         (syms['compressed_log_output']&~1 if compiled else 0x43ce9e):'compact',
         (syms['g2_log_fatal_idle']&~1 if compiled else 0x44b0ae):'reset',
         0x300000:'callback'}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    if k=='flags':res=flags
    elif k=='log':calls.append((k,r0,cstr(uc,uc.reg_read(UC_ARM_REG_R1))));res=0
    elif k=='compact':calls.append((k,r0,cstr(uc,uc.reg_read(UC_ARM_REG_R1))));res=0
    elif k=='callback':calls.append((k,cstr(uc,r0),cstr(uc,uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2)));res=0
    else:
     calls.append((k,));uc.emu_stop();return
    uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_wsf_assert'] if compiled else 0x569a44)|1,0x600000,count=800)
   rows.append(calls)
  assert rows[0]==rows[1],(flags,file_present,hook_present,rows)
  print('PASS',flags,file_present,hook_present,rows[0])
