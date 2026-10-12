#!/usr/bin/env python3
"""Compare compiled C/stock Cordio discovery step and database hash branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
S=[D/'display_ble_service_discovery_step.c',D/'display_ble_service_database_hash.c',D/'display_ble_service_discovery_start.c']
STUB='''#include <stdint.h>
volatile uint8_t audio_ble_trace_level_cell;uint8_t audio_ble_subsystem_rows_200733fc[32];uintptr_t audio_ble_service_dispatch_20074348;
uint8_t *audio_ble_pair_record(uint8_t x){(void)x;return 0;}void *audio_queue_copy_bytes(void*a,const void*b,uint32_t n){(void)b;(void)n;return a;}
uint32_t audio_log_flags(void){return 0;}void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}void audio_ble_attc_read_by_type_56c4ee(uint8_t a,uint16_t b,uint16_t c,uint8_t d,const uint8_t*e,uint32_t f){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void callback(uint8_t a,uint8_t b){(void)a;(void)b;}
'''
cases=[('step',0,0,0,0,0),('step',0,1,0,0,2),('step',1,0,3,0,0),('step',1,0,8,0,0),('step',1,0,8,1,0),('step',1,0,9,0,0),('hash',0,0,0,0,0),('hash',0,1,0,0,2),('hash',1,0,0,0,0),('hash',1,1,0,0,0)]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_service_discovery_start',*map(str,S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind,connection,state,status,field8,logflags in cases:
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   row=sym['audio_ble_subsystem_rows_200733fc'] if compiled else 0x200733fc
   data=bytearray(16);data[11]=state;data[8]=field8;u.mem_write(row,bytes(data))
   u.mem_write(sym['audio_ble_trace_level_cell'] if compiled else 0x2007502f,bytes([state]))
   cb=sym['callback'] if compiled else 0x100500
   u.mem_write(sym['audio_ble_service_dispatch_20074348'] if compiled else 0x20074348,struct.pack('<I',cb|1))
   trace=[]
   for name,cs,stock in (('callback','callback',0x100500),('read','audio_ble_attc_read_by_type_56c4ee',0x56c4ee),('flags','audio_log_flags',0x43d0ce),('extended','audio_log_extended',0x43d574),('wsf','audio_ble_wsf_trace',0x52a63c)):
    target=sym[cs] if compiled else stock
    def hook(uc,pc,size,user,name=name):
     if name=='callback':trace.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     elif name=='read':
      ptr=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
      trace.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),bytes(uc.mem_read(ptr,2))))
     elif name=='flags':uc.reg_write(UC_ARM_REG_R0,logflags)
     elif name=='extended':trace.append((name,uc.reg_read(UC_ARM_REG_R0)))
     else:trace.append((name,))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,connection);u.reg_write(UC_ARM_REG_R1,status);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   c='audio_ble_service_discovery_step_531bd4' if kind=='step' else 'audio_ble_service_discovery_followup_5336e0'
   stock=0x531bd4 if kind=='step' else 0x5336e0
   u.emu_start((sym[c] if compiled else stock)|1,0x600000,count=3000)
   pair.append((trace,bytes(u.mem_read(row,16))))
  assert pair[0]==pair[1],((kind,connection,state,status,field8,logflags),pair)
print('PASS_BLE_SERVICE_DISCOVERY_CHILDREN_NATIVE',len(cases))
