#!/usr/bin/env python3
"""Actual compiled C/native callback payload bytes, lengths, and diagnostics."""
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
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_callback_payload_48f6ea',str(S/'display_pb_decode_callback_payload.c'),str(S/'display_pb_decode_stream.c'),str(S/'display_pb_decode_tag.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(is_c,wire,data,capacity):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  s=0x20080000;source=0x20080100;out=0x20080200;length=0x20080300
  u.mem_write(source,data);u.mem_write(out,b'\xaa'*16);u.mem_write(length,struct.pack('<I',capacity))
  cb=sy['audio_pb_buffer_read_48f3a4'] if is_c else 0x48f3a5;u.mem_write(s,struct.pack('<IIII',cb,source,len(data),0))
  for reg,val in ((UC_ARM_REG_R0,s),(UC_ARM_REG_R1,wire),(UC_ARM_REG_R2,out),(UC_ARM_REG_R3,length),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(reg,val)
  u.emu_start((sy['audio_pb_callback_payload_48f6ea'] if is_c else 0x48f6ea)|1,0x600000,count=2000)
  raw=bytes(u.mem_read(s,16));err=struct.unpack_from('<I',raw,12)[0]
  msg=bytes(u.mem_read(err,40)).split(b'\0')[0] if err else b''
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(out,16)),struct.unpack('<I',bytes(u.mem_read(length,4)))[0],raw[4:12],msg
 cases=[(0,b'\x01',10),(0,b'\x80\x01',10),(0,b'\x80\x80\x01',2),(0,b'\x80',10),(1,bytes(range(8)),10),(1,b'\x12',10),(5,b'\x12\x34\x56\x78',10),(3,b'\x12',10)]
 for case in cases:
  a=run(False,*case);b=run(True,*case);assert a==b,(case,a,b)
print('PASS_PB_DECODE_CALLBACK_PAYLOAD_NATIVE',len(cases))
