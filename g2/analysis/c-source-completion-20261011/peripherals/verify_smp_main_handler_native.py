#!/usr/bin/env python3
"""Actual compiled-C/native SmpHandler 0x537d0c branch and queue effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/smp_main_handler.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_stack_state_20072cb8[0x50];
void SmpDbService(void){} void WsfBufFree(void*a){(void)a;}
uint8_t *smpCcbByConnId(uint8_t a){(void)a;return 0;}
void smpSmExecute(uint8_t*a,const uint8_t*b){(void)a;(void)b;}
void *audio_ble_wsf_message_dequeue(void*a,uint8_t*b){(void)a;(void)b;return 0;}
void audio_ble_wsf_message_free(void*a){(void)a;}
uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void){return 0;}
int32_t audio_l2c_strncmp(const char*a,const char*b,uint32_t n){(void)a;(void)b;(void)n;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'smp.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_smp_handler_537d0c',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names=[('service','SmpDbService',0x542960),('buf_free','WsfBufFree',0x5304d4),('ccb','smpCcbByConnId',0x5375fc),('sm','smpSmExecute',0x56ee62),('deq','audio_ble_wsf_message_dequeue',0x4bf9ec),('msg_free','audio_ble_wsf_message_free',0x4bf9b0),('enabled','audio_ble_hci_vendor_log_enabled_4c9c50',0x4c9c50),('compare','audio_l2c_strncmp',0x44b610),('flags','audio_log_level',0x43d0ce),('log','audio_log_extended',0x43d574),('trace','audio_ble_wsf_trace',0x52a63c)]
 def run(compiled,event_type,active,mismatch,enabled,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  event=0x20081000;ccb=0x20082000;msg=0x20083000
  q=(sy['audio_ble_stack_state_20072cb8']+0x20) if compiled else 0x20072cd8
  u.mem_write(q,bytes(24));u.mem_write(ccb,bytes(0x3d)+bytes((active,))+bytes(3)+bytes((7 if mismatch else 9,))+bytes(8))
  e=bytearray(16);e[0]=3;e[2]=event_type if event_type<256 else 0;e[3]=9;e[8:12]=struct.pack('<I',msg);u.mem_write(event,bytes(e))
  trace=[];deqs=0
  def string(uc,p):return bytes(uc.mem_read(p,120)).split(b'\0')[0]
  for name,cname,stock in names:
   addr=(sy[cname]&~1) if compiled else stock
   def hook(uc,pc,size,user,name=name):
    nonlocal deqs
    a,b,c,d=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='service':trace.append(('service',))
    elif name=='buf_free':trace.append(('buf_free',a))
    elif name=='ccb':trace.append(('ccb',a));uc.reg_write(UC_ARM_REG_R0,ccb)
    elif name=='sm':trace.append(('sm',a==ccb,b==event))
    elif name=='deq':
     trace.append(('deq',a==q));deqs+=1;uc.reg_write(UC_ARM_REG_R0,msg if deqs==1 else 0)
    elif name=='msg_free':trace.append(('msg_free',a==msg))
    elif name=='enabled':trace.append(('enabled',));uc.reg_write(UC_ARM_REG_R0,enabled)
    elif name=='compare':
     x,y=string(uc,a),string(uc,b);trace.append(('compare',x[:c],y[:c],c));uc.reg_write(UC_ARM_REG_R0,0 if x[:c]==y[:c] else 1)
    elif name=='flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,flags)
    elif name=='log':trace.append(('log',a,string(uc,b),string(uc,c),string(uc,d)))
    else:trace.append(('trace',string(uc,a),string(uc,b),c,d))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
  for r,v in ((UC_ARM_REG_R0,5),(UC_ARM_REG_R1,0 if event_type==256 else event),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  entry=(sy['audio_ble_smp_handler_537d0c']&~1) if compiled else 0x537d0c
  u.emu_start(entry|1,0x600000,count=30000)
  return trace
 cases=0
 for event in (0x20,0x1c,0x0b,0x01,256):
  for active,mismatch,enabled,flags in ((0,0,0,0),(1,0,0,0),(1,1,0,0),(1,1,1,0),(1,1,1,2)):
   a=run(False,event,active,mismatch,enabled,flags);b=run(True,event,active,mismatch,enabled,flags)
   assert a==b,(event,active,mismatch,enabled,flags,a,b)
   cases+=1
 print('PASS_SMP_MAIN_HANDLER_NATIVE',cases)
