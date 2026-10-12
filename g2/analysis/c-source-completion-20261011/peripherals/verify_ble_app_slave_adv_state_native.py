#!/usr/bin/env python3
"""Actual C/native legacy advertising state/timer transitions."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_slave_adv_state.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
const uint8_t *audio_ble_slave_registration_slot;
uint8_t audio_ble_adv_transition_pending_20074f94,audio_ble_adv_timer_20073df4[0x20],audio_ble_adv_handler_id_20074f92;
uint8_t audio_ble_dm_adv_state(uint8_t h){(void)h;return 0;}
void WsfTimerStartMs(void *t,uint32_t m){(void)t;(void)m;}
void appAdvStart(uint8_t n,const uint8_t *h,const uint16_t *i,const uint16_t *d,const uint8_t *e,uint8_t c){(void)n;(void)h;(void)i;(void)d;(void)e;(void)c;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSlaveLegAdvStart',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 native={'state':0x200719c8,'cfg':0x2007434c,'pending':0x20074f94,'timer':0x20073df4,'handler':0x20074f92,'adv':0x4bac4e,'starttimer':0x52a4c4,'start':0x4b42f0}
 compiled={'state':sy['audio_ble_subsystem_link_state_200719c8'],'cfg':sy['audio_ble_slave_registration_slot'],'pending':sy['audio_ble_adv_transition_pending_20074f94'],'timer':sy['audio_ble_adv_timer_20073df4'],'handler':sy['audio_ble_adv_handler_id_20074f92'],'adv':sy['audio_ble_dm_adv_state']&~1,'starttimer':sy['WsfTimerStartMs']&~1,'start':sy['appAdvStart']&~1}
 cases=[('start',0,0,0,0),('start',0,1,0,0),('start',0,1,1,0),('start',0,1,1,1),('next',0,1,0,0),('next',0,1,1,0),('changed',1,1,0,0)]
 for kind,current,interval,advertising,pending in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   a=compiled if is_c else native;cfg=0x20080000
   u.mem_write(a['state'],bytes([0]*0x80));u.mem_write(a['state']+0x57,bytes([current]));u.mem_write(a['state']+0x5b,b'\x01')
   u.mem_write(a['cfg'],cfg.to_bytes(4,'little'));u.mem_write(cfg,bytes([3,0,4,0,5,0])+interval.to_bytes(2,'little')*3)
   u.mem_write(a['pending'],bytes([pending]));u.mem_write(a['handler'],b'\x09');u.mem_write(a['timer'],bytes([0]*0x20))
   calls=[];targets={a[k]:k for k in ('adv','starttimer','start')}
   def hook(uc,pc,n,user):
    k=targets[pc];calls.append(k)
    if k=='adv':uc.reg_write(UC_ARM_REG_R0,advertising)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in targets:u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   entry=(sy['appSlaveLegAdvStart'] if kind=='start' else sy['appSlaveNextLegAdvState'] if kind=='next' else sy['appSlaveLegAdvTypeChanged']) if is_c else (0x4b2a04 if kind=='start' else 0x4b2aaa if kind=='next' else 0x4b2a92)
   u.emu_start(entry|1,0x600000,count=1500)
   pair.append((calls,bytes(u.mem_read(a['state']+0x57,7)),bytes(u.mem_read(a['pending'],1)),bytes(u.mem_read(a['timer'],0x10))))
  assert pair[0]==pair[1],(kind,current,interval,advertising,pending,pair)
print('PASS_BLE_APP_SLAVE_ADV_STATE_NATIVE 7')
