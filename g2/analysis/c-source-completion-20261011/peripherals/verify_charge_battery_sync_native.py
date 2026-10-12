#!/usr/bin/env python3
"""Compare bounded compiled ARM C/native battery-sync constructor states."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_charge_battery_sync_init.c'
STUB='''#include <stdint.h>
void *audio_charge_sync_mutex;uint8_t audio_charge_sync_record[24],audio_charge_sync_peer_record[8];
volatile uint8_t audio_charge_sync_flag_20074f97,audio_charge_sync_flag_20074f98,audio_charge_sync_flag_20074f99;
volatile uint16_t audio_charge_sync_mode_20074f1a,audio_charge_sync_phase_20074f1c;
void *audio_uart_mutex_new(const void*p){(void)p;return 0;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
void audio_settings_init_battery_callbacks(void){}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_device_manager_battery_sync_init',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 native={'audio_charge_sync_mutex':0x20074370,'audio_charge_sync_record':0x20073b30,'audio_charge_sync_peer_record':0x20074104,'audio_charge_sync_flag_20074f97':0x20074f97,'audio_charge_sync_flag_20074f98':0x20074f98,'audio_charge_sync_mode_20074f1a':0x20074f1a,'audio_charge_sync_phase_20074f1c':0x20074f1c,'audio_charge_sync_flag_20074f99':0x20074f99}
 for mutex in (0,0x20060000):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   for name,address in native.items():u.mem_write((sym[name] if is_c else address),b'\xaa'*(24 if name.endswith('record') and 'peer' not in name else 8 if 'peer_record' in name else 4 if 'mutex' in name else 2))
   trace=[];hooks=[('mutex','audio_uart_mutex_new',0x44971c),('zero','audio_uart_buffer_zero',0x43c0e4),('callbacks','audio_settings_init_battery_callbacks',0x4aea40),('flags','audio_log_level',0x43d0ce)]
   for name,symbol,address in hooks:
    target=sym[symbol] if is_c else address
    def hook(uc,pc,size,user,name=name):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     if name=='mutex':trace.append(('mutex',));uc.reg_write(UC_ARM_REG_R0,mutex)
     elif name=='zero':uc.mem_write(r0,bytes([r2&255])*r1)
     elif name=='callbacks':trace.append(('callbacks',))
     else:uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_device_manager_battery_sync_init'] if is_c else 0x4acf7c)|1,0x600000,count=5000)
   image=[]
   for name,address in native.items():image.append(bytes(u.mem_read(sym[name] if is_c else address,24 if name=='audio_charge_sync_record' else 8 if name=='audio_charge_sync_peer_record' else 4 if name=='audio_charge_sync_mutex' else 2 if 'mode' in name or 'phase' in name else 1)))
   pair.append((trace,image))
  assert pair[0]==pair[1],(mutex,pair)
print('PASS_CHARGE_BATTERY_SYNC_NATIVE 2')
