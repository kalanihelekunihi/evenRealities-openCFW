#!/usr/bin/env python3
"""Actual ARM C/native descriptor verify and find-info transition."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_discovery_descriptors.c'
STUB='''#include <stdint.h>
void audio_ble_attc_find_info_request_4b571e(uint8_t a,uint16_t b,uint16_t c,uint8_t d){(void)a;(void)b;(void)c;(void)d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_discovery_descriptors_56b86a',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('empty','required_missing','find'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   context,handles,entries,e0,e1=0x20080000,0x20080100,0x20080200,0x20080300,0x20080400
   c=bytearray(32);c[0:4]=entries.to_bytes(4,'little');c[4:8]=handles.to_bytes(4,'little');c[12]=0 if kind=='empty' else (1 if kind=='required_missing' else 2);c[18]=0 if kind!='find' else 1;u.mem_write(context,bytes(c))
   u.mem_write(entries,e0.to_bytes(4,'little')+e1.to_bytes(4,'little'));u.mem_write(e0,b'\0\0\0\0'+(b'\x02' if kind=='required_missing' else b'\0')+b'\0'*3);u.mem_write(e1,b'\0\0\0\0\x04\0\0\0')
   u.mem_write(handles,b'\x0a\0'+(b'\x14\0' if kind=='find' else b'\0\0'))
   calls=[];target=sym['audio_ble_attc_find_info_request_4b571e'] if compiled else 0x4b571e
   def hook(uc,pc,n,user):
    calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,context);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_discovery_descriptors_56b86a'] if compiled else 0x56b86a)|1,0x600000,count=1000)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(context+18,1)),bytes(u.mem_read(handles,4)),calls))
  assert pair[0]==pair[1],(kind,pair)
print('PASS_BLE_DISCOVERY_DESCRIPTORS_NATIVE 3')
