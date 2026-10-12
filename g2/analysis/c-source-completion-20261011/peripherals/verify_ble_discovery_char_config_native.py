#!/usr/bin/env python3
"""Actual ARM C/native characteristic-start and config-complete calls."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_discovery_char_config.c'
STUB='''#include <stdint.h>
void audio_ble_attc_read_by_type_56c4ee(uint8_t a,uint16_t b,uint16_t c,uint8_t d,const uint8_t*e,uint32_t f){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t audio_ble_discovery_config_next_56beb6(uint8_t a,uint8_t*b){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_discovery_char_start_56c1b8',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('char','config'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   c=bytearray(32);c[14:18]=b'\x34\x12\x78\x56';c[18]=7;c[19]=4;context=0x20080000;u.mem_write(context,bytes(c));trace=[]
   if kind=='char':target=sym['audio_ble_attc_read_by_type_56c4ee'] if compiled else 0x56c4ee
   else:target=sym['audio_ble_discovery_config_next_56beb6'] if compiled else 0x56beb6
   def hook(uc,pc,n,user):
    if kind=='char':
     sp=uc.reg_read(UC_ARM_REG_SP);uuid=int.from_bytes(uc.mem_read(sp,4),'little');option=int.from_bytes(uc.mem_read(sp+4,4),'little')
     trace.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),bytes(uc.mem_read(uuid,2)),option))
    else:
     trace.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)-context));uc.reg_write(UC_ARM_REG_R0,0x79)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   entry=(sym['audio_ble_discovery_char_start_56c1b8'] if kind=='char' else sym['audio_ble_discovery_config_complete_56c396']) if compiled else (0x56c1b8 if kind=='char' else 0x56c396)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,context);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start(entry|1,0x600000,count=200)
   pair.append((bytes(u.mem_read(context+18,2)),trace,u.reg_read(UC_ARM_REG_R0) if kind=='config' else 0))
  assert pair[0]==pair[1],(kind,pair)
print('PASS_BLE_DISCOVERY_CHAR_CONFIG_NATIVE 2')
