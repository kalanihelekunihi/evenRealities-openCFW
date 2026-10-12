#!/usr/bin/env python3
"""Bounded compiled-C/stock APP_MasterPublishRingLinkReady effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_publish_link_ready.c'
STUB='''#include <stdint.h>
volatile uint8_t audio_ble_ring_link_state,audio_ble_master_link_ready,audio_ble_master_connection_flag,audio_ble_master_publish_flag;
uint8_t *audio_ble_master_context;
void audio_ble_slave_security_state(uint8_t x){(void)x;}
uint32_t audio_uart_ring_active(void){return 0;}
void audio_ble_ring_policy_notify_success_49f646(void){}
void audio_ble_master_emit_ring_event(uint8_t x){(void)x;}
const char *audio_ble_ring_link_state_name(uint8_t x){(void)x;return "STATE";}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_publish_link_ready_4a271e',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[('already',0),('wrong',0),('wrong',7),('null',0),('no_conn',7),('success_no_owner',0),('success_owner',0),('success_owner',7)]
 for scenario,level in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cells={'audio_ble_ring_link_state':0x20074f85,'audio_ble_master_link_ready':0x20074f89,'audio_ble_master_connection_flag':0x20074f84,'audio_ble_master_publish_flag':0x20074f88,'audio_ble_master_context':0x200742fc}
   def cell(n):return sym[n] if is_c else cells[n]
   u.mem_write(cell('audio_ble_ring_link_state'),bytes([1 if scenario=='wrong' else 2]))
   u.mem_write(cell('audio_ble_master_link_ready'),bytes([1 if scenario=='already' else 0]))
   u.mem_write(cell('audio_ble_master_connection_flag'),b'\x05')
   u.mem_write(cell('audio_ble_master_publish_flag'),b'\x09')
   ctx=0x2007f000;u.mem_write(cell('audio_ble_master_context'),struct.pack('<I',0 if scenario=='null' else ctx));u.mem_write(ctx+0x55,bytes([0 if scenario=='no_conn' else 4]))
   trace=[]
   hooks=[('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e),('audio_ble_slave_security_state',0x4b82e8),('audio_uart_ring_active',0x4a2914),('audio_ble_ring_policy_notify_success_49f646',0x49f646),('audio_ble_master_emit_ring_event',0x4ac16c),('audio_ble_ring_link_state_name',0x49f828)]
   for n,a in hooks:
    addr=sym[n] if is_c else a
    def hook(uc,address,size,user_data,n=n):
     r0=uc.reg_read(UC_ARM_REG_R0)
     if n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
     elif n=='audio_log_extended':trace.append(('extended',r0))
     elif n=='compressed_log_output':trace.append(('compressed',r0))
     elif n=='audio_uart_ring_active':trace.append(('owner',));uc.reg_write(UC_ARM_REG_R0,int(scenario=='success_owner'))
     elif n=='audio_ble_ring_link_state_name':trace.append(('name',r0));uc.reg_write(UC_ARM_REG_R0,0x2007f100)
     else:trace.append((n,r0))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_publish_link_ready_4a271e'] if is_c else 0x4a271e)|1,0x600000,count=3000)
   state=tuple(u.mem_read(cell(n),1)[0] for n in ('audio_ble_ring_link_state','audio_ble_master_link_ready','audio_ble_master_connection_flag','audio_ble_master_publish_flag'))
   pair.append((trace,state))
  assert pair[0]==pair[1],(scenario,level,pair)
 print('PASS_RING_PUBLISH_LINK_READY_NATIVE',len(cases))
