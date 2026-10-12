#!/usr/bin/env python3
"""Actual C/native ANCC delayed, ATT packet, and value-update effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
uint8_t audio_ble_ancc_state[0x600];uint8_t *audio_ble_ancc_service_context;
uint8_t audio_ble_ancc_service_state[8];uint8_t audio_efs_transfer_state[0x100];
uint32_t audio_ble_ancc_connection_tick;
uint32_t audio_log_level(void){return 0;} uint32_t audio_ota_transfer_active(void){return 0;}
uint32_t g2_flashdb_candidate_tick(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void *WsfMsgAlloc(uint16_t a){(void)a;return 0;}
void WsfMsgSend(uint8_t a,void*b){(void)a;(void)b;}
void audio_ble_attc_write_request(uint8_t a,uint16_t b,uint16_t c,const uint8_t*d){(void)a;(void)b;(void)c;(void)d;}
void audio_ble_ancc_notification_value_update_4bee5a(uint8_t*a,const uint8_t*b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'ancc.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_ancc_get_next_delayed_4bea7a',str(D/'display_ble_ancc_remaining.c'),str(D/'display_ble_ancc_value_update.c'),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 stock={'audio_ble_ancc_get_next_delayed_4bea7a':0x4bea7a,'audio_ble_ancc_get_notification_attribute_4beae8':0x4beae8,'audio_ble_ancc_value_update_4befce':0x4befce,
        'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,'WsfMsgAlloc':0x4bf99e,'WsfMsgSend':0x4bf9ba,'audio_ble_attc_write_request':0x4b579c,
        'audio_ota_transfer_active':0x4487ac,'g2_flashdb_candidate_tick':0x4490cc,'audio_ble_ancc_notification_value_update_4bee5a':0x4bee5a}
 def run(c,which,flags=0,alloc=1,handle=7,enabled=1,ota=0,efs=0,tick=6001):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  state=sy['audio_ble_ancc_state'] if c else 0x200695c8
  context=0x20082000
  u.mem_write(context,bytes((7,0,0,0,0 if which=='audio_ble_ancc_get_notification_attribute_4beae8' and handle==0 else 8,0,9,0)))
  u.mem_write((sy['audio_ble_ancc_service_context'] if c else 0x200748a0),struct.pack('<I',context))
  u.mem_write((sy['audio_ble_ancc_service_state'] if c else 0x200036c8),bytes((enabled,)))
  u.mem_write((sy['audio_efs_transfer_state']+0x75 if c else 0x20071cc8+0x75),bytes((efs,)))
  u.mem_write((sy['audio_ble_ancc_connection_tick'] if c else 0x200742f4),struct.pack('<I',1000))
  u.mem_write(state,bytes((3,0x42))+bytes(0x5fe));u.mem_write(0x20081000,bytes((0,0,0,0,0,0,0,0,0,0,handle,0))+bytes(20))
  effects=[]
  names={((sy[k]&~1) if c else v):k for k,v in stock.items() if k in sy}
  def hook(uc,a,size,user):
   k=names.get(a)
   if not k:return
   r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   if k=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,flags)
   elif k=='WsfMsgAlloc':effects.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,0x20090000 if alloc else 0)
   elif k=='WsfMsgSend':effects.append(('send',r0,bytes(uc.mem_read(r1,3))))
   elif k=='audio_ble_attc_write_request':effects.append(('att',r0,r1,r2,bytes(uc.mem_read(r3,r2))))
   elif k=='audio_ota_transfer_active':uc.reg_write(UC_ARM_REG_R0,ota)
   elif k=='g2_flashdb_candidate_tick':uc.reg_write(UC_ARM_REG_R0,tick)
   elif k=='audio_ble_ancc_notification_value_update_4bee5a':effects.append(('value',r0==context,r1==0x20081000))
   elif k=='audio_log_extended':effects.append(('log',r0))
   elif k=='compressed_log_output':effects.append(('compact',r0))
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  if which=='audio_ble_ancc_get_next_delayed_4bea7a':r0,r1=0xa2,0
  elif which=='audio_ble_ancc_get_notification_attribute_4beae8':r0,r1=context,0x12345678
  else:r0,r1=0x20081000,0
  for reg,val in ((UC_ARM_REG_R0,r0),(UC_ARM_REG_R1,r1),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start(((sy[which]&~1) if c else stock[which])|1,0x600000,count=30000)
  return effects
 cases=0
 for which in ('audio_ble_ancc_get_next_delayed_4bea7a','audio_ble_ancc_get_notification_attribute_4beae8','audio_ble_ancc_value_update_4befce'):
  vectors=([{'alloc':a,'flags':f} for a in (0,1) for f in (0,1,2,4,7)] if 'delayed' in which else
           [{'handle':h} for h in (0,7,8,9,10)] if 'attribute' in which else
           ([{'handle':h,'enabled':en,'ota':o,'efs':ef,'tick':tk} for h in (7,8,9,10) for en,o,ef,tk in ((1,0,0,6001),(1,0,0,3000),(0,0,0,6001),(1,1,0,6001),(1,0,1,6001))]+
            [{'handle':7,'tick':3000,'flags':f} for f in (1,2,4,7)]))
  for v in vectors:
   a=run(False,which,**v);b=run(True,which,**v)
   assert a==b,(which,v,a,b)
   cases+=1
 print('PASS_BLE_ANCC_REMAINING_NATIVE',cases)
