#!/usr/bin/env python3
"""Actual compiled C/native direct protobuf BLE send and OTA gate."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_notify_direct.c'
STUB='''#include <stdint.h>
uint32_t audio_ota_transfer_active(void){return 0;}
uint32_t audio_ble_msg_tx(uint8_t a,uint8_t b,uint8_t c,uint8_t d,const void *p,uint16_t n){(void)a;(void)b;(void)c;(void)d;(void)p;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,...){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_notify_direct_475aa6',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names=['audio_ota_transfer_active','audio_ble_msg_tx','audio_log_flags','audio_log_extended','compressed_log_output']
 native=[0x4487ac,0x47564e,0x43d0ce,0x43d574,0x43ce9e]
 for ota in (False,True):
  for flags in (0,1,2,4):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    addr=[sy[n]&~1 for n in names] if is_c else native;calls=[]
    def hook(uc,pc,n,user):
     ix=addr.index(pc);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3);sp=uc.reg_read(UC_ARM_REG_SP)
     if ix==0:uc.reg_write(UC_ARM_REG_R0,1 if ota else 0)
     elif ix==1:
      calls.append(('send',r0,r1,r2,r3,int.from_bytes(uc.mem_read(sp,4),'little')==0x20080000,int.from_bytes(uc.mem_read(sp+4,4),'little')&0xffff));uc.reg_write(UC_ARM_REG_R0,0x1234)
     elif ix==2:uc.reg_write(UC_ARM_REG_R0,flags)
     elif ix==3:calls.append(('log',r0&255,int.from_bytes(uc.mem_read(sp,4),'little')))
     else:calls.append(('compact',r0))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
    u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_R1,0x80);u.reg_write(UC_ARM_REG_R2,0x20080000);u.reg_write(UC_ARM_REG_R3,0x12345);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['audio_ble_notify_direct_475aa6'] if is_c else 0x475aa6)|1,0x600000,count=500)
    pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(ota,flags,pair)
print('PASS_BLE_NOTIFY_DIRECT_NATIVE 8')
