#!/usr/bin/env python3
"""Actual C/native DM random address copy and address type lock effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_dm_adv_address.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_dm_handler_state[0x18];
void HciLeSetRandAddrCmd(const uint8_t *a){(void)a;}
void WsfTaskLock(void){} void WsfTaskUnlock(void){}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,DmDevSetRandAddr',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('random','type'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_dm_handler_state'] if is_c else 0x20073b78
   u.mem_write(state,bytes([0xa5]*0x18));addr=0x20080000;u.mem_write(addr,b'\x11\x22\x33\x44\x55\x66')
   hci=(sy['HciLeSetRandAddrCmd']&~1) if is_c else 0x52b4ba
   lock=(sy['WsfTaskLock']&~1) if is_c else 0x52b8c8
   unlock=(sy['WsfTaskUnlock']&~1) if is_c else 0x52b8d0
   calls=[];targets={hci:'hci',lock:'lock',unlock:'unlock'}
   def hook(uc,pc,n,user):calls.append(targets[pc]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in targets:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,addr if kind=='random' else 1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   entry=(sy['DmDevSetRandAddr'] if kind=='random' else sy['DmAdvSetAddrType']) if is_c else (0x4b304c if kind=='random' else 0x4b32b8)
   u.emu_start(entry|1,0x600000,count=1000)
   pair.append((calls,bytes(u.mem_read(state,0x18))))
  assert pair[0]==pair[1],(kind,pair)
print('PASS_BLE_DM_ADV_ADDRESS_NATIVE 2')
