#!/usr/bin/env python3
"""Stock/C APP_MasterSetPhyEvent allocation and Cordio dispatch."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_phy_event.c'
STUB='''#include <stdint.h>
uint8_t *audio_ble_master_context;
void *audio_wsf_msg_alloc(uint16_t x){(void)x;return 0;}
void audio_wsf_msg_send(uint8_t x,void *p){(void)x;(void)p;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_master_set_phy_event_4a2254',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for allocate in (False,True):
  for level in (0,7):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    cell=sym['audio_ble_master_context'] if is_c else 0x200742fc
    ctx=0x2007f000;msg=0x2007f100;u.mem_write(cell,struct.pack('<I',ctx));u.mem_write(ctx+0x55,b'\x34\x56');u.mem_write(msg,b'\xaa'*12)
    trace=[]
    hooks=[('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e),('audio_wsf_msg_alloc',0x4bf99e),('audio_wsf_msg_send',0x4bf9ba)]
    for n,a in hooks:
     addr=sym[n] if is_c else a
     def hook(uc,address,size,data,n=n):
      r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
      if n=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
      elif n=='audio_log_extended':trace.append(('extended',r0,int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')))
      elif n=='compressed_log_output':trace.append(('compressed',r0))
      elif n=='audio_wsf_msg_alloc':trace.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,msg if allocate else 0)
      else:trace.append(('send',r0,r1,bytes(uc.mem_read(msg,12))))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0)
    u.emu_start((sym['audio_uart_ring_master_set_phy_event_4a2254'] if is_c else 0x4a2254)|1,0x600000,count=2000)
    pair.append(trace)
   assert pair[0]==pair[1],(allocate,level,pair)
 print('PASS_RING_PHY_EVENT_NATIVE',4)
