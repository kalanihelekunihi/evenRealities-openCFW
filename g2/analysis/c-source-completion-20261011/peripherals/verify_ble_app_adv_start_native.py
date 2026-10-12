#!/usr/bin/env python3
"""Bounded native/C appAdvStart OTA, capacity and active-call effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_adv_start.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
const uint8_t *audio_ble_slave_profile_slot;
int ble_ota_mode_get(void){return 0;}
uint8_t appSlaveConnectableAdv(uint8_t n,const uint8_t *h){(void)n;(void)h;return 0;}
uint8_t appNumConns(uint8_t r){(void)r;return 0;}
void DmAdvSetInterval(uint8_t h,uint16_t a,uint16_t b){(void)h;(void)a;(void)b;}
void DmAdvConfig(uint8_t h,uint8_t t,uint8_t p,const uint8_t *a){(void)h;(void)t;(void)p;(void)a;}
void appSetAdvScanData(uint8_t h,uint8_t m){(void)h;(void)m;}
void DmAdvStart(uint8_t n,const uint8_t *h,const uint16_t *d,const uint8_t *e){(void)n;(void)h;(void)d;(void)e;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appAdvStart',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 native={0x46efec:'ota',0x4b32e2:'connect',0x4bacf0:'num',0x4b3292:'interval',0x4b3166:'config',0x4b3514:'data',0x4b31ea:'start'}
 # Native child addresses are verified from the 0x4b42f0 BL sites.
 compiled={sy['ble_ota_mode_get']&~1:'ota',sy['appSlaveConnectableAdv']&~1:'connect',sy['appNumConns']&~1:'num',sy['DmAdvSetInterval']&~1:'interval',sy['DmAdvConfig']&~1:'config',sy['appSetAdvScanData']&~1:'data',sy['DmAdvStart']&~1:'start'}
 for ota,connect,num in ((1,0,0),(0,1,2),(0,0,0)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
   cfg_slot=sy['audio_ble_slave_profile_slot'] if is_c else 0x20074350
   u.mem_write(cfg_slot,(0x20080100).to_bytes(4,'little'));u.mem_write(0x20080100,b'\x01')
   u.mem_write(state+0x57,b'\x01');u.mem_write(state+0x5d,b'\x00');u.mem_write(state+0x55,b'\x00')
   u.mem_write(0x20080000,b'\x00');u.mem_write(0x20080010,b'\x34\x12');u.mem_write(0x20080020,b'\x78\x56');u.mem_write(0x20080030,b'\x09')
   calls=[];children=compiled if is_c else native
   def hook(uc,pc,n,user):
    k=children[pc];calls.append(k)
    if k=='ota':uc.reg_write(UC_ARM_REG_R0,ota)
    elif k=='connect':uc.reg_write(UC_ARM_REG_R0,connect)
    elif k=='num':uc.reg_write(UC_ARM_REG_R0,num)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in children:u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,0x20080000);u.reg_write(UC_ARM_REG_R2,0x20080010);u.reg_write(UC_ARM_REG_R3,0x20080020)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,(0x20080030).to_bytes(4,'little')+(1).to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appAdvStart'] if is_c else 0x4b42f0)|1,0x600000,count=2000)
   pair.append((calls,bytes(u.mem_read(state+0x55,4))))
  assert pair[0]==pair[1],(ota,connect,num,pair)
print('PASS_BLE_APP_ADV_START_NATIVE 3')
