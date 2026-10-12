#!/usr/bin/env python3
"""Actual ARM C/native SMP L2C control callback on credit transitions."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
STUB='''#include <stdint.h>
uint8_t *test_ccb;
uint8_t *smpCcbByConnId(uint8_t x){(void)x;return test_ccb;}
void smpSendPkt(uint8_t*a,void*b){(void)a;(void)b;}
void smpSmExecute(uint8_t*a,const uint8_t*b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_smp_l2c_control_callback_537444',
                 str(S/'display_ble_smp_l2c_control.c'),str(S/'display_ble_smp_state_idle.c'),
                 str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for event in (1,2):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   ccb=0x20080000;message=0x20080100
   c=bytearray(0x4c);c[0x3d]=1;c[0x3e]=0;u.mem_write(ccb,bytes(c))
   u.mem_write(message,bytes((1,0,event,0)))
   if compiled:u.mem_write(sym['test_ccb'],ccb.to_bytes(4,'little'))
   else:
    def lookup(uc,pc,n,user):
     uc.reg_write(UC_ARM_REG_R0,ccb);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,lookup,begin=0x5375fc,end=0x5375fc)
   u.reg_write(UC_ARM_REG_R0,message);u.reg_write(UC_ARM_REG_R1,0)
   u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,0x1234)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_smp_l2c_control_callback_537444'] if compiled else 0x537444)|1,0x600000,count=2000)
   pair.append((bytes(u.mem_read(ccb,0x4c)),bytes(u.mem_read(message,4)),u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(event,pair)
print('PASS_BLE_SMP_L2C_CONTROL_NATIVE 2')
