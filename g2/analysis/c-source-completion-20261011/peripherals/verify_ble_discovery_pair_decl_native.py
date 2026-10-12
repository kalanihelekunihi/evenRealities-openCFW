#!/usr/bin/env python3
"""Actual ARM C/native descriptor-pair and characteristic-declaration writes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
S=[D/'display_ble_discovery_desc_pair.c',D/'display_ble_discovery_char_decl.c']
STUB='''#include <stdint.h>
volatile uint8_t audio_ble_trace_level_cell;uint8_t audio_ble_att_uuid_base_2000044c[16];
int32_t g2_lfs_memcmp(const void*a,const void*b,uint32_t n){const uint8_t*x=a,*y=b;for(uint32_t i=0;i<n;i++)if(x[i]!=y[i])return x[i]-y[i];return 0;}
int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t n){return g2_lfs_memcmp(a,b,n);}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_discovery_proc_char_decl_56bb1c',*[str(s) for s in S],str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('char','desc'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   context,entries,entry,handles,uuid,item=0x20080000,0x20080100,0x20080200,0x20080300,0x20080400,0x20080500
   c=bytearray(32);c[0:4]=entries.to_bytes(4,'little');c[4:8]=handles.to_bytes(4,'little');c[12]=1;c[16:18]=b'\0\x01';c[19]=0xff;u.mem_write(context,bytes(c))
   u.mem_write(entries,entry.to_bytes(4,'little'));u.mem_write(entry,uuid.to_bytes(4,'little')+(b'\x04' if kind=='desc' else b'\0')+b'\0'*3)
   u.mem_write(handles,b'\0\0\0\0');u.mem_write(uuid,b'\x37\x2a' if kind=='char' else b'\x02\x29')
   u.mem_write(item,b'\x20\0\x00\x21\0\x37\x2a' if kind=='char' else b'\x25\0\x02\x29')
   trace=[]
   for name,target in [('wsf',sym['audio_ble_wsf_trace'] if compiled else 0x52a63c),('level',0 if compiled else 0x4c9c50)]:
    if target==0:continue
    def hook(uc,pc,n,user,name=name):
     if name=='level':uc.reg_write(UC_ARM_REG_R0,0)
     else:trace.append(name)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   entryfn=(sym['audio_ble_discovery_proc_char_decl_56bb1c'] if kind=='char' else sym['audio_ble_discovery_proc_desc_pair_56b8fa']) if compiled else (0x56bb1c if kind=='char' else 0x56b8fa)
   u.reg_write(UC_ARM_REG_R0,context);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,item);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start(entryfn|1,0x600000,count=5000)
   pair.append((bytes(u.mem_read(handles,4)),bytes(u.mem_read(context+19,1)),trace))
  assert pair[0]==pair[1],(kind,pair)
print('PASS_BLE_DISCOVERY_PAIR_DECL_NATIVE 2')
