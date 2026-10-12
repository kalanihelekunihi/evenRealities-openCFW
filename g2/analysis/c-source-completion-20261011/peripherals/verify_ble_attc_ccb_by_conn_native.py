#!/usr/bin/env python3
"""Compare client CCB lookup, row offsets, and invalid diagnostics."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_attc_ccb_by_conn.c'
STUB='''#include <stdint.h>
volatile uint8_t audio_ble_trace_level_cell;uint8_t audio_ble_attc_state[0x400];
uint8_t audio_ble_connection_record_active(uint8_t c){(void)c;return 0;}
int32_t audio_ble_hci_vendor_compare_44b610(const void*a,const void*b,uint32_t n){const uint8_t*x=a,*y=b;for(uint32_t i=0;i<n;i++){if(x[i]!=y[i])return x[i]<y[i]?-1:1;if(x[i]==0)return 0;}return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
cases=[(0,0,0,0,0),(0,2,0,1,2),(1,0,0,0,0),(1,2,0,1,2),(1,0,1,0,0),(2,2,1,1,0)]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_attc_ccb_by_conn_id_531820',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for conn,slot,active,flag,logflags in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   trace=[];cell=sym['audio_ble_trace_level_cell'] if compiled else 0x2007502f;u.mem_write(cell,bytes([flag]))
   for name,cs,stock in (('active','audio_ble_connection_record_active',0x4b6ec6),('flags','audio_log_flags',0x43d0ce),('extended','audio_log_extended',0x43d574),('wsf','audio_ble_wsf_trace',0x52a63c)):
    target=sym[cs] if compiled else stock
    def hook(uc,pc,size,user,name=name):
     if name=='active':trace.append((name,uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,active)
     elif name=='flags':uc.reg_write(UC_ARM_REG_R0,logflags)
     elif name=='extended':trace.append((name,uc.reg_read(UC_ARM_REG_R0)))
     else:trace.append((name,))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,conn);u.reg_write(UC_ARM_REG_R1,slot);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_attc_ccb_by_conn_id_531820'] if compiled else 0x531820)|1,0x600000,count=3000)
   result=u.reg_read(UC_ARM_REG_R0);base=sym['audio_ble_attc_state'] if compiled else 0x2006f904
   pair.append((result-base if result else None,trace))
  assert pair[0]==pair[1],((conn,slot,active,flag,logflags),pair)
print('PASS_BLE_ATTC_CCB_BY_CONN_NATIVE',len(cases))
