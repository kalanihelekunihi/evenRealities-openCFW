"""Compiled-C/native connect-event state and WSF message cases with child contracts cut."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
shim='''#include <stdint.h>
volatile uint8_t audio_ble_master_connect_state,audio_ble_master_connection_flag,audio_ble_ring_link_state;
uint8_t *audio_ble_master_context;uint8_t audio_ble_master_target_address[6];
uint32_t audio_uart_ring_active(void){return 1;} void audio_ble_master_reset_retry_count(void){} void audio_ble_master_clear_failure_notify(void){}
uint32_t audio_ble_master_link_matches_target(const uint8_t*p){(void)p;return 0;}
uint8_t audio_dm_conn_role(uint8_t p){return p;} const uint8_t *audio_dm_conn_peer_address(uint8_t p){(void)p;return 0;}
uint32_t audio_ble_privacy_compare_address(const uint8_t*a,const uint8_t*b){(void)a;(void)b;return 0;}
void *audio_wsf_msg_alloc(uint16_t p){(void)p;return 0;}void audio_wsf_msg_send(uint8_t p,void*q){(void)p;(void)q;}
uint32_t audio_event_loop_remove_delayed(void(*p)(void)){(void)p;return 0;}void audio_event_loop_push_delayed(void(*p)(void),uint32_t a,uint32_t b){(void)p;(void)a;(void)b;}
void audio_ble_master_success_delayed(void){} void audio_ble_master_followup_delayed(void){} void audio_ble_master_disconnect_delayed(void){}
uint32_t audio_log_level(void){return 0;}void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(shim);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_master_connect_event',str(ROOT/'components/audio/uart_thread_source_candidate/display_ble_master_connect_event.c'),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 names={'audio_event_loop_remove_delayed':0x476ace,'audio_event_loop_push_delayed':0x47697e,'audio_log_level':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e,'audio_uart_ring_active':0x4a2914,'audio_ble_master_reset_retry_count':0x4a2300,'audio_ble_master_clear_failure_notify':0x4a15c0,'audio_ble_master_link_matches_target':0x4a2864,'audio_dm_conn_role':0x4bf44e,'audio_dm_conn_peer_address':0x4b6eea,'audio_ble_privacy_compare_address':0x4d294a,'audio_wsf_msg_alloc':0x4bf99e,'audio_wsf_msg_send':0x4bf9ba}
 for event,owner,ring,conn,match in ((0,1,0,0,0),(1,0,0,2,0),(1,1,6,2,0),(1,1,0,2,1),(0x81,1,0,0,0),(2,1,0,2,0),(1,1,0,0,0)):
  obs=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cells=(syms['audio_ble_master_connect_state'],syms['audio_ble_master_connection_flag'],syms['audio_ble_ring_link_state'],syms['audio_ble_master_context']) if compiled else (0x20074f87,0x20074f84,0x20074f85,0x200742fc)
   state,flag,ringcell,ctxptr=cells
   u.mem_write(state,b'\x02');u.mem_write(flag,b'\x03');u.mem_write(ringcell,bytes([ring]));u.mem_write(ctxptr,struct.pack('<I',0x20002000));u.mem_write(0x20002055,bytes([conn,7]))
   cuts={(syms[n]&~1 if compiled else a):n for n,a in names.items()};calls=[]
   def hook(uc,a,size,_):
    n=cuts.get(a)
    if n is None:return
    r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
    if n=='audio_log_level':uc.reg_write(UC_ARM_REG_R0,0)
    elif n=='audio_uart_ring_active':uc.reg_write(UC_ARM_REG_R0,owner);calls.append(('owner',))
    elif n=='audio_ble_master_link_matches_target':uc.reg_write(UC_ARM_REG_R0,match);calls.append(('match',))
    elif n=='audio_wsf_msg_alloc':uc.reg_write(UC_ARM_REG_R0,0x20003000);calls.append(('alloc',r0))
    elif n=='audio_wsf_msg_send':calls.append(('send',r0,bytes(uc.mem_read(r1,12))))
    elif n=='audio_event_loop_remove_delayed':calls.append(('remove',))
    elif n=='audio_event_loop_push_delayed':calls.append(('push',r1,r2))
    elif n=='audio_ble_master_reset_retry_count':calls.append(('reset',))
    elif n=='audio_ble_master_clear_failure_notify':calls.append(('clear',))
    elif n=='audio_dm_conn_role':uc.reg_write(UC_ARM_REG_R0,1)
    elif n=='audio_dm_conn_peer_address':uc.reg_write(UC_ARM_REG_R0,0)
    elif n=='audio_ble_privacy_compare_address':uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,event);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((syms['audio_ble_master_connect_event'] if compiled else 0x4a1b60)|1,0x600000,count=2000)
   obs.append((calls,u.mem_read(state,1)[0],u.mem_read(flag,1)[0]))
  assert obs[0]==obs[1],(event,owner,ring,conn,match,obs)
  print('PASS master event',event,owner,ring,conn,match)
