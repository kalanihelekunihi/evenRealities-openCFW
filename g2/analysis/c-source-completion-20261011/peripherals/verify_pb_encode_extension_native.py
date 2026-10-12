#!/usr/bin/env python3
"""Compiled C/native extension chain effects with child callbacks intercepted."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_extension.c'
STUB='''#include <stdint.h>
uint32_t audio_pb_encode_default_extension_490bc8(void *s,const void *e){(void)s;(void)e;return 1;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_extension_490bf8',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for count,custom,fail_at in [(0,False,-1),(1,False,-1),(1,True,-1),(3,False,-1),(3,True,1),(3,False,2)]:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   stream=0x20080000;it=0x20081000;head=0x20082000;ext=0x20083000;typ=0x20084000;callback=0x20085000
   u.mem_write(it,bytes(40));u.mem_write(it+28,struct.pack('<I',head));u.mem_write(head,struct.pack('<I',ext if count else 0))
   u.mem_write(typ,struct.pack('<II',0,callback+1 if custom else 0))
   for i in range(count):u.mem_write(ext+12*i,struct.pack('<III',typ,0,ext+12*(i+1) if i+1<count else 0))
   calls=[]
   def hook(uc,pc,n,user):
    i=(uc.reg_read(UC_ARM_REG_R1)-ext)//12
    calls.append((pc in (callback,sy['audio_pb_encode_default_extension_490bc8']&~1,0x490bc8),uc.reg_read(UC_ARM_REG_R0)==stream,i))
    uc.reg_write(UC_ARM_REG_R0,int(i!=fail_at));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in [callback,sy['audio_pb_encode_default_extension_490bc8']&~1,0x490bc8]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_pb_encode_extension_490bf8'] if is_c else 0x490bf8)|1,0x600000,count=1000)
   pair.append(([(x[1],x[2]) for x in calls],u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(count,custom,fail_at,pair)
print('PASS_PB_ENCODE_EXTENSION_NATIVE 6')
