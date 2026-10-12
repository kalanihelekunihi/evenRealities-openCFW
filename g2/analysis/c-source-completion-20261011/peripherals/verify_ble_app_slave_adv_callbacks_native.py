#!/usr/bin/env python3
"""Actual C/native legacy advertising callback branch and timer effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_slave_adv_callbacks.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
uint8_t audio_ble_adv_transition_pending_20074f94,audio_ble_adv_timer_20073df4[0x20],audio_ble_adv_handler_id_20074f92;
uint8_t audio_ble_dm_adv_state(uint8_t h){(void)h;return 0;}
void WsfTimerStartMs(void *t,uint32_t m){(void)t;(void)m;}
void WsfTimerStop(void *t){(void)t;}
void appSlaveLegAdvTypeChanged(void *e){(void)e;}
void appSlaveNextLegAdvState(void *e){(void)e;}
void appSlaveLegAdvStart(void){}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSlaveLegAdvStop',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 native={'state':0x200719c8,'pending':0x20074f94,'timer':0x20073df4,'handler':0x20074f92,
         'adv':0x4bac4e,'starttimer':0x52a4c4,'stoptimer':0x52a4d2,
         'changed':0x4b2a92,'next':0x4b2aaa,'start':0x4b2a04}
 compiled={'state':sy['audio_ble_subsystem_link_state_200719c8'],'pending':sy['audio_ble_adv_transition_pending_20074f94'],
           'timer':sy['audio_ble_adv_timer_20073df4'],'handler':sy['audio_ble_adv_handler_id_20074f92'],
           'adv':sy['audio_ble_dm_adv_state']&~1,'starttimer':sy['WsfTimerStartMs']&~1,
           'stoptimer':sy['WsfTimerStop']&~1,'changed':sy['appSlaveLegAdvTypeChanged']&~1,
           'next':sy['appSlaveNextLegAdvState']&~1,'start':sy['appSlaveLegAdvStart']&~1}
 cases=[('stop',0x48,0,0,0,0),('stop',0x22,1,0,0,0),('stop',0x22,1,1,0,0),('stop',0x22,0,1,0,0),('stop',0x10,0,0,1,0),('restart',0x28,0,0,0,1),('restart',0x27,0,0,0,0),('restart',0x10,0,0,0,0)]
 for kind,event,advertising,pending,typechanged,directed in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   a=compiled if is_c else native
   u.mem_write(a['state'],bytes([0]*0x80));u.mem_write(a['state']+0x5b,bytes([typechanged]));u.mem_write(a['state']+0x75,bytes([directed]))
   u.mem_write(a['pending'],bytes([pending]));u.mem_write(a['handler'],b'\x09');u.mem_write(a['timer'],bytes([0]*0x20))
   msg=0x20080000;u.mem_write(msg,bytes([0,0,event,0,0])+bytes([0]*8))
   calls=[];targets={a[k]:k for k in ('adv','starttimer','stoptimer','changed','next','start')}
   def hook(uc,pc,n,user):
    k=targets[pc];calls.append(k)
    if k=='adv':uc.reg_write(UC_ARM_REG_R0,advertising)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in targets:u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_R0,msg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   entry=(sy['appSlaveLegAdvStop'] if kind=='stop' else sy['appSlaveLegAdvRestart']) if is_c else (0x4b2afe if kind=='stop' else 0x4b2b90)
   u.emu_start(entry|1,0x600000,count=1000)
   pair.append((calls,bytes(u.mem_read(a['state']+0x57,0x1f)),bytes(u.mem_read(a['pending'],1)),bytes(u.mem_read(a['timer'],0x10))))
  assert pair[0]==pair[1],(kind,event,advertising,pending,typechanged,directed,pair)
print('PASS_BLE_APP_SLAVE_ADV_CALLBACKS_NATIVE 8')
