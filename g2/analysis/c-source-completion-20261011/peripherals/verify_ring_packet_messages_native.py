#!/usr/bin/env python3
"""Stock/C ring protocol frame bytes and call ordering for three message types."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_packet_messages.c'
STUB='''#include <stdint.h>
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *p,uint32_t n){(void)p;return n;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_message_80_472378',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[('audio_uart_ring_message_80_472378',0x472378,0,0),('audio_uart_ring_message_80_472378',0x472378,1,0),('audio_uart_ring_message_400_4723d6',0x4723d6,1,0),('audio_uart_ring_message_400_4723d6',0x4723d6,0,1),('audio_uart_ring_message_1000_4722d8',0x4722d8,0x1234,0)]
 for name,native,arg0,arg1 in cases:
  for level in (0,7):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    trace=[]
    hooks=[('audio_uart_buffer_zero',0x43c0e4),('audio_uart_ring_ble_send_data_4c4b7e',0x4c4b7e),('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
    for h,a in hooks:
     addr=sym[h] if is_c else a
     def hook(uc,address,size,data,h=h):
      r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
      if h=='audio_uart_buffer_zero':trace.append(('zero',r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
      elif h=='audio_uart_ring_ble_send_data_4c4b7e':trace.append(('send',r1,bytes(uc.mem_read(r0,r1))));uc.reg_write(UC_ARM_REG_R0,r1)
      elif h=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
      elif h=='audio_log_extended':trace.append(('extended',r0,int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')))
      else:trace.append(('compressed',r0))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,arg0);u.reg_write(UC_ARM_REG_R1,arg1)
    u.emu_start((sym[name] if is_c else native)|1,0x600000,count=5000)
    pair.append((trace,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(name,arg0,arg1,level,pair)
 print('PASS_RING_PACKET_MESSAGES_NATIVE',len(cases)*2)
