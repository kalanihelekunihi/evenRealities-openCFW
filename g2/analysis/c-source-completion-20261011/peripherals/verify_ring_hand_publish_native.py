#!/usr/bin/env python3
"""Compare actual compiled ARM C/native hand-sync packet and call arguments."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_hand_publish.c'
STUB='''#include <stdint.h>
uint8_t audio_uart_hand_record[48];
uint8_t audio_uart_device_role_get(void){return 0;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t x){(void)p;(void)n;(void)x;}
void *audio_queue_copy_bytes(void *a,const void *b,uint32_t n){(void)b;(void)n;return a;}
int32_t audio_settings_send_peer_packet(uint16_t a,const void *b,uint32_t c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_unpair_publish_hand_4661a6',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for role in (1,2):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   record=sym['audio_uart_hand_record'] if is_c else 0x200736d4
   u.mem_write(record,bytes(range(48)));trace=[]
   hooks=[('role','audio_uart_device_role_get',0x45a568),('zero','audio_uart_buffer_zero',0x43c0e4),('copy','audio_queue_copy_bytes',0x439be4),('send','audio_settings_send_peer_packet',0x465480),('flags','audio_log_level',0x43d0ce)]
   for name,symbol,native in hooks:
    addr=sym[symbol] if is_c else native
    def hook(uc,address,size,user_data,name=name):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     if name=='role':uc.reg_write(UC_ARM_REG_R0,role)
     elif name=='zero':uc.mem_write(r0,bytes([r2&255])*r1)
     elif name=='copy':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
     elif name=='send':trace.append((r0,r2,uc.reg_read(UC_ARM_REG_R3),bytes(uc.mem_read(r1,48))))
     else:uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_unpair_publish_hand_4661a6'] if is_c else 0x4661a6)|1,0x600000,count=6000)
   pair.append(trace)
  assert pair[0]==pair[1],(role,pair)
print('PASS_RING_HAND_PUBLISH_NATIVE 2')
