#!/usr/bin/env python3
"""Bounded compiled-C/stock ring command child effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_send_packet_children.c'
STUB='''#include <stdint.h>
volatile uint32_t audio_uart_ring_touch_tick,audio_uart_ring_wear_tick;
volatile uint8_t audio_uart_ring_worn;
uint8_t audio_ble_master_target_address[6];char audio_ble_master_target_name[15];
void *audio_queue_copy_bytes(void *p,const void *q,uint32_t n){(void)q;(void)n;return p;}
void audio_uart_ring_touch_event_4c5916(uint16_t a,uint32_t b,uint8_t c,uint8_t d){(void)a;(void)b;(void)c;(void)d;}
void audio_ble_device_manager_send(const uint8_t *p){(void)p;}
void audio_uart_ring_wear_persist_48eb32(uint32_t a,uint32_t b,const void *p){(void)a;(void)b;(void)p;}
uint32_t g2_flashdb_candidate_tick(void){return 0;}
int32_t audio_ble_ring_touch_message(uint8_t x){return x;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_touch_report_47269e',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 hooks={'audio_queue_copy_bytes':0x439be4,'audio_uart_ring_touch_event_4c5916':0x4c5916,'audio_ble_device_manager_send':0x4c659a,'audio_uart_ring_wear_persist_48eb32':0x48eb32,'g2_flashdb_candidate_tick':0x4490cc,'audio_ble_ring_touch_message':0x472426,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
 cases=[('touch',x,0,0) for x in (0,1,2,4,5,8)]+[('touch',4,7,1),('ack',1,7,0),('battery',6,0,0),('battery',5,7,0),('wear',1,0,0),('wear',0,7,1),('addr',0,0,0),('addr',1,0,0),('disable',0,7,0)]
 for kind,value,level,seed in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cells={'audio_uart_ring_touch_tick':0x20074900,'audio_uart_ring_wear_tick':0x20074904,'audio_uart_ring_worn':0x2007500c,'audio_ble_master_target_address':0x200003c0,'audio_ble_master_target_name':0x200003c8}
   def cell(n):return sym[n] if is_c else cells[n]
   u.mem_write(cell('audio_uart_ring_touch_tick'),struct.pack('<I',123 if seed else 0))
   u.mem_write(cell('audio_uart_ring_wear_tick'),struct.pack('<I',100 if seed else 0))
   u.mem_write(cell('audio_uart_ring_worn'),bytes([1 if seed else 0]))
   u.mem_write(cell('audio_ble_master_target_address'),b'ABCDEF')
   p=0x2007f100;data=bytearray(20);data[3]=0 if kind=='touch' else 1;data[4]=value;data[5]=7;data[6]=8;data[7:11]=struct.pack('<I',160);u.mem_write(p,bytes(data))
   trace=[]
   for n,a in hooks.items():
    addr=sym[n] if is_c else a
    def hook(uc,address,size,user_data,n=n):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
     if n=='audio_queue_copy_bytes':trace.append(('copy',r2,bytes(uc.mem_read(r1,r2))));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
     elif n=='audio_uart_ring_touch_event_4c5916':trace.append(('touch_evt',r0,r1,r2,r3))
     elif n=='audio_ble_device_manager_send':trace.append(('dm',bytes(uc.mem_read(r0,8))))
     elif n=='audio_uart_ring_wear_persist_48eb32':trace.append(('persist',r0,r1,bytes(uc.mem_read(r2,4))))
     elif n=='g2_flashdb_candidate_tick':trace.append(('tick',));uc.reg_write(UC_ARM_REG_R0,160)
     elif n=='audio_ble_ring_touch_message':trace.append(('touch_msg',r0));uc.reg_write(UC_ARM_REG_R0,0)
     elif n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
     elif n=='audio_log_extended':trace.append(('extended',r0))
     else:trace.append(('compressed',r0))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   names={'touch':('audio_uart_ring_touch_report_47269e',0x47269e),'ack':('audio_uart_ring_touch_ack_47263c',0x47263c),'battery':('audio_uart_ring_device_report_4727aa',0x4727aa),'wear':('audio_uart_ring_wear_report_4728b2',0x4728b2),'addr':('audio_uart_ring_target_addr_copy_4a2190',0x4a2190),'disable':('audio_uart_ring_disable_touch_4c4fe4',0x4c4fe4)}
   name,stock=names[kind]
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,p)
   u.reg_write(UC_ARM_REG_R1,value if kind in ('battery','addr') else (8 if kind=='touch' else 0))
   u.emu_start((sym[name] if is_c else stock)|1,0x600000,count=3000)
   pair.append((trace,bytes(u.mem_read(cell('audio_uart_ring_touch_tick'),4)),bytes(u.mem_read(cell('audio_uart_ring_wear_tick'),4)),u.mem_read(cell('audio_uart_ring_worn'),1)[0],bytes(u.mem_read(p,6)) if kind=='addr' else None,bytes(u.mem_read(cell('audio_ble_master_target_name'),7)) if kind=='addr' else None,u.reg_read(UC_ARM_REG_R0) if kind in ('touch','ack','battery') else None))
  assert pair[0]==pair[1],(kind,value,level,seed,pair)
 print('PASS_RING_SEND_PACKET_CHILDREN_NATIVE',len(cases))
