#!/usr/bin/env python3
"""Bounded stock/compiled-C nanopb tag parsing, including byte and error effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_pb_decode_tag.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_read_tag_48f66c',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[b'\x08',b'\x80\x01',b'\xff\xff\xff\xff\x0f',b'\x80',b'',b'\xff\xff\xff\xff\xff\x01',b'\xff\xff\xff\xff\x7f']
 def run(is_c,payload,fail):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  stream=0x20080000;out=0x20080100;cursor=[0]
  u.mem_write(stream,struct.pack('<IIII',0x100801,0,len(payload),0))
  u.mem_write(out,b'\xaa'*8)
  def callback(uc,pc,n,user):
   if fail or cursor[0]>=len(payload):uc.reg_write(UC_ARM_REG_R0,0)
   else:
    uc.mem_write(uc.reg_read(UC_ARM_REG_R1),payload[cursor[0]:cursor[0]+1]);cursor[0]+=1;uc.reg_write(UC_ARM_REG_R0,1)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,callback,begin=0x100800,end=0x100800)
  for reg,val in ((UC_ARM_REG_R0,stream),(UC_ARM_REG_R1,out),(UC_ARM_REG_R2,out+1),(UC_ARM_REG_R3,out+5),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  target=sy['audio_pb_read_tag_48f66c'] if is_c else 0x48f66c
  u.emu_start(target|1,0x600000,count=10000)
  data=bytes(u.mem_read(out,8));s=bytes(u.mem_read(stream,16));err=struct.unpack_from('<I',s,12)[0]
  if err:
   msg=bytes(u.mem_read(err,40)).split(b'\0')[0]
  else:msg=b''
  return u.reg_read(UC_ARM_REG_R0),data,struct.unpack_from('<I',s,8)[0],msg,cursor[0]
 total=0
 for payload in cases:
  for fail in (False,True):
   a=run(False,payload,fail);b=run(True,payload,fail)
   assert a==b,(payload,fail,a,b)
   total+=1
print('PASS_PB_DECODE_TAG_NATIVE',total)
