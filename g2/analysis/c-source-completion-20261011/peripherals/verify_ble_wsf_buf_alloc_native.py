#!/usr/bin/env python3
"""Native/C WSF pool class scan, free-list pop and failure diagnostics."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_wsf_buf_alloc.c'
stub='''#include <stdint.h>
void *audio_wsf_pool_list;uint8_t audio_wsf_pool_count;
__attribute__((naked)) void WsfCsEnter(void){__asm volatile("bx lr");}
__attribute__((naked)) void WsfCsExit(void){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,WsfBufAlloc',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('empty','oversize','one','second','exhausted'):
  for flags in (0,1,2):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    p=sym['audio_wsf_pool_list'] if is_c else 0x20074eec
    c=sym['audio_wsf_pool_count'] if is_c else 0x20075044
    table=0x2007f000;block=0x2007f100;nextb=0x2007f200
    u.mem_write(p,struct.pack('<I',table));u.mem_write(c,bytes((0 if mode=='empty' else 2,)))
    rows=bytearray(24);rows[0:2]=struct.pack('<H',16);rows[12:14]=struct.pack('<H',64)
    if mode=='one':rows[8:12]=struct.pack('<I',block)
    if mode=='second':rows[20:24]=struct.pack('<I',block)
    u.mem_write(table,bytes(rows));u.mem_write(block,struct.pack('<II',nextb,0xdeadbeef))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,100 if mode=='oversize' else 32 if mode=='second' else 8)
    seen=[]
    def string(uc,p):return bytes(uc.mem_read(p,130)).split(b'\0')[0]
    def hook(uc,a,size,_):
     if a in (0x52b8a4,sym['WsfCsEnter']&~1):seen.append(('enter',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x52b8b6,sym['WsfCsExit']&~1):seen.append(('exit',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x43d0ce,sym['audio_log_flags']&~1):uc.reg_write(UC_ARM_REG_R0,flags);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x43ce9e,sym['compressed_log_output']&~1):seen.append(('compact',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x43d574,sym['audio_log_extended']&~1):
      line,fmt=struct.unpack('<II',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)));seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,string(uc,fmt)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['WsfBufAlloc'] if is_c else 0x530446)|1,0x600000,count=600)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(table,24)),bytes(u.mem_read(block,8))))
   assert pair[0]==pair[1],(mode,flags,pair)
   cases+=1
 print('PASS_BLE_WSF_BUF_ALLOC_NATIVE',cases)
