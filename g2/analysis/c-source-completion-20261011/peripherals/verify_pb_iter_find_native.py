#!/usr/bin/env python3
"""Stock versus actual compiled C for nanopb field/extension iterator search."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate'
U16=lambda a:struct.unpack_from('<H',B,a-0x438000)[0]
U32=lambda a:struct.unpack_from('<I',B,a-0x438000)[0]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_pb_iter_find_tag_4d93f8',str(S/'display_pb_iter_find_decode.c'),str(S/'display_pb_iter_decode_advance.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 desc=0x7766dc;field=U32(desc);count=U16(desc+16)
 cases=[];wi=0;req=0;sub=0
 for ix in range(count):
  w=U32(field+4*wi);tag=(w>>2)&63;typ=(w>>8)&255
  cases.append((ix,wi,req,sub,tag));wi+=1<<(w&3);req+=((typ&0x30)==0);sub+=(typ&15) in (8,9)
 def run(is_c,name,case,tag):
  ix,wi,req,sub,_=case
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  it=0x20080000;msg=0x20081000;u.mem_write(msg,bytes(4096));u.mem_write(it,bytes(40))
  u.mem_write(it,struct.pack('<IIHHHH',desc,msg,ix,wi,req,sub))
  # Materialize the selected field's pointers, as the parent first calls iter_begin.
  u.reg_write(UC_ARM_REG_R0,it);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  decoder=sy['audio_pb_iter_decode_field_4d916e'] if is_c else 0x4d916e
  u.emu_start(decoder|1,0x600000,count=1000)
  u.reg_write(UC_ARM_REG_R0,it);u.reg_write(UC_ARM_REG_R1,tag);u.reg_write(UC_ARM_REG_LR,0x600001)
  target=(sy[name] if is_c else {'audio_pb_iter_find_tag_4d93f8':0x4d93f8,'audio_pb_iter_find_extension_4d946e':0x4d946e}[name])
  u.emu_start(target|1,0x600000,count=10000)
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(it,40))
 total=0
 for case in cases:
  for name,tag in [('audio_pb_iter_find_tag_4d93f8',case[-1]),('audio_pb_iter_find_tag_4d93f8',65535),('audio_pb_iter_find_extension_4d946e',0)]:
   a=run(False,name,case,tag);b=run(True,name,case,tag)
   assert a==b,(name,case,tag,a,b)
   total+=1
print('PASS_PB_ITER_FIND_NATIVE',total)
