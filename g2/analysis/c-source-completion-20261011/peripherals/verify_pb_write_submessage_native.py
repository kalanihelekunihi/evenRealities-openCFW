#!/usr/bin/env python3
"""Actual C/native two-pass submessage effects with encoder child cut."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_write_submessage.c'
STUB='''unsigned audio_pb_encode(void *s,const void *d,const void *m){(void)s;(void)d;(void)m;return 1;}
unsigned audio_pb_write_varint_490ce0(void *s,unsigned a,unsigned b,unsigned c){(void)s;(void)a;(void)b;(void)c;return 1;}
unsigned audio_pb_stream_write_490616(void *s,const void *p,unsigned n){(void)s;(void)p;(void)n;return 1;}'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-inline','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_write_submessage_490ddc',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,20,1,1,5),(1,20,0,1,5),(1,20,1,1,5),(1,3,1,1,5),(1,20,1,0,5),(1,20,1,1,3)]
 total=0
 for first_ok,max_size,varint_ok,second_ok,second_len in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   stream=0x20080000;descriptor=0x20081000;message=0x20082000;cb=0x20084000
   u.mem_write(stream,struct.pack('<IIIII',cb+1,0,max_size,0,0))
   names=['audio_pb_encode','audio_pb_write_varint_490ce0','audio_pb_stream_write_490616']
   addr=[sy[n]&~1 for n in names] if is_c else [0x490c32,0x490ce0,0x490616]
   calls=[]
   def hook(uc,pc,n,user):
    ix=addr.index(pc);calls.append(ix)
    if ix==0:
     child=uc.reg_read(UC_ARM_REG_R0);first=calls.count(0)==1
     uc.mem_write(child+12,struct.pack('<I',5 if first else second_len))
     uc.reg_write(UC_ARM_REG_R0,first_ok if first else second_ok)
    else:uc.reg_write(UC_ARM_REG_R0,varint_ok if ix==1 else 1)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for a in addr:u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
   u.reg_write(UC_ARM_REG_R0,stream);u.reg_write(UC_ARM_REG_R1,descriptor);u.reg_write(UC_ARM_REG_R2,message);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sy['audio_pb_write_submessage_490ddc'] if is_c else 0x490ddc)|1,0x600000,count=1000)
   ptr=struct.unpack('<I',u.mem_read(stream+16,4))[0];err=bytes(u.mem_read(ptr,22)).split(b'\0')[0] if ptr else b''
   pair.append((calls,u.reg_read(UC_ARM_REG_R0),struct.unpack('<I',u.mem_read(stream+12,4))[0],err))
  assert pair[0]==pair[1],((first_ok,max_size,varint_ok,second_ok,second_len),pair)
  total+=1
print('PASS_PB_WRITE_SUBMESSAGE_NATIVE',total)
