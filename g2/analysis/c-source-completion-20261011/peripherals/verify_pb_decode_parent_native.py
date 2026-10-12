#!/usr/bin/env python3
"""Actual C/native nanopb decoder parent branch effects at authentic child ABIs."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_parent.c'
N=['iter_begin_4d94ba','default_fields_48fdf2','read_tag_48f66c','iter_find_tag_4d93f8','iter_find_extension_4d946e','decode_field_48fbe4','decode_extension_unknown_48fc88','skip_wire_48f6a0']
A=[0x4d9384,0x48fdf2,0x48f66c,0x4d93f8,0x4d946e,0x48fbe4,0x48fc88,0x48f6a0]
STUB='unsigned audio_pb_iter_begin_4d94ba(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_default_fields_48fdf2(void*a){(void)a;return 0;} unsigned audio_pb_read_tag_48f66c(void*a,void*b,void*c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;} unsigned audio_pb_iter_find_tag_4d93f8(void*a,unsigned b){(void)a;(void)b;return 0;} unsigned audio_pb_iter_find_extension_4d946e(void*a){(void)a;return 0;} unsigned audio_pb_decode_field_48fbe4(void*a,unsigned b,void*c){(void)a;(void)b;(void)c;return 0;} unsigned audio_pb_decode_extension_unknown_48fc88(void*a,unsigned b,unsigned c,void*d){(void)a;(void)b;(void)c;(void)d;return 0;} unsigned audio_pb_skip_wire_48f6a0(void*a,unsigned b){(void)a;(void)b;return 0;}'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_decode_parent_48fe98',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,tag,known,required,flags,init_ok,defaults_ok,field_ok):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;desc=0x20080100;msg=0x20080200
  u.mem_write(stream,struct.pack('<IIII',0,0,1,0));u.mem_write(desc,bytes(24));u.mem_write(desc+18,struct.pack('<H',required));calls=[];iterptr=[0]
  for ix,name in enumerate(N):
   addr=sy['audio_pb_'+name] if is_c else A[ix]
   def hook(uc,pc,n,user,kind=ix):
    regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
    calls.append(kind)
    if kind==0:
     iterptr[0]=regs[0];uc.mem_write(regs[0],struct.pack('<II',desc,msg)+bytes(32));result=init_ok
    elif kind==1:result=defaults_ok
    elif kind==2:
     uc.mem_write(regs[1],b'\x00');uc.mem_write(regs[2],struct.pack('<I',tag));uc.mem_write(regs[3],b'\x00')
     uc.mem_write(stream+8,struct.pack('<I',0));result=1
    elif kind==3:
     p=regs[0];uc.mem_write(p+16,struct.pack('<H',tag));uc.mem_write(p+22,b'\x01');uc.mem_write(p+12,struct.pack('<H',0));result=known
    elif kind==4:result=0
    elif kind==5:result=field_ok
    else:result=1
    uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,desc),(UC_ARM_REG_R2,msg),(UC_ARM_REG_R3,flags),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_decode_parent_48fe98'] if is_c else 0x48fe98)|1,0x600000,count=2000)
  err=struct.unpack('<I',bytes(u.mem_read(stream+12,4)))[0];message=bytes(u.mem_read(err,48)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),calls,message
 cases=[(1,1,0,0,1,1,1),(1,1,1,0,1,1,1),(1,0,0,0,1,1,1),(0,0,0,0,1,1,1),(0,0,0,4,1,1,1),(1,1,0,0,1,0,1),(1,1,0,1,1,0,1),(1,1,0,0,1,1,0),(1,0,1,0,1,1,1),(1,0,0,0,0,1,1)]
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
print('PASS_PB_DECODE_PARENT_NATIVE',len(cases))
