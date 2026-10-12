#!/usr/bin/env python3
"""Bounded native/C effects for NVM status and pairing-failure record clear."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_failure_children.c'
stub='''
#include <stdint.h>
uint8_t mock_record[256];
const uint8_t audio_ble_mram_records_7ff000[2560];
__attribute__((naked)) void audio_ble_privacy_cache_maintenance(const void*a,uint8_t b){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t *audio_ble_pair_record(uint8_t c){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t audio_ble_remove_pair(uint8_t t,const uint8_t *r){__asm volatile("bx lr");}
__attribute__((naked)) void audio_ble_pair_storage_refresh(void){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_failure_prepare',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for kind in ('prepare','clear'):
  for mode in (('empty','one','all') if kind=='prepare' else ('none','invalid','valid_fail','valid_success')):
   for flags in (0,1,2):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     base=sym['audio_ble_mram_records_7ff000'] if is_c else 0x7ff000
     record=sym['mock_record'] if is_c else 0x20070000
     rows=bytearray(2560)
     for i in (range(10) if mode=='all' else (range(1) if mode=='one' else ())):
      off=i*256;rows[off:off+6]=bytes((1,2,3,4,5,6));rows[off+0x2e:off+0x31]=bytes((5,1,1))
     u.mem_write(base,bytes(rows));rec=bytearray(256);rec[:7]=bytes((1,2,3,4,5,6,1));rec[0x2e]=1 if mode.startswith('valid') else 0;rec[0x2f]=rec[0x30]=1;u.mem_write(record,bytes(rec))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,2)
     seen=[]
     def string(uc,p):return bytes(uc.mem_read(p,230)).split(b'\0')[0]
     def hook(uc,a,size,_):
      if a in (0x43d0ce,sym['audio_log_flags']&~1):uc.reg_write(UC_ARM_REG_R0,flags);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x43ce9e,sym['compressed_log_output']&~1):seen.append(('compact',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x43d574,sym['audio_log_extended']&~1):
       line,p=struct.unpack('<II',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)));seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,string(uc,p)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x475014,sym['audio_ble_privacy_cache_maintenance']&~1):seen.append(('cache',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x4bb07c,sym['audio_ble_pair_record']&~1):seen.append(('lookup',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0 if mode=='none' else record);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x47b59c,sym['audio_ble_remove_pair']&~1):seen.append(('remove',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)-record));uc.reg_write(UC_ARM_REG_R0,1 if mode=='valid_success' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x4b4720,sym['audio_ble_pair_storage_refresh']&~1):seen.append(('refresh',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['audio_ble_pair_failure_prepare' if kind=='prepare' else 'audio_ble_pair_failure_clear'] if is_c else (0x47c2bc if kind=='prepare' else 0x47c8cc))|1,0x600000,count=3500)
     pair.append((seen,bytes(u.mem_read(record,256))))
    assert pair[0]==pair[1],(kind,mode,flags,pair)
    cases+=1
 print('PASS_BLE_PAIR_FAILURE_CHILDREN_NATIVE',cases)
