#!/usr/bin/env python3
"""Stock/C WsfTrace format, output, and assertion effect comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_wsf_trace.c'
SHIM='''#include <stdint.h>
#include <stdarg.h>
int32_t g2_log_transport_vformat_unbounded(char*a,const char*b,va_list c){(void)a;(void)b;(void)c;return 0;}
int32_t g2_log_transport_queue_failure(const char*a,...){(void)a;return 0;}
void audio_ble_wsf_assert(const char*a,uint32_t b){(void)a;(void)b;for(;;){}}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'wsf.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_wsf_trace',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,written):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  fmt=(sy['g2_log_transport_vformat_unbounded']&~1) if c else 0x473036
  log=(sy['g2_log_transport_queue_failure']&~1) if c else 0x4733ee
  ass=(sy['audio_ble_wsf_assert']&~1) if c else 0x569a44
  tag=0x20080000;u.mem_write(tag,b'TRACE\0');effects=[]
  def txt(p):return bytes(u.mem_read(p,150)).split(b'\0')[0].decode('ascii')
  def hook(uc,addr,size,user):
   if addr==fmt:
    out=uc.reg_read(UC_ARM_REG_R0);ap=uc.reg_read(UC_ARM_REG_R2)
    args=struct.unpack('<III',bytes(uc.mem_read(ap,12)))
    effects.append(('format',txt(uc.reg_read(UC_ARM_REG_R1)),args))
    uc.mem_write(out,b'TRACE\0');uc.reg_write(UC_ARM_REG_R0,5)
   elif addr==log:
    effects.append(('log',txt(uc.reg_read(UC_ARM_REG_R0))))
    uc.reg_write(UC_ARM_REG_R0,written if len(effects)==2 else 0)
   elif addr==ass:
    effects.append(('assert',txt(uc.reg_read(UC_ARM_REG_R0)),uc.reg_read(UC_ARM_REG_R1)))
    uc.reg_write(UC_ARM_REG_PC,0x600000);return
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((UC_ARM_REG_R0,tag),(UC_ARM_REG_R1,0x12345678),(UC_ARM_REG_R2,0xabcdef00),(UC_ARM_REG_R3,0x87654321),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  entry=(sy['audio_ble_hci_wsf_trace']&~1) if c else 0x52a63c
  u.emu_start(entry|1,0x600000,count=50000)
  return effects
 cases=0
 for written in (0,5,1023,1024,0xffffffff):
  a=run(False,written);b=run(True,written)
  assert a==b,(written,a,b)
  cases+=1
 print('PASS_L2C_WSF_TRACE_NATIVE',cases)
