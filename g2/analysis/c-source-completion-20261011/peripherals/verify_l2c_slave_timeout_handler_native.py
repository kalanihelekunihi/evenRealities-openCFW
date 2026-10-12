#!/usr/bin/env python3
"""Actual compiled-C/native L2C slave handler and timeout effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/l2c_slave_timeout_handler.c'
STUB='''#include <stdint.h>
uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
int32_t audio_l2c_strncmp(const char*a,const char*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
void audio_ble_dm_l2c_conn_update_cnf_56e580(uint16_t a,uint16_t b){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'handler.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_handler_536fa4',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names=[('enabled','audio_ble_hci_vendor_log_enabled_4c9c50',0x4c9c50),('compare','audio_l2c_strncmp',0x44b610),('flags','audio_log_level',0x43d0ce),('log','audio_log_extended',0x43d574),('trace','audio_ble_wsf_trace',0x52a63c),('dm','audio_ble_dm_l2c_conn_update_cnf_56e580',0x56e580)]
 def run(compiled,event_type,enabled,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_write(0x20081000,bytes((0x34,0x12,event_type if event_type<256 else 1))+bytes(8))
  trace=[]
  def string(uc,p):return bytes(uc.mem_read(p,120)).split(b'\0')[0]
  for name,cname,stock in names:
   addr=(sy[cname]&~1) if compiled else stock
   def hook(uc,pc,size,user,name=name):
    a,b,c,d=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='enabled':trace.append(('enabled',));uc.reg_write(UC_ARM_REG_R0,enabled)
    elif name=='compare':
     x,y=string(uc,a),string(uc,b);trace.append(('compare',x[:c],y[:c],c));uc.reg_write(UC_ARM_REG_R0,0 if x[:c]==y[:c] else 1)
    elif name=='flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,flags)
    elif name=='log':trace.append(('log',a,string(uc,b),string(uc,c),string(uc,d)))
    elif name=='trace':trace.append(('trace',string(uc,a),string(uc,b)))
    else:trace.append(('dm',a,b))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
  ptr=0 if event_type==256 else 0x20081000
  for r,v in ((UC_ARM_REG_R0,5),(UC_ARM_REG_R1,ptr),(UC_ARM_REG_R7,0x12345678),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  entry=(sy['audio_ble_handler_536fa4']&~1) if compiled else 0x536fa4
  u.emu_start(entry|1,0x600000,count=30000)
  return u.reg_read(UC_ARM_REG_R0),trace
 cases=0
 for event in (0,1,2,256):
  for enabled in (0,1):
   for flags in (0,2):
    a=run(False,event,enabled,flags);b=run(True,event,enabled,flags)
    assert a==b,(event,enabled,flags,a,b)
    cases+=1
 print('PASS_L2C_SLAVE_TIMEOUT_HANDLER_NATIVE',cases)
