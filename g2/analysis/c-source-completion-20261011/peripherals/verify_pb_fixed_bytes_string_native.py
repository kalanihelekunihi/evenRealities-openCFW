#!/usr/bin/env python3
"""Actual C/native fixed/bytes/string bounded child effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
STUB='''unsigned audio_pb_stream_write_490616(void *s,const void *p,unsigned n){(void)s;(void)p;(void)n;return 1;}
unsigned audio_pb_write_varint_490ce0(void *s,unsigned t,unsigned l,unsigned h){(void)s;(void)t;(void)l;(void)h;return 1;}'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_fixed_490f72',str(D/'display_pb_encode_fixed_bytes.c'),str(D/'display_pb_encode_string.c'),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[('fixed',4,0,4,b''),('fixed',8,0,8,b''),('fixed',3,0,3,b''),('bytes',6,0,0,b''),('bytes',6,0,6,b'abc'),('bytes',4,0,6,b'abc'),('string',0,0,0,b''),('string',5,0,5,b'abc'),('string',2,0,2,b'abc'),('string',5,0,5,b''),('string',5,0x80,5,b'abc')]
 total=0
 for mode,size,typ,present,payload in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   stream=0x20080000;it=0x20081000;data=0x20082000
   u.mem_write(stream,bytes(20));u.mem_write(it,bytes(40));u.mem_write(data,struct.pack('<H',len(payload))+payload+b'\0'+bytes(16))
   u.mem_write(it+18,struct.pack('<H',size));u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<I',data if present else 0))
   if mode=='string':u.mem_write(data,payload+b'\0'+bytes(16))
   child=(sy['audio_pb_write_length_delimited_490db6']&~1 if is_c else 0x490db6) if mode!='fixed' else None
   child32=(sy['audio_pb_write_fixed32_490d36']&~1 if is_c else 0x490d36)
   child64=(sy['audio_pb_write_fixed64_490d40']&~1 if is_c else 0x490d40)
   addr=[child] if child else [child32,child64];calls=[]
   def hook(uc,pc,n,user):
    calls.append((addr.index(pc),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   fn={'fixed':('audio_pb_encode_fixed_490f72',0x490f72),'bytes':('audio_pb_encode_bytes_490fa2',0x490fa2),'string':('audio_pb_encode_string_490fe4',0x490fe4)}[mode]
   u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy[fn[0]] if is_c else fn[1])|1,0x600000,count=1000)
   ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,22)).split(b'\0')[0] if ptr else b''
   pair.append((calls,u.reg_read(UC_ARM_REG_R0),err))
  assert pair[0]==pair[1],(mode,size,typ,present,payload,pair)
  total+=1
print('PASS_PB_FIXED_BYTES_STRING_NATIVE',total)
