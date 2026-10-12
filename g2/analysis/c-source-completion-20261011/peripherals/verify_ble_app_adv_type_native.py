#!/usr/bin/env python3
"""Compiled C/native appSetAdvType branch, state, and child-call comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_type.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
void appSlaveResetAdvDataOffset(uint8_t h){(void)h;}
void appAdvStart(uint8_t n,const uint8_t *h,const uint16_t *i,const uint16_t *d,const uint8_t *m,uint8_t c){(void)n;(void)h;(void)i;(void)d;(void)m;(void)c;}
void DmAdvStop(uint8_t n,const uint8_t *h){(void)n;(void)h;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSetAdvType',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 native={0x4b334c:'reset',0x4b42f0:'start',0x4b3250:'stop'}
 compiled={sy['appSlaveResetAdvDataOffset']&~1:'reset',sy['appAdvStart']&~1:'start',sy['DmAdvStop']&~1:'stop'}
 cases=[(1,0,3),(4,0,3),(2,2,3),(2,0,3),(2,0,0),(2,0xff,0)]
 for typ,disc,adv in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
   u.mem_write(state+0x57,bytes([adv,0,0,0,0,0,disc]))
   calls=[]
   def hook(uc,pc,n,user):
    kind=(compiled if is_c else native)[pc];sp=uc.reg_read(UC_ARM_REG_SP)
    if kind=='reset':calls.append((kind,uc.reg_read(UC_ARM_REG_R0)&0xff))
    elif kind=='start':calls.append((kind,uc.reg_read(UC_ARM_REG_R0)&0xff,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1)),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R2),2)),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R3),2)),bytes(uc.mem_read(int.from_bytes(uc.mem_read(sp,4),'little'),1)),int.from_bytes(uc.mem_read(sp+4,4),'little')&0xff))
    else:calls.append((kind,uc.reg_read(UC_ARM_REG_R0)&0xff,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),1))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in (compiled if is_c else native):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,typ)
   u.reg_write(UC_ARM_REG_R2,0x1234);u.reg_write(UC_ARM_REG_R3,0x5678)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,(9).to_bytes(4,'little')+(1).to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appSetAdvType'] if is_c else 0x4b4510)|1,0x600000,count=1000)
   pair.append((bytes(u.mem_read(state+0x57,7)),calls))
  assert pair[0]==pair[1],(typ,disc,adv,pair)
print('PASS_BLE_APP_ADV_TYPE_NATIVE 6')
