#!/usr/bin/env python3
"""Actual compiled-C/native slave security parent and Cordio child effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_slave_security.c'
STUB='''#include <stdint.h>
const uint8_t *audio_ble_comm_profile_slot;
uint8_t DmConnSecLevel(uint8_t c){(void)c;return 0;}
void *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void SmpDmMsgSend(void*p){(void)p;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_slave_security_request',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,conn,level,alloc):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  cfg=0x20084000;packet=0x20085000;u.mem_write(cfg,b'\x06');u.mem_write(packet,bytes([0xa5]*6))
  cell=sy['audio_ble_comm_profile_slot'] if compiled else 0x20074358
  u.mem_write(cell,cfg.to_bytes(4,'little'));trace=[]
  names=[('level','DmConnSecLevel',0x4b71b2),('alloc','WsfMsgAlloc',0x4bf99e),('send','SmpDmMsgSend',0x537bd6),('log','audio_log_level',0x43d0ce)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    if name=='level':trace.append(('level',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,level)
    elif name=='alloc':trace.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,packet if alloc else 0)
    elif name=='send':trace.append(('send',uc.reg_read(UC_ARM_REG_R0)==packet,bytes(uc.mem_read(packet,6))))
    else:uc.reg_write(UC_ARM_REG_R0,0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,conn);u.reg_write(UC_ARM_REG_R1,0x12345678)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_slave_security_request'] if compiled else 0x46df7e)|1,0x600000,count=3000)
  return trace,bytes(u.mem_read(packet,6)),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)
 cases=0
 for conn in (0,1,0x34,0x100,0x1234):
  for level in (0,1):
   for alloc in (0,1):
    a,b=run(False,conn,level,alloc),run(True,conn,level,alloc)
    assert a==b,(conn,level,alloc,a,b)
    cases+=1
 print('PASS_BLE_SLAVE_SECURITY_NATIVE',cases)
