#!/usr/bin/env python3
"""Actual C/native bounded primitive/default-predicate branches."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_default_predicate.c'
STUB='''#include <stdint.h>
uint32_t audio_pb_first_char_nonzero_490678(const void *p){(void)p;return 0;}
uint32_t audio_pb_iter_begin_4d94ba(void *a,const void *b,const void *c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_pb_iter_next_4d93d8(void *p){(void)p;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_field_is_default_49087a',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0x00,0,0,0,0),(0x20,0,0,0,0),(0x20,1,0,0,0),(0x10,0,0,0,0),(0x10,0,0,1,0),(0x06,0,0,0,0),(0x06,1,0,0,0),(0x07,0,0,0,0),(0x8a,0,0,0,0),(0x8a,1,0,0,0),(0x4a,0,0,0,0),(0x40,0,0,0,0)]
 for typ,value,defaultv,firstchar,marker in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   it=0x20080000;desc=0x20081000;data=0x20082000
   u.mem_write(it,bytes(40));u.mem_write(desc,bytes(24));u.mem_write(data,struct.pack('<I',value))
   u.mem_write(it,struct.pack('<I',desc));u.mem_write(it+18,struct.pack('<H',4));u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<I',data));u.mem_write(it+32,struct.pack('<I',data))
   u.mem_write(desc+8,struct.pack('<I',data if defaultv else 0));u.mem_write(desc+12,struct.pack('<I',(sy['audio_pb_default_callback_4d94e6'] if is_c else 0x4d94e7) if marker else 0))
   child=(sy['audio_pb_first_char_nonzero_490678']&~1) if is_c else 0x490678;calls=[]
   def hook(uc,pc,n,user):
    calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,firstchar);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   u.reg_write(UC_ARM_REG_R0,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_pb_field_is_default_49087a'] if is_c else 0x49087a)|1,0x600000,count=1000)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],((typ,value,defaultv,firstchar,marker),pair)
print('PASS_PB_DEFAULT_PREDICATE_NATIVE',len(cases))
