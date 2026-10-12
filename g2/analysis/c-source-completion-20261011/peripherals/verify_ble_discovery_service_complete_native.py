#!/usr/bin/env python3
"""Actual ARM C/native service-completion status and range effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_discovery_service_complete.c'
STUB='''#include <stdint.h>
volatile uint8_t audio_ble_trace_level_cell;
int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t n){const uint8_t*x=a,*y=b;for(uint32_t i=0;i<n;i++)if(x[i]!=y[i])return x[i]-y[i];return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_discovery_service_complete_56bf32',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('found','empty','status','unexpected'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   context,message,payload=0x20080000,0x20080100,0x20080200
   u.mem_write(context,b'\0'*32);u.mem_write(payload,b'\x11\0\x22\0')
   m=bytearray(16);m[2]=2 if kind=='unexpected' else 3;m[3]=5 if kind=='status' else 0;m[4:8]=payload.to_bytes(4,'little');m[8]=0 if kind=='empty' else 4;u.mem_write(message,bytes(m))
   trace=[]
   for name,target in [('wsf',sym['audio_ble_wsf_trace'] if compiled else 0x52a63c),('level',0 if compiled else 0x4c9c50)]:
    if target==0:continue
    def hook(uc,pc,n,user,name=name):
     if name=='level':uc.reg_write(UC_ARM_REG_R0,0)
     else:trace.append(name)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,context);u.reg_write(UC_ARM_REG_R1,message);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_discovery_service_complete_56bf32'] if compiled else 0x56bf32)|1,0x600000,count=3000)
   pair.append((u.reg_read(UC_ARM_REG_R0)&0xff,bytes(u.mem_read(context+14,4)),trace))
  assert pair[0]==pair[1],(kind,pair)
print('PASS_BLE_DISCOVERY_SERVICE_COMPLETE_NATIVE 4')
