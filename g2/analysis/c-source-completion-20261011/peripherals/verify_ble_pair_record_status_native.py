#!/usr/bin/env python3
"""Native/C complete ten-slot MRAM status reporter with all logger gates."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_record_status.c'
stub='''
#include <stdint.h>
const uint8_t audio_ble_mram_records_7ff000[2560];
uint32_t audio_ble_pair_timestamp_counter_20074344;
__attribute__((naked)) void audio_ble_privacy_cache_maintenance(const void*a,uint8_t b){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_complete_commit',str(S),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  cases=0
  for layout in ((),((0,1),),((0,1),(2,20),(5,5)),tuple((i,i+1) for i in range(10))):
    for flags in (0,1,2):
      pair=[]
      for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in seg:u.mem_write(a,d)
        base=sym['audio_ble_mram_records_7ff000'] if is_c else 0x7ff000
        counter=sym['audio_ble_pair_timestamp_counter_20074344'] if is_c else 0x20074344
        u.mem_write(counter,struct.pack('<I',50))
        rows=bytearray(2560)
        for i,t in layout:
          rows[i*256:i*256+7]=bytes((1,2,3,4,5,6,1))
          rows[i*256+0x2e:i*256+0x31]=b'\x0d\x01\x01'
          rows[i*256+0xc4:i*256+0xc8]=struct.pack('<I',t)
        rows[7*256+0x2f]=1 if len(layout)<10 else rows[7*256+0x2f]
        u.mem_write(base,bytes(rows))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        seen=[]
        def string(uc,p):return bytes(uc.mem_read(p,190)).split(b'\0')[0]
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
          if a in (0x475014,sym['audio_ble_privacy_cache_maintenance']&~1):
            seen.append(('cache',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
        u.hook_add(UC_HOOK_CODE,hook)
        u.emu_start((sym['audio_ble_pair_complete_commit'] if is_c else 0x47bc30)|1,0x600000,count=1700)
        pair.append(seen)
      assert pair[0]==pair[1],(layout,flags,pair)
      cases+=1
  print('PASS_BLE_PAIR_RECORD_STATUS_NATIVE',cases)
