#!/usr/bin/env python3
"""Bounded compiled-C/stock heartbeat packet and diagnostics."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_heartbeat.c'
STUB='''#include <stdint.h>
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
void audio_dump_hex(const char *a,uint32_t b,const uint8_t *c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *p,uint32_t n){(void)p;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_heartbeat_472244',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for level in (0,7):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   trace=[]
   hooks=[('audio_uart_buffer_zero',0x43c0e4),('audio_dump_hex',0x43dacc),('audio_uart_ring_ble_send_data_4c4b7e',0x4c4b7e),('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
   for n,a in hooks:
    addr=sym[n] if is_c else a
    def hook(uc,address,size,user_data,n=n):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
     if n=='audio_uart_buffer_zero':trace.append(('zero',r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
     elif n=='audio_dump_hex':trace.append(('dump',r1,r3,bytes(uc.mem_read(r2,r3))))
     elif n=='audio_uart_ring_ble_send_data_4c4b7e':trace.append(('send',r1,bytes(uc.mem_read(r0,r1))));uc.reg_write(UC_ARM_REG_R0,0)
     elif n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
     elif n=='audio_log_extended':trace.append(('extended',r0))
     else:trace.append(('compressed',r0))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_heartbeat_472244'] if is_c else 0x472244)|1,0x600000,count=3000)
   pair.append((trace,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(level,pair)
 print('PASS_RING_HEARTBEAT_NATIVE',2)
