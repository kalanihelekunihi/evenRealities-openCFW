#!/usr/bin/env python3
"""Actual ARM C/native SMP send/queue and L2CAP header effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_smp_packet_send.c'
STUB='''#include <stdint.h>
volatile uint8_t audio_ble_trace_level_cell;
void HciSendAclData(void*x){(void)x;}
void audio_ble_wsf_message_free(void*x){(void)x;}
uint32_t g2_smp_candidate_compare(void*a,uint32_t b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,smpSendPkt',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for case in ('send','queue'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   ccb=0x20080000;packet=0x20080100
   c=bytearray(0x4c);c[0x3c]=(case=='queue');c[0x38:0x3a]=b'\x34\x12';u.mem_write(ccb,bytes(c))
   p=bytearray(32);p[8]=1;u.mem_write(packet,bytes(p))
   if not compiled:
    def send(uc,pc,n,user):uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,send,begin=0x52ad04,end=0x52ad04)
   u.reg_write(UC_ARM_REG_R0,ccb);u.reg_write(UC_ARM_REG_R1,packet)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['smpSendPkt'] if compiled else 0x537a5a)|1,0x600000,count=5000)
   pair.append((bytes(u.mem_read(ccb,0x4c)),bytes(u.mem_read(packet,16))))
  assert pair[0]==pair[1],(case,pair)
print('PASS_BLE_SMP_PACKET_SEND_NATIVE 2')
