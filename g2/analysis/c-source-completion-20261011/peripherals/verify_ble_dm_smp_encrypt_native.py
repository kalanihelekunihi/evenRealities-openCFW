#!/usr/bin/env python3
"""Actual C/native DM SMP encryption request state and HCI effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_smp_encrypt.c'
STUB='''#include <stdint.h>
const uint8_t calc128Zeros[16]={0};
uint8_t *dmConnCcbById(uint8_t x){(void)x;return 0;}
void HciLeStartEncryptionCmd(uint16_t h,const uint8_t*r,uint16_t e,const uint8_t*k){(void)h;(void)r;(void)e;(void)k;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2',
                 '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000',
                 '-Wl,-e,DmSmpEncryptReq',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for present in (False,True):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   ccb,key=0x20080000,0x20080100
   u.mem_write(ccb,bytes([0xa5]*0x30));u.mem_write(ccb+0x0c,(0x3456).to_bytes(2,'little'))
   u.mem_write(key,bytes(range(16)))
   addrs={'lookup':(sy['dmConnCcbById']&~1) if compiled else 0x4b62a8,
          'send':(sy['HciLeStartEncryptionCmd']&~1) if compiled else 0x52b5a2}
   calls=[]
   def hook(uc,pc,n,user):
    if pc==addrs['lookup']:uc.reg_write(UC_ARM_REG_R0,ccb if present else 0)
    else:
     h,r,e,k=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
     calls.append((h,bytes(uc.mem_read(r,8)),e,bytes(uc.mem_read(k,16))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addrs.values():u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_R1,2);u.reg_write(UC_ARM_REG_R2,key)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['DmSmpEncryptReq'] if compiled else 0x55bbc4)|1,0x600000,count=1000)
   pair.append((bytes(u.mem_read(ccb,0x30)),calls))
  assert pair[0]==pair[1],(present,pair)
print('PASS_BLE_DM_SMP_ENCRYPT_NATIVE 2')
