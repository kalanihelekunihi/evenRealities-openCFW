#!/usr/bin/env python3
"""Actual compiled-C/native legacy mode callback and warning effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_slave_adv_mode.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_subsystem_link_state_200719c8[0x80];
volatile uint8_t audio_ble_trace_level_cell;
void appSlaveLegAdvStop(void *e){(void)e;}
void appSlaveLegAdvRestart(void *e){(void)e;}
int32_t audio_ble_hci_vendor_compare_44b610(const void *a,const void *b,uint32_t n){const uint8_t *p=a,*q=b;for(;n;n--,p++,q++){if(*p!=*q)return *p<*q?-1:1;if(!*p)return 0;}return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t l,const char *a,const char *b,const char *c,uint32_t d,const char *e,...){(void)l;(void)a;(void)b;(void)c;(void)d;(void)e;}
void audio_ble_wsf_trace(const char *a,const char *b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSlaveAdvMode',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for mode,trace,flags in (('init',0,0),('same',0,0),('invalid',0,0),('invalid',1,0),('invalid',1,2)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   state=sy['audio_ble_subsystem_link_state_200719c8'] if is_c else 0x200719c8
   trace_cell=sy['audio_ble_trace_level_cell'] if is_c else 0x2007502f
   u.mem_write(trace_cell,bytes([trace]));stop=(sy['appSlaveLegAdvStop'] if is_c else 0x4b2aff)
   init=0 if mode=='init' else stop if mode=='same' else 0x12345679
   u.mem_write(state+0x78,init.to_bytes(4,'little'));u.mem_write(state+0x7c,(0).to_bytes(4,'little'))
   log=(sy['audio_log_extended']&~1) if is_c else 0x43d574
   wsf=(sy['audio_ble_wsf_trace']&~1) if is_c else 0x52a63c
   flag=(sy['audio_log_flags']&~1) if is_c else 0x43d0ce
   calls=[]
   def hook(uc,pc,n,user):
    if pc==flag:uc.reg_write(UC_ARM_REG_R0,flags)
    elif pc==log:calls.append(('log',uc.reg_read(UC_ARM_REG_R0)&255))
    else:
     ptr=uc.reg_read(UC_ARM_REG_R1);msg=bytes(uc.mem_read(ptr,80)).split(b'\0')[0]
     calls.append(('trace',msg))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for addr in (flag,log,wsf):u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appSlaveAdvMode'] if is_c else 0x4b2bde)|1,0x600000,count=2000)
   raw=bytes(u.mem_read(state+0x78,8))
   callbacks=(int.from_bytes(raw[:4],'little')==stop,int.from_bytes(raw[4:],'little')==(sy['appSlaveLegAdvRestart'] if is_c else 0x4b2b91))
   pair.append((u.reg_read(UC_ARM_REG_R0)&255,callbacks,calls))
  assert pair[0]==pair[1],(mode,trace,flags,pair)
print('PASS_BLE_APP_SLAVE_ADV_MODE_NATIVE 5')
