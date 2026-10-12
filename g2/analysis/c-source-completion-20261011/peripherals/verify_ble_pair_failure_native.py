#!/usr/bin/env python3
"""Compare compiled pairing-failure parent against native, intercepting direct children."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_failure.c'
stub='''
#include <stdint.h>
uint8_t mock_record[256];
__attribute__((naked)) void audio_ble_pair_failure_prepare(void){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t *audio_ble_pair_record(uint8_t c){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_pair_failure_clear(uint8_t c){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_failure',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for record_case in ('none','invalid','valid'):
  for status in (1,3,4,11,7):
   for flags in (0,1,2):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     rec=sym['mock_record'] if is_c else 0x20070000
     data=bytearray(256);data[:6]=bytes((1,2,3,4,5,6));data[0x2e]=1 if record_case=='valid' else 0;data[0x2f]=1;data[0x30]=1 if record_case!='none' else 0
     u.mem_write(rec,bytes(data));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,2);u.reg_write(UC_ARM_REG_R1,status)
     seen=[]
     def string(uc,p):return bytes(uc.mem_read(p,220)).split(b'\0')[0]
     def hook(uc,a,size,_):
      if a in (0x43d0ce,sym['audio_log_flags']&~1):uc.reg_write(UC_ARM_REG_R0,flags);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x43ce9e,sym['compressed_log_output']&~1):seen.append(('compact',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x43d574,sym['audio_log_extended']&~1):
       line,p=struct.unpack('<II',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)));seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,string(uc,p)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x47c2bc,sym['audio_ble_pair_failure_prepare']&~1):seen.append(('prepare',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x4bb07c,sym['audio_ble_pair_record']&~1):seen.append(('lookup',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0 if record_case=='none' else rec);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x47c8cc,sym['audio_ble_pair_failure_clear']&~1):seen.append(('clear',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['audio_ble_pair_failure'] if is_c else 0x47c568)|1,0x600000,count=1500)
     pair.append((seen,bytes(u.mem_read(rec,256))))
    assert pair[0]==pair[1],(record_case,status,flags,pair)
    cases+=1
 print('PASS_BLE_PAIR_FAILURE_NATIVE',cases)
