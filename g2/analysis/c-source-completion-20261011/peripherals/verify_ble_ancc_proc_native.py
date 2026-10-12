#!/usr/bin/env python3
"""Stock/C ANCC message dispatch and action-list effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_ancc_proc_msg.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ancc_state[0x100];uint8_t *audio_ble_ancc_service_context;
uint8_t DmConnRole(uint8_t c){(void)c;return 0;}
void audio_ble_ancc_value_update_4befce(const void*p){(void)p;}
void audio_ble_ancc_conn_open_4bea04(uint8_t c,uint32_t d){(void)c;(void)d;}
void audio_ble_ancc_conn_close_4bea14(void){}
uint32_t audio_ble_ancc_action_pop_4bea36(void){return 0;}
void audio_ble_ancc_get_notification_attribute_4beae8(uint32_t a,uint32_t b){(void)a;(void)b;}
uint32_t audio_ble_ancc_no_connection_active_4bea24(void){return 0;}
void audio_ble_ancc_get_next_delayed_4bea7a(void){}
void audio_event_loop_push_delayed(void(*f)(void),uint32_t a,uint32_t b){(void)f;(void)a;(void)b;}
uint32_t audio_event_loop_remove_delayed(void(*f)(void)){(void)f;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'ancc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_message',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 funcs={'DmConnRole':0x4b73c4,'audio_ble_ancc_value_update_4befce':0x4befce,'audio_ble_ancc_conn_open_4bea04':0x4bea04,'audio_ble_ancc_conn_close_4bea14':0x4bea14,'audio_ble_ancc_action_pop_4bea36':0x4bea36,'audio_ble_ancc_get_notification_attribute_4beae8':0x4beae8,'audio_ble_ancc_no_connection_active_4bea24':0x4bea24,'audio_event_loop_push_delayed':0x47697e,'audio_event_loop_remove_delayed':0x476ace}
 def run(c,event,role,popped,active):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_ancc_state'] if c else 0x200695c8
  context=sy['audio_ble_ancc_service_context'] if c else 0x200748a0
  u.mem_write(state+4,struct.pack('<I',0x12345678));u.mem_write(state+8,struct.pack('<H',1));u.mem_write(state+0x2c,struct.pack('<I',0xabcd1234))
  u.mem_write(context,struct.pack('<I',0x778899aa))
  p=0x20081000;u.mem_write(p,bytes((3,0,event,0))+b'\0'*12)
  callback=(sy['audio_ble_ancc_get_next_delayed_4bea7a']&~1) if c else 0x4bea7a
  addr={((sy[k]&~1) if c else v):k for k,v in funcs.items()};effects=[]
  def hook(uc,a,size,user):
   k=addr.get(a)
   if k is None:return
   r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
   if k=='DmConnRole':effects.append(('role',r0));uc.reg_write(UC_ARM_REG_R0,role)
   elif k=='audio_ble_ancc_action_pop_4bea36':effects.append(('pop',));uc.reg_write(UC_ARM_REG_R0,popped)
   elif k=='audio_ble_ancc_no_connection_active_4bea24':effects.append(('active',));uc.reg_write(UC_ARM_REG_R0,active)
   elif k=='audio_ble_ancc_value_update_4befce':effects.append(('value',r0))
   elif k=='audio_ble_ancc_conn_open_4bea04':effects.append(('open',r0,r1))
   elif k=='audio_ble_ancc_conn_close_4bea14':effects.append(('close',))
   elif k=='audio_ble_ancc_get_notification_attribute_4beae8':effects.append(('attr',r0,r1))
   elif k=='audio_event_loop_push_delayed':effects.append(('delay',r0==callback,r1,r2))
   elif k=='audio_event_loop_remove_delayed':effects.append(('remove',r0==callback))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in ((UC_ARM_REG_R0,0x42),(UC_ARM_REG_R1,p),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start(((sy['audio_ble_ancc_message']&~1) if c else 0x4bf780)|1,0x600000,count=30000)
  return effects
 cases=0
 for event in (5,9,10,13,14,0x27,0x28,0xa2,0xff):
  for role in (0,1):
   for popped,active in ((0,0),(1,0),(1,1)):
    a=run(False,event,role,popped,active);b=run(True,event,role,popped,active)
    assert a==b,(event,role,popped,active,a,b)
    cases+=1
 print('PASS_BLE_ANCC_PROC_NATIVE',cases)
