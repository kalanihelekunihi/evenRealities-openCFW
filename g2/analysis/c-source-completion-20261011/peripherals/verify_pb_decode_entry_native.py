#!/usr/bin/env python3
"""Actual C/native protobuf decode entry flags and return masking."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_entry.c'
STUB='unsigned audio_pb_decode_parent_48fe98(void *a,const void*b,void*c,unsigned d){(void)a;(void)b;(void)c;(void)d;return 0;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_pb_decode',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for result in (0,1,0x1234):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   child=(sy['audio_pb_decode_parent_48fe98']&~1) if is_c else 0x48fe98;calls=[]
   def hook(uc,pc,n,user):
    calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
    uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=child,end=child)
   for reg,val in ((UC_ARM_REG_R0,0x20080000),(UC_ARM_REG_R1,0x20081000),(UC_ARM_REG_R2,0x20082000),(UC_ARM_REG_R3,0xdeadbeef),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
   u.emu_start((sy['audio_uart_pb_decode'] if is_c else 0x490120)|1,0x600000,count=100)
   pair.append((calls,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(result,pair)
print('PASS_PB_DECODE_ENTRY_NATIVE 3')
