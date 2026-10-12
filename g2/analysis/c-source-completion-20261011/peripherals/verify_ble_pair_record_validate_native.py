#!/usr/bin/env python3
"""Native/C MRAM record verification over matching, mismatch, key and log cases."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_pair_record_validate.c'
stub='''
#include <stdint.h>
const uint8_t audio_ble_mram_records_7ff000[2560];
__attribute__((naked)) void audio_ble_privacy_cache_maintenance(const void*a,uint8_t b){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_ble_privacy_compare_address(const uint8_t*a,const uint8_t*b){__asm volatile("bx lr");}
__attribute__((naked)) int32_t g2_lfs_memcmp(const void*a,const void*b,uint32_t n){__asm volatile("bx lr");}
__attribute__((naked)) void audio_dump_hex(const char*a,uint32_t b,const uint8_t*c,uint32_t d){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_log_flags(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
  mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
  subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                  '-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_pair_record_validate',str(S),str(mock),'-o',str(elf)],check=True)
  with elf.open('rb') as f:
    x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD']
    sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
  scenarios=[]
  for match in (False,True):
    for mismatch in ('none','valid','inuse','mask','ltk','irk','csrk'):
      if match or mismatch=='none':scenarios.append((match,mismatch))
  cases=0
  for match,mismatch in scenarios:
    for flags in (0,1,2):
      pair=[]
      for is_c in (False,True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B)
        u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
        for a,d in seg:u.mem_write(a,d)
        base=sym['audio_ble_mram_records_7ff000'] if is_c else 0x7ff000
        ram=bytearray(0xc8);ram[:6]=b'ABCDEF';ram[6]=1;ram[0x2e]=0x0d
        ram[0x2f]=1;ram[0x30]=1
        ram[7:23]=b'I'*16;ram[0x1e:0x2e]=b'C'*16;ram[0x34:0x44]=b'L'*16
        rows=bytearray(2560)
        row=bytearray(ram[:256]);row.extend(b'\0'*(256-len(row)))
        if match:rows[2*256:3*256]=row
        if mismatch=='valid':rows[2*256+0x30]=0
        if mismatch=='inuse':rows[2*256+0x2f]=0
        if mismatch=='mask':rows[2*256+0x2e]=0
        if mismatch=='ltk':rows[2*256+0x34]=ord('X')
        if mismatch=='irk':rows[2*256+7]=ord('X')
        if mismatch=='csrk':rows[2*256+0x1e]=ord('X')
        u.mem_write(0x20010000,bytes(ram));u.mem_write(base,bytes(rows))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20010000)
        seen=[]
        def string(uc,p):return bytes(uc.mem_read(p,180)).split(b'\0')[0]
        def hook(uc,a,size,_):
          if a in (0x43d0ce,sym['audio_log_flags']&~1):
            uc.reg_write(UC_ARM_REG_R0,flags)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
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
          if a in (0x4d294a,sym['audio_ble_privacy_compare_address']&~1):
            ptr=uc.reg_read(UC_ARM_REG_R1)
            index=(ptr-base)//256
            seen.append(('address',index))
            ok=bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),6))==bytes(uc.mem_read(ptr,6))
            uc.reg_write(UC_ARM_REG_R0,int(ok))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          if a in (0x4751c8,sym['g2_lfs_memcmp']&~1):
            ptr=uc.reg_read(UC_ARM_REG_R0);offset=ptr-0x20010000
            n=uc.reg_read(UC_ARM_REG_R2)
            seen.append(('compare',offset,n))
            ok=bytes(uc.mem_read(ptr,n))==bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),n))
            uc.reg_write(UC_ARM_REG_R0,0 if ok else 1)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
          if a in (0x43dacc,sym['audio_dump_hex']&~1):
            seen.append(('hex',string(uc,uc.reg_read(UC_ARM_REG_R0)),
                         bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R2),16))))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
        u.hook_add(UC_HOOK_CODE,hook)
        u.emu_start((sym['audio_ble_pair_record_validate'] if is_c else 0x47b730)|1,0x600000,count=1400)
        pair.append((u.reg_read(UC_ARM_REG_R0)&255,seen))
      assert pair[0]==pair[1],(match,mismatch,flags,pair)
      cases+=1
  print('PASS_BLE_PAIR_RECORD_VALIDATE_NATIVE',cases)
