#!/usr/bin/env python3
"""Compare actual compiled C/native nanopb top-level loop at real child cuts."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_parent.c'
names=['audio_pb_iter_begin_4d94ba','audio_pb_iter_next_4d93d8','audio_pb_encode_extension_490bf8','audio_pb_encode_field_490b1e']
native=[0x4d94ba,0x4d93d8,0x490bf8,0x490b1e]
STUB='''#include <stdint.h>
uint32_t audio_pb_iter_begin_4d94ba(void *a,const void *b,const void *c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_pb_iter_next_4d93d8(void *a){(void)a;return 0;}
uint32_t audio_pb_encode_extension_490bf8(void *a,void *b){(void)a;(void)b;return 0;}
uint32_t audio_pb_encode_field_490b1e(void *a,void *b){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for begin,types,fail_at in ((False,(),None),(True,(0x12,),None),(True,(0x1a,),None),(True,(0x12,),0),(True,(0x1a,),0),(True,(0x12,0x1a,0x12),None),(True,(0x12,0x1a,0x12),1),(True,(0x12,0x1a,0x12),2)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   addr=[sy[n]&~1 for n in names] if is_c else native;calls=[];state={'field':0}
   def hook(uc,pc,n,user):
    ix=addr.index(pc);r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
    if ix==0:
     calls.append(('begin',r1==0x20081000,uc.reg_read(UC_ARM_REG_R2)==0x20082000))
     if begin:uc.mem_write(r0+22,bytes([types[0]]))
     uc.reg_write(UC_ARM_REG_R0,1 if begin else 0)
    elif ix==1:
     calls.append(('next',))
     state['field']+=1
     more=state['field']<len(types)
     if more:uc.mem_write(r0+22,bytes([types[state['field']]]))
     uc.reg_write(UC_ARM_REG_R0,1 if more else 0)
    else:
     calls.append(('extension' if ix==2 else 'field',r0==0x20080000))
     uc.reg_write(UC_ARM_REG_R0,0 if fail_at==state['field'] else 1)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,0x20080000);u.reg_write(UC_ARM_REG_R1,0x20081000);u.reg_write(UC_ARM_REG_R2,0x20082000)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_pb_encode'] if is_c else 0x490c32)|1,0x600000,count=400)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(begin,types,fail_at,pair)
print('PASS_PB_ENCODE_PARENT_NATIVE 8')
