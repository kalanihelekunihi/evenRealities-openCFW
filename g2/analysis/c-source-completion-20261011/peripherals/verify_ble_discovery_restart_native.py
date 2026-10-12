#!/usr/bin/env python3
"""Actual ARM C/native discovery restart row and branch effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_discovery_restart.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_rows_200733fc[48],mode[2];const void *audio_ble_profile_dispatch_slot=mode;
volatile uint8_t audio_ble_trace_level_cell;
uint8_t *audio_ble_pair_record(uint8_t x){(void)x;return 0;}
void audio_ble_pair_record_clear_a(uint8_t*x,uint8_t y){(void)x;(void)y;}
void audio_ble_pair_record_attach(uint8_t*x,uint32_t y){(void)x;(void)y;}
void audio_uart_buffer_zero(void*x,uint32_t y,uint32_t z){(void)x;(void)y;(void)z;}
void audio_ble_service_discovery_start(uint8_t x){(void)x;}
int32_t audio_ble_hci_vendor_compare_44b610(const void*x,const void*y,uint32_t n){(void)x;(void)y;(void)n;return 1;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_service_discovery_restart_531f20',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('stage2','mode0','mode1','already_closed'):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   row=sym['audio_ble_subsystem_rows_200733fc'] if compiled else 0x200733fc
   mode=sym['mode'] if compiled else 0x20074400
   if not compiled:u.mem_write(0x20074360,mode.to_bytes(4,'little'))
   u.mem_write(mode,b'\x01\0' if kind in ('mode1','already_closed') else b'\0\0')
   data=bytearray(range(16));data[4:8]=b'\0'*4;data[11]=2 if kind=='stage2' else 1;data[12]=1 if kind=='already_closed' else 0;u.mem_write(row,bytes(data))
   calls=[];target=sym['audio_ble_service_discovery_start'] if compiled else 0x531d60
   def hook(uc,pc,n,user):calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_service_discovery_restart_531f20'] if compiled else 0x531f20)|1,0x600000,count=1000)
   pair.append((bytes(u.mem_read(row,16)),calls))
  assert pair[0]==pair[1],(kind,pair)
print('PASS_BLE_DISCOVERY_RESTART_NATIVE 4')
