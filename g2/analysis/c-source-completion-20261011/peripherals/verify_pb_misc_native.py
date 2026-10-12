#!/usr/bin/env python3
"""Actual C/native bool, fixed-length and submessage dispatch effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_misc.c'
STUB='''unsigned audio_pb_first_char_nonzero_490678(const void *p){(void)p;return 1;}
unsigned audio_pb_write_varint_490ce0(void *s,unsigned a,unsigned b,unsigned c){(void)s;(void)a;(void)b;(void)c;return 1;}
unsigned audio_pb_write_length_delimited_490db6(void *s,const void *p,unsigned n){(void)s;(void)p;(void)n;return 1;}
unsigned audio_pb_write_submessage_490ddc(void *s,const void *d,const void *m){(void)s;(void)d;(void)m;return 1;}'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_submessage_49104c',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[('bool',0,0,0),('bool',1,0,0),('fixed',7,0,0),('sub',0,0,0),('sub',1,0,0),('sub',1,1,0),('sub',1,1,1)]
 total=0
 for mode,value,callback,fail in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   stream=0x20080000;it=0x20081000;data=0x20082000;prefix=0x20083000;cb=0x20084000;desc=0x20085000
   u.mem_write(stream,bytes(20));u.mem_write(it,bytes(40));u.mem_write(data,bytes([value])+bytes(20));u.mem_write(prefix,struct.pack('<II',cb+1 if callback else 0,0)+bytes(20))
   u.mem_write(it+18,struct.pack('<H',7));u.mem_write(it+22,bytes([9 if mode=='sub' and callback else 8]));u.mem_write(it+28,struct.pack('<I',data));u.mem_write(it+32,struct.pack('<I',prefix+8));u.mem_write(it+36,struct.pack('<I',desc if value else 0))
   names=['audio_pb_first_char_nonzero_490678','audio_pb_write_varint_490ce0','audio_pb_write_length_delimited_490db6','audio_pb_write_submessage_490ddc']
   addr=([sy[n]&~1 for n in names] if is_c else [0x490678,0x490ce0,0x490db6,0x490ddc]);calls=[]
   def hook(uc,pc,n,user):
    ix=4 if pc==cb else addr.index(pc);calls.append((ix,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    uc.reg_write(UC_ARM_REG_R0,0 if ix==4 and fail else 1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr+[cb]:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   fn={'bool':('audio_pb_encode_bool_490e90',0x490e90),'fixed':('audio_pb_encode_fixed_length_bytes_4910e8',0x4910e8),'sub':('audio_pb_encode_submessage_49104c',0x49104c)}[mode]
   u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy[fn[0]] if is_c else fn[1])|1,0x600000,count=1000)
   ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,25)).split(b'\0')[0] if ptr else b''
   # Native bool carries unused R1 residue from its predicate into varint.
   normalized=[(ix,r0,(0 if mode=='bool' and ix in (0,1) else r1),r2) for ix,r0,r1,r2 in calls]
   pair.append((normalized,u.reg_read(UC_ARM_REG_R0),err))
  assert pair[0]==pair[1],(mode,value,callback,fail,pair)
  total+=1
print('PASS_PB_MISC_NATIVE',total)
