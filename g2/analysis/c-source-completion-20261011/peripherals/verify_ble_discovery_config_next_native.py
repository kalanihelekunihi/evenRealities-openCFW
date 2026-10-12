#!/usr/bin/env python3
"""Compare actual ARM C/native Cordio config descriptor walk and request effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_discovery_config_next.c'
STUB='''#include <stdint.h>
void audio_ble_attc_read_request(uint8_t a,uint16_t b){(void)a;(void)b;}
void audio_ble_attc_write_request(uint8_t a,uint16_t b,uint16_t c,const uint8_t*d){(void)a;(void)b;(void)c;(void)d;}
'''
cases=[('empty',0,0,0,0),('skip',2,0,0,0),('read',1,0x1234,0,0),('write',1,0x1234,3,0)]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_discovery_config_next_56beb6',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for case,count,handle,size,_ in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   context=0x20080000;handles=0x20080100;desc=0x20080200
   c=bytearray(32);c[4:8]=handles.to_bytes(4,'little');c[8:12]=desc.to_bytes(4,'little');c[13]=count;u.mem_write(context,bytes(c))
   u.mem_write(handles,handle.to_bytes(2,'little')+b'\0'*14)
   d=bytearray(16);d[0:4]=(0x20080300).to_bytes(4,'little');d[4]=size;d[5]=0;d[8:12]=(0x20080300).to_bytes(4,'little');d[13]=0;u.mem_write(desc,bytes(d))
   trace=[]
   for name,cs,stock in [('read','audio_ble_attc_read_request',0x4b575a),('write','audio_ble_attc_write_request',0x4b579c)]:
    target=sym[cs] if compiled else stock
    def hook(uc,pc,n,user,name=name):
     trace.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,context);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_discovery_config_next_56beb6'] if compiled else 0x56beb6)|1,0x600000,count=3000)
   pair.append((u.reg_read(UC_ARM_REG_R0),u.mem_read(context+18,1),trace))
  assert pair[0]==pair[1],(case,pair)
print('PASS_BLE_DISCOVERY_CONFIG_NEXT_NATIVE',len(cases))
