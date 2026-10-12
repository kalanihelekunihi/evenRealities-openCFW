#!/usr/bin/env python3
"""Actual C/native nanopb bounded substream begin/end with buffer effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_substream_begin_48f77e',str(S/'display_pb_decode_substream.c'),str(S/'display_pb_decode_stream.c'),str(S/'display_pb_decode_tag.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,payload,end):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  parent=0x20080000;sub=0x20080100;data=0x20080200;u.mem_write(data,payload);u.mem_write(sub,b'\xaa'*16)
  cb=sy['audio_pb_buffer_read_48f3a4'] if is_c else 0x48f3a5
  u.mem_write(parent,struct.pack('<IIII',cb,data,len(payload),0))
  for reg,val in ((UC_ARM_REG_R0,parent),(UC_ARM_REG_R1,sub),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  begin=sy['audio_pb_substream_begin_48f77e'] if is_c else 0x48f77e
  u.emu_start(begin|1,0x600000,count=5000)
  begin_result=u.reg_read(UC_ARM_REG_R0)
  first=(bytes(u.mem_read(parent,16)),bytes(u.mem_read(sub,16)))
  if end and begin_result:
   u.reg_write(UC_ARM_REG_R0,parent);u.reg_write(UC_ARM_REG_R1,sub);u.reg_write(UC_ARM_REG_LR,0x600001)
   finish=sy['audio_pb_substream_end_48f7ca'] if is_c else 0x48f7ca
   u.emu_start(finish|1,0x600000,count=5000)
   end_result=u.reg_read(UC_ARM_REG_R0)
  else:end_result=None
  second=(bytes(u.mem_read(parent,16)),bytes(u.mem_read(sub,16)))
  def norm(pair):
   out=[]
   for raw in pair:
    p=bytearray(raw);p[:4]=b'\0'*4
    err=struct.unpack_from('<I',p,12)[0]
    if err and err!=0xaaaaaaaa:p[12:16]=b'\0'*4
    out.append((bytes(p),bytes(u.mem_read(err,40)).split(b'\0')[0] if err and err!=0xaaaaaaaa else b''))
   return out
  return begin_result,norm(first),end_result,norm(second)
 total=0
 for payload,end in [(b'\x00',True),(b'\x03abc',True),(b'\x04abc',False),(b'\x80',False),(b'\x05abcde\x99',True)]:
  a=run(False,payload,end);b=run(True,payload,end)
  assert a==b,(payload,end,a,b)
  total+=1
print('PASS_PB_DECODE_SUBSTREAM_NATIVE',total)
