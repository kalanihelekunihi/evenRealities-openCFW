#!/usr/bin/env python3
"""Compare the compiled C and stock discovery enqueue effects, logs disabled."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_service_discovery_enqueue.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_discovery_handler_id_20074f8a=9;
void audio_event_loop_remove_delayed(void (*f)(void)){(void)f;}
uint8_t *audio_ble_pair_record(uint8_t n){(void)n;return 0;}
void audio_ble_pair_record_clear_a(uint8_t *p,uint8_t f){(void)p;(void)f;}
void audio_ble_pair_record_clear_b(uint8_t *p,uint8_t f){(void)p;(void)f;}
uint8_t *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void WsfMsgSend(uint8_t h,void *m){(void)h;(void)m;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_comm_disconnect_delayed',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD']
  sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names=['audio_event_loop_remove_delayed','audio_log_flags','audio_ble_pair_record','audio_ble_pair_record_clear_a','audio_ble_pair_record_clear_b','WsfMsgAlloc','WsfMsgSend','audio_log_extended','compressed_log_output']
 native=[0x476ace,0x43d0ce,0x4bb07c,0x47b488,0x47b3cc,0x4bf99e,0x4bf9ba,0x43d574,0x43ce9e]
 for has_record in (False,True):
  for alloc in (False,True):
   for flags in (0,1,2,4):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
     u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     cell=sy['audio_ble_discovery_handler_id_20074f8a'] if is_c else 0x20074f8a
     u.mem_write(cell,b'\x09');u.mem_write(0x20080000,bytes(16));u.mem_write(0x20080100,bytes(16))
     addr=[sy[n]&~1 for n in names] if is_c else native
     calls=[]
     def hook(uc,pc,n,user):
      ix=addr.index(pc);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);sp=uc.reg_read(UC_ARM_REG_SP)
      word=lambda off:int.from_bytes(uc.mem_read(sp+off,4),'little')
      if ix==0:calls.append(('remove',bool(r0)))
      elif ix==1:uc.reg_write(UC_ARM_REG_R0,flags)
      elif ix==2:uc.reg_write(UC_ARM_REG_R0,0x20080100 if has_record else 0);calls.append(('lookup',r0&255))
      elif ix in (3,4):calls.append((names[ix],r0==0x20080100,r1&255))
      elif ix==5:uc.reg_write(UC_ARM_REG_R0,0x20080000 if alloc else 0);calls.append(('alloc',r0))
      elif ix==6:calls.append(('send',r0&255,r1==0x20080000))
      elif ix==7:
       line=word(0);calls.append(('log',line,word(8)&255 if line==0xd9 else None,word(12) if line==0xd9 else None,word(16)&255 if line==0xd9 else None))
      else:
       calls.append(('compact',r0,uc.reg_read(UC_ARM_REG_R3)&255 if r0==0x10c00000 else None,word(0) if r0==0x10c00000 else None,word(4)&255 if r0==0x10c00000 else None))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
     u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R4,0x11223344);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.emu_start((sy['audio_ble_comm_disconnect_delayed'] if is_c else 0x5354c2)|1,0x600000,count=2000)
     pair.append((calls,bytes(u.mem_read(0x20080000,3))))
    assert pair[0]==pair[1],(has_record,alloc,flags,pair)
print('PASS_BLE_SERVICE_DISCOVERY_ENQUEUE_NATIVE 16 INCLUDING_LOGS')
