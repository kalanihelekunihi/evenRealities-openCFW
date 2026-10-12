#!/usr/bin/env python3
"""Actual C/native connection-open pointer and diagnostics comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_app_slave_conn_open.c'
STUB='''#include <stdint.h>
uint8_t *audio_ble_dm_conn_cell,*audio_ble_profile_connection_context;
uint8_t audio_ble_discovery_connection_records_200717b0[0x90];
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t l,const char *m,const char *s,const char *f,uint32_t n,const char *t,...){(void)l;(void)m;(void)s;(void)f;(void)n;(void)t;}
uint32_t compressed_log_output(uint32_t n,const char *a,const char *b,...){(void)n;(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,appSlaveConnOpen',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for connection,flags in ((1,0),(2,2),(3,1),(1,4)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cell=sy['audio_ble_dm_conn_cell'] if is_c else 0x20074328
   rows=sy['audio_ble_discovery_connection_records_200717b0'] if is_c else 0x200717b0
   context=sy['audio_ble_profile_connection_context'] if is_c else 0x2007432c
   state=0x20080100;u.mem_write(context,state.to_bytes(4,'little'));u.mem_write(state,bytes([0]*0x80))
   msg=0x20080000;u.mem_write(msg,connection.to_bytes(2,'little')+bytes([0]*10))
   flag=(sy['audio_log_flags']&~1) if is_c else 0x43d0ce
   log=(sy['audio_log_extended']&~1) if is_c else 0x43d574
   compact=(sy['compressed_log_output']&~1) if is_c else 0x43ce9e
   calls=[]
   def hook(uc,pc,n,user):
    if pc==flag:uc.reg_write(UC_ARM_REG_R0,flags)
    elif pc==log:calls.append(('log',uc.reg_read(UC_ARM_REG_R0)&255))
    else:calls.append(('compact',uc.reg_read(UC_ARM_REG_R0)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in (flag,log,compact):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,msg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['appSlaveConnOpen'] if is_c else 0x46de78)|1,0x600000,count=1000)
   value=int.from_bytes(u.mem_read(cell,4),'little')-rows
   pair.append((value,bytes(u.mem_read(state+0x54,1)),calls))
  assert pair[0]==pair[1],(connection,flags,pair)
print('PASS_BLE_APP_SLAVE_CONN_OPEN_NATIVE 4')
