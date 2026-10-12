#!/usr/bin/env python3
"""Actual C/native extension descriptor/message choice and error effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_default_extension.c'
STUB='''unsigned audio_pb_iter_begin_4d94ba(void *i,const void *d,const void *m){(void)i;(void)d;(void)m;return 1;}
unsigned audio_pb_encode_field_490b1e(void *s,void *i){(void)s;(void)i;return 1;}'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_default_extension_490bc8',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 total=0
 for pointer in (False,True):
  for begin_ok in (False,True):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    stream=0x20080000;ext=0x20081000;typ=0x20082000;desc=0x20083000;field=0x20084000;msg=0x20085000
    u.mem_write(stream,bytes(20));u.mem_write(ext,struct.pack('<III',typ,msg,0));u.mem_write(typ,struct.pack('<III',0,0,desc));u.mem_write(desc,struct.pack('<I',field)+bytes(20));u.mem_write(field,struct.pack('<I',0x8000 if pointer else 0))
    begin=(sy['audio_pb_iter_begin_4d94ba']&~1) if is_c else 0x4d9384;encode=(sy['audio_pb_encode_field_490b1e']&~1) if is_c else 0x490b1e;calls=[]
    def hook(uc,pc,n,user):
     if pc==begin:
      it=uc.reg_read(UC_ARM_REG_R0);calls.append(('begin',uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
      uc.mem_write(it,bytes(40));uc.reg_write(UC_ARM_REG_R0,int(begin_ok))
     else:
      it=uc.reg_read(UC_ARM_REG_R1);calls.append(('encode',uc.reg_read(UC_ARM_REG_R0),struct.unpack('<I',uc.mem_read(it+32,4))[0]))
      uc.reg_write(UC_ARM_REG_R0,1)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for a in (begin,encode):u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
    u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,ext);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((sy['audio_pb_encode_default_extension_490bc8'] if is_c else 0x490bc8)|1,0x600000,count=1000)
    ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,18)).split(b'\0')[0] if ptr else b''
    pair.append((calls,u.reg_read(UC_ARM_REG_R0),err))
   assert pair[0]==pair[1],(pointer,begin_ok,pair)
   total+=1
print('PASS_PB_DEFAULT_EXTENSION_NATIVE',total)
