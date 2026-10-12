#!/usr/bin/env python3
"""Actual C/native repeated-field packed and pointer-array branch effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_encode_repeated.c'
N=['key_490d4a','int_490eae','fixed_490f72','single_490a46','tag_490d66','write_varint_490ce0','stream_write_490616']
A=[0x490d4a,0x490eae,0x490f72,0x490a46,0x490d66,0x490ce0,0x490616]
STUB='\n'.join('unsigned audio_pb_encode_'+n+'(void *s,const void *i){(void)s;(void)i;return 1;}' if n.startswith(('key','int','fixed','single','tag')) else ('unsigned audio_pb_'+n+'(void *s,unsigned a,unsigned b,unsigned c){(void)s;(void)a;(void)b;(void)c;return 1;}' if n.startswith('write_varint') else 'unsigned audio_pb_'+n+'(void *s,const void *p,unsigned z){(void)s;(void)p;(void)z;return 1;}') for n in N)
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_encode_repeated_490690',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0x22,0,2,True,-1),(0x22,3,2,True,-1),(0x22,2,2,True,-1),(0x24,2,2,True,-1),(0x25,2,2,False,-1),(0x87,2,2,True,-1),(0x87,2,2,True,3),(0x06,2,2,True,-1),(0x87,2,2,False,-1),(0x28,2,2,True,-1)]
 total=0
 for typ,count,maxcount,callback,fail_call in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   stream=0x20080000;it=0x20081000;data=0x20082000;size=0x20083000
   u.mem_write(stream,struct.pack('<IIIII',0x20084001 if callback else 0,0,100,0,0));u.mem_write(it,bytes(40));u.mem_write(data,struct.pack('<III',0,0x20085000,0));u.mem_write(size,struct.pack('<H',count))
   u.mem_write(it+16,struct.pack('<HHH',4,4,maxcount));u.mem_write(it+22,bytes([typ]));u.mem_write(it+28,struct.pack('<I',data));u.mem_write(it+32,struct.pack('<I',size))
   addr=[sy['audio_pb_encode_'+n]&~1 if n.startswith(('key','int','fixed','single','tag')) else sy['audio_pb_'+n]&~1 for n in N] if is_c else A
   calls=[]
   def hook(uc,pc,n,user):
    ix=addr.index(pc);sptr=uc.reg_read(UC_ARM_REG_R0);calls.append((ix,sptr==stream))
    if ix==1 and sptr!=stream:
     old=struct.unpack('<I',uc.mem_read(sptr+12,4))[0];uc.mem_write(sptr+12,struct.pack('<I',old+2))
    uc.reg_write(UC_ARM_REG_R0,0 if len(calls)==fail_call else 1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_pb_encode_repeated_490690'] if is_c else 0x490690)|1,0x600000,count=3000)
   ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,24)).split(b'\0')[0] if ptr else b''
   pair.append((calls,u.reg_read(UC_ARM_REG_R0),struct.unpack('<I',u.mem_read(it+28,4))[0],err))
  assert pair[0]==pair[1],(typ,count,maxcount,callback,fail_call,pair)
  total+=1
print('PASS_PB_REPEATED_NATIVE',total)
