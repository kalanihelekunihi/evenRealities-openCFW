#!/usr/bin/env python3
"""Actual C/native field-dispatch branch effects with encoder children cut."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_field.c'
N=['audio_pb_field_is_default_49087a','audio_pb_first_char_nonzero_490678','audio_pb_encode_callback_490aea','audio_pb_encode_repeated_490690','audio_pb_encode_single_490a46']
A=[0x49087a,0x490678,0x490aea,0x490690,0x490a46]
STUB='''#include <stdint.h>
uint32_t audio_pb_field_is_default_49087a(const void *p){(void)p;return 0;}
uint32_t audio_pb_first_char_nonzero_490678(const void *p){(void)p;return 0;}
uint32_t audio_pb_encode_callback_490aea(void *s,const void *p){(void)s;(void)p;return 1;}
uint32_t audio_pb_encode_repeated_490690(void *s,const void *p){(void)s;(void)p;return 1;}
uint32_t audio_pb_encode_single_490a46(void *s,const void *p){(void)s;(void)p;return 1;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_field_490b1e',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0x00,0,0,0,0,1),(0x10,1,0,1,0,1),(0x10,1,0,0,0,1),(0x10,1,1,1,0,1),(0x30,1,1,1,0,1),(0x30,1,1,1,1,1),(0x20,1,1,1,0,0),(0x40,1,1,1,0,1),(0x00,1,1,1,0,1),(0x00,1,1,1,0,0)]
 for typ,size,data,child_result,oneof,errmsg_existing in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   stream=0x20080000;it=0x20081000;sz=0x20082000
   u.mem_write(stream,bytes(20));u.mem_write(it,bytes(40));u.mem_write(sz,struct.pack('<H',2 if oneof else 1))
   u.mem_write(it+16,struct.pack('<H',1));u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<I',sz if data else 0));u.mem_write(it+32,struct.pack('<I',sz if size else 0))
   if errmsg_existing:u.mem_write(stream+16,struct.pack('<I',0x779fc4))
   addr=[sy[x]&~1 for x in N] if is_c else A;calls=[]
   def hook(uc,pc,n,user):
    ix=addr.index(pc);calls.append(ix)
    uc.reg_write(UC_ARM_REG_R0,child_result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_pb_encode_field_490b1e'] if is_c else 0x490b1e)|1,0x600000,count=1000)
   ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0]
   err=bytes(u.mem_read(ptr,22)).split(b'\0')[0] if ptr else b''
   pair.append((calls,u.reg_read(UC_ARM_REG_R0),err))
  assert pair[0]==pair[1],((typ,size,data,child_result,oneof,errmsg_existing),pair)
print('PASS_PB_ENCODE_FIELD_NATIVE',len(cases))
