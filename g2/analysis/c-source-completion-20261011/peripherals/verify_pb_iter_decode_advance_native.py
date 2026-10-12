#!/usr/bin/env python3
"""Actual compiled C/native iterator effects on authenticated stock descriptors."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_iter_decode_advance.c'
P=lambda a,n: B[a-0x438000:a-0x438000+n]
U16=lambda a:struct.unpack('<H',P(a,2))[0]
U32=lambda a:struct.unpack('<I',P(a,4))[0]
descs=[0x7766dc,0x7766f4,0x77670c,0x776724]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_iter_decode_field_4d916e',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 for desc in descs:
  fields=U32(desc);count=U16(desc+16);word_index=0;subidx=0;reqidx=0
  for idx in range(count):
   cases.append((desc,idx,word_index,reqidx,subidx))
   w=U32(fields+4*word_index);t=(w>>8)&255
   word_index+=1<<(w&3);reqidx+=((t&0x30)==0);subidx+=(t&15) in (8,9)
  cases.append((desc,count,word_index,reqidx,subidx))
 def run(is_c,fn,case,message):
  desc,index,fi,ri,si=case
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  it=0x20080000;msg=0x20081000
  u.mem_write(msg,bytes(4096));u.mem_write(it,b'\xcc'*40)
  u.mem_write(it,struct.pack('<IIHHHH',desc,msg if message else 0,index,fi,ri,si))
  u.reg_write(UC_ARM_REG_R0,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  target=sy[fn] if is_c else {'audio_pb_iter_decode_field_4d916e':0x4d916e,'audio_pb_iter_advance_4d930a':0x4d930a}[fn]
  u.emu_start(target|1,0x600000,count=1000)
  return bytes(u.mem_read(it,40)),u.reg_read(UC_ARM_REG_R0)
 total=0
 for case in cases:
  for fn in ('audio_pb_iter_decode_field_4d916e','audio_pb_iter_advance_4d930a'):
   for message in (False,True):
    a=run(False,fn,case,message);b=run(True,fn,case,message)
    if fn=='audio_pb_iter_advance_4d930a':a=(a[0],0);b=(b[0],0)
    assert a==b,(fn,case,message,a,b)
    total+=1
print('PASS_PB_ITER_DECODE_ADVANCE_NATIVE',total)
