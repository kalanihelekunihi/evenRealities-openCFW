#!/usr/bin/env python3
"""Bounded actual compiled-C/stock ring command dispatcher branches."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_send_packet.c'
STUB='''#include <stdint.h>
int32_t audio_uart_ring_touch_report_47269e(const uint8_t *p,uint16_t n){(void)p;(void)n;return 0;}
int32_t audio_uart_ring_touch_ack_47263c(const uint8_t *p){(void)p;return 0;}
int32_t audio_uart_ring_device_report_4727aa(const uint8_t *p,uint16_t n){(void)p;(void)n;return 0;}
void audio_uart_ring_wear_report_4728b2(const uint8_t *p){(void)p;}
void audio_uart_ring_target_addr_copy_4a2190(uint8_t *p,uint32_t n){(void)p;(void)n;}
void audio_ble_master_cleanup_ring_unpair_4a2c9c(const uint8_t *p){(void)p;}
uint32_t audio_event_loop_remove_delayed(void (*f)(void)){(void)f;return 0;}
void audio_event_loop_push_delayed(void (*f)(void),uint32_t a,uint32_t d){(void)f;(void)a;(void)d;}
uint32_t audio_ble_master_success_delayed(uint32_t x){return x;}
void audio_uart_ring_status_delayed_4a285c(void){}
void audio_uart_ring_disable_touch_4c4fe4(void){}
void audio_ble_master_followup_delayed(void){}
uint32_t audio_uart_ring_active(void){return 0;}
void audio_uart_ring_publish_link_ready_4a271e(void){}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_send_packet_472988',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 callbacks={'audio_ble_master_success_delayed':0x4bc418,'audio_uart_ring_status_delayed_4a285c':0x4a285c,'audio_uart_ring_disable_touch_4c4fe4':0x4c4fe4,'audio_ble_master_followup_delayed':0x4c4ee4}
 methods={'audio_uart_ring_touch_report_47269e':0x47269e,'audio_uart_ring_touch_ack_47263c':0x47263c,'audio_uart_ring_device_report_4727aa':0x4727aa,'audio_uart_ring_wear_report_4728b2':0x4728b2,'audio_uart_ring_target_addr_copy_4a2190':0x4a2190,'audio_ble_master_cleanup_ring_unpair_4a2c9c':0x4a2c9c,'audio_event_loop_remove_delayed':0x476ace,'audio_event_loop_push_delayed':0x47697e,'audio_uart_ring_active':0x4a2914,'audio_uart_ring_publish_link_ready_4a271e':0x4a271e,'audio_uart_buffer_zero':0x43c0e4,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
 cases=[(0x61,0,0),(0x85,0,0),(0x85,1,0),(0x8a,0,7),(0x8b,0,0),(0x8c,0,0),(0x94,0,0x20),(0x94,0,0x40),(0x94,0,0),(0x96,0,7),(0x99,0,0)]
 for opcode,owner,byte4 in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   packet=0x2007f100;data=bytearray(16);data[2]=opcode;data[4]=byte4;u.mem_write(packet,bytes(data))
   def callback(x):
    for n,a in callbacks.items():
     v=sym[n] if is_c else a
     if x in (v,v&~1,v|1):return n
    return hex(x)
   trace=[]
   for n,a in methods.items():
    addr=sym[n] if is_c else a
    def hook(uc,address,size,user_data,n=n):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     if n in ('audio_uart_ring_touch_report_47269e','audio_uart_ring_device_report_4727aa'):trace.append((n,r1,bytes(uc.mem_read(r0,8))))
     elif n in ('audio_uart_ring_touch_ack_47263c','audio_uart_ring_wear_report_4728b2'):trace.append((n,bytes(uc.mem_read(r0,8))))
     elif n=='audio_uart_ring_target_addr_copy_4a2190':trace.append(('addr_copy',r1));uc.mem_write(r0,b'ABCDEF')
     elif n=='audio_ble_master_cleanup_ring_unpair_4a2c9c':trace.append(('cleanup',bytes(uc.mem_read(r0,6))))
     elif n=='audio_event_loop_remove_delayed':trace.append(('remove',callback(r0)))
     elif n=='audio_event_loop_push_delayed':trace.append(('push',callback(r0),r1,r2))
     elif n=='audio_uart_ring_active':trace.append(('owner',));uc.reg_write(UC_ARM_REG_R0,owner)
     elif n=='audio_uart_ring_publish_link_ready_4a271e':trace.append(('publish',))
     elif n=='audio_uart_buffer_zero':trace.append(('zero',r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
     elif n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,7 if opcode in (0x8a,0x96) else 0)
     elif n=='audio_log_extended':trace.append(('extended',r0))
     else:trace.append(('compressed',r0))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   for n,a in callbacks.items():
    if n=='audio_ble_master_success_delayed':
     addr=sym[n] if is_c else a
     def cb_hook(uc,address,size,user_data):trace.append(('notify',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,cb_hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,packet);u.reg_write(UC_ARM_REG_R1,8)
   u.emu_start((sym['audio_uart_ring_send_packet_472988'] if is_c else 0x472988)|1,0x600000,count=5000)
   pair.append(trace)
  assert pair[0]==pair[1],(opcode,owner,byte4,pair)
 print('PASS_RING_SEND_PACKET_NATIVE',len(cases))
