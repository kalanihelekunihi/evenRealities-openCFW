"""Actual ARM compiled-C/native WsfTrace formatting/print/assert cut."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_wsf_trace.c'
SHIM='''#include <stdint.h>
#include <stdarg.h>
int32_t g2_log_transport_vformat_unbounded(char*a,const char*b,va_list c){(void)a;(void)b;(void)c;return 0;}
int32_t g2_log_transport_queue_failure(const char*a,...){(void)a;return 0;}
void audio_ble_wsf_assert(const char*a,uint32_t b){(void)a;(void)b;}
'''
def cstr(u,a):return bytes(u.mem_read(a,160)).split(b'\0')[0].decode('latin1')
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_wsf_trace',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for first_count in (5,1024):
  rows=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20005000,b'WARN\0');u.mem_write(0x20005020,b'MSG\0')
   u.reg_write(UC_ARM_REG_R0,0x20005000);u.reg_write(UC_ARM_REG_R1,0x20005020)
   u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,42)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   cuts={(syms['g2_log_transport_vformat_unbounded']&~1 if compiled else 0x473036):'format',
         (syms['g2_log_transport_queue_failure']&~1 if compiled else 0x4733ee):'print',
         (syms['audio_ble_wsf_assert']&~1 if compiled else 0x569a44):'assert'}
   calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    k=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0)
    if k=='format':
     calls.append((k,cstr(uc,uc.reg_read(UC_ARM_REG_R1))))
     uc.mem_write(r0,b'hello\0');res=5
    elif k=='print':
     calls.append((k,cstr(uc,r0)));res=first_count if len([x for x in calls if x[0]=='print'])==1 else 1
    else:calls.append((k,cstr(uc,r0),uc.reg_read(UC_ARM_REG_R1)));res=0
    uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_wsf_trace'] if compiled else 0x52a63c)|1,0x600000,count=1500)
   rows.append(calls)
  assert rows[0]==rows[1],(first_count,rows)
  print('PASS',first_count,rows[0])
