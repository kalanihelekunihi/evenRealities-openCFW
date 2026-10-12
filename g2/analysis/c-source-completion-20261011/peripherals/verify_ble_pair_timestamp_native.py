#!/usr/bin/env python3
"""Native/C LRU timestamp update including overflow reset and row rewrites."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_timestamp_update.c'
S2=R/'components/audio/uart_thread_source_candidate/display_ble_pair_timestamp_reset.c'
stub='''
#include <stdint.h>
uint32_t audio_ble_pair_timestamp_counter_20074344;
uint8_t audio_ble_privacy_rows[2000];
__attribute__((naked)) uint32_t audio_ble_privacy_rewrite_record(uint8_t*p){__asm volatile("bx lr");}
__attribute__((naked)) uint8_t audio_ble_pair_record_validate(uint8_t*p){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_complete_prepare',str(S),str(S2),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  cases=0
  for counter in (0,7,0xfffffffe,0xffffffff):
    for flags in (0,1,2):
      pair=[]
      for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in seg:u.mem_write(a,d)
        cell=sym['audio_ble_pair_timestamp_counter_20074344'] if is_c else 0x20074344
        rows=sym['audio_ble_privacy_rows'] if is_c else 0x20067a30
        u.mem_write(cell,struct.pack('<I',counter))
        u.mem_write(0x20010000,b'\x77'*0xc8)
        for index in (0,3):
          u.mem_write(rows+index*200+0x2f,b'\x01\x01')
          u.mem_write(rows+index*200+0xc4,struct.pack('<I',0x98765432))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,0x20010000)
        seen=[]
        def string(uc,p):return bytes(uc.mem_read(p,180)).split(b'\0')[0]
        def hook(uc,a,size,_):
          if a in (0x43d0ce,sym['audio_log_flags']&~1):
            uc.reg_write(UC_ARM_REG_R0,flags);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          if a in (0x43ce9e,sym['compressed_log_output']&~1):
            seen.append(('compact',uc.reg_read(UC_ARM_REG_R0),string(uc,uc.reg_read(UC_ARM_REG_R1))))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          if a in (0x43d574,sym['audio_log_extended']&~1):
            line,p=struct.unpack('<II',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)))
            seen.append(('extended',uc.reg_read(UC_ARM_REG_R0),line,string(uc,p)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          if a in (0x479b74,sym['audio_ble_privacy_rewrite_record']&~1,
                   0x47b730,sym['audio_ble_pair_record_validate']&~1):
            ptr=uc.reg_read(UC_ARM_REG_R0)
            target=('record' if ptr==0x20010000 else ('row', (ptr-rows)//200))
            seen.append(('rewrite' if a in (0x479b74,sym['audio_ble_privacy_rewrite_record']&~1) else 'verify',target))
            uc.reg_write(UC_ARM_REG_R0,1)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
        u.hook_add(UC_HOOK_CODE,hook)
        u.emu_start((sym['audio_ble_pair_complete_prepare'] if is_c else 0x47c084)|1,0x600000,count=900)
        outcome=(struct.unpack('<I',bytes(u.mem_read(cell,4)))[0],
          bytes(u.mem_read(0x200100c4,4)),
          bytes(u.mem_read(rows+0xc4,4)),bytes(u.mem_read(rows+3*200+0xc4,4)),seen)
        pair.append(outcome)
      assert pair[0]==pair[1],(counter,flags,pair)
      cases+=1
  print('PASS_BLE_PAIR_TIMESTAMP_NATIVE',cases)
