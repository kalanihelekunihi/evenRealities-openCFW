#!/usr/bin/env python3
"""Actual compiled C/native nanopb iterator begin and next bounded effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_iter_begin_next.c'
names=['audio_uart_buffer_zero','audio_pb_iter_decode_field_4d916e','audio_pb_iter_advance_4d930a']
native=[0x43c0e4,0x4d916e,0x4d930a]
STUB='''#include <stdint.h>
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
uint32_t audio_pb_iter_decode_field_4d916e(void *p){(void)p;return 0;}
void audio_pb_iter_advance_4d930a(void *p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_iter_begin_4d94ba',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for entry,decode,index in (('audio_pb_iter_begin_4d94ba',0,0),('audio_pb_iter_begin_4d94ba',1,1),('audio_pb_iter_next_4d93d8',0,0),('audio_pb_iter_next_4d93d8',1,1)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   it=0x20080000;u.mem_write(it,b'\xcc'*40)
   addr=[sy[n]&~1 for n in names] if is_c else native;calls=[]
   def hook(uc,pc,n,user):
    ix=addr.index(pc);r0=uc.reg_read(UC_ARM_REG_R0)
    if ix==0:
     calls.append(('zero',r0==it,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
     uc.mem_write(r0,bytes(40))
    elif ix==1:calls.append(('decode',r0==it));uc.reg_write(UC_ARM_REG_R0,decode)
    else:calls.append(('advance',r0==it));uc.mem_write(r0+8,index.to_bytes(2,'little'))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,it);u.reg_write(UC_ARM_REG_R1,0x20081000);u.reg_write(UC_ARM_REG_R2,0x20082000)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   entry_addr=(sy[entry] if is_c else (0x4d94ba if entry=='audio_pb_iter_begin_4d94ba' else 0x4d93d8))
   u.emu_start(entry_addr|1,0x600000,count=300)
   pair.append((calls,bytes(u.mem_read(it,40)),u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(entry,decode,index,pair)
print('PASS_PB_ITER_BEGIN_NEXT_NATIVE 4')
