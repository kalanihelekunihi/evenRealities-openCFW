#!/usr/bin/env python3
"""Stock 0x59c7ac vs source signed64-to-double raw-bit comparison."""
from pathlib import Path
import hashlib,json,random,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,
    UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_FPSCR)
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
stock=blob[0x59c7ac-0x437fe0:0x59c800-0x437fe0]
assert hashlib.sha256(stock).hexdigest()=='eebedaca845140b15ab5ffbe3ed94e135d303dc976ac2e5d320bcdb7e4d0b596'
compiler=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
elf_path=Path('/tmp/audio_dsp_i64.elf')
flags=['-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=hard',
       '-O0','-ffreestanding','-fno-builtin','-nostdlib',
       '-Wl,-Ttext=0x10001000','-Wl,-e,g2_audio_dsp_i64_to_double_bits']
subprocess.run([str(compiler),*flags,str(HERE/'i64_to_double.c'),'-lgcc','-o',str(elf_path)],check=True)
with elf_path.open('rb') as stream:
  elf=ELFFile(stream)
  source_entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_audio_dsp_i64_to_double_bits')
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']

def run(source,value,preset):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
  u.mem_write(0x437fe0,blob)
  u.mem_map(0x10000000,0x100000)
  for a,data in segments:u.mem_write(a,data)
  u.mem_map(0x20000000,0x1000)
  u.reg_write(UC_ARM_REG_SP,0x20000ff0)
  u.reg_write(UC_ARM_REG_LR,0x10000001)
  u.reg_write(UC_ARM_REG_FPSCR,preset)
  value &= (1<<64)-1
  u.reg_write(UC_ARM_REG_R0,value&0xffffffff)
  u.reg_write(UC_ARM_REG_R1,value>>32)
  u.emu_start((source_entry if source else 0x59c7ac)|1,0x10000000,count=1000)
  assert u.reg_read(UC_ARM_REG_PC)==0x10000000
  bits=u.reg_read(UC_ARM_REG_R0)|(u.reg_read(UC_ARM_REG_R1)<<32)
  return bits,u.reg_read(UC_ARM_REG_FPSCR)

values={0,1,-1,(1<<63)-1,-(1<<63)}
for power in range(0,63):
  for delta in (-3,-2,-1,0,1,2,3):
    for sign in (-1,1):
      value=sign*((1<<power)+delta)
      if -(1<<63)<=value<(1<<63):values.add(value)
rng=random.Random(0x59c7ac)
for _ in range(256):values.add(rng.randrange(-(1<<63),(1<<63)))
rows=[]
for preset in (0,1,0x00400000,0x00800000):
  for value in sorted(values):
    original=run(False,value,preset)
    compiled=run(True,value,preset)
    assert original==compiled,(value,hex(preset),original,compiled)
    rows.append(dict(value=value,initial_fpscr=hex(preset),bits=hex(original[0]),fpscr=hex(original[1])))
receipt=dict(status='PASS',cases=len(rows),unique_values=len(values),image_sha256=SHA,
             stock_body_sha256=hashlib.sha256(stock).hexdigest(),
             source_sha256=hashlib.sha256((HERE/'i64_to_double.c').read_bytes()).hexdigest(),
             elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),compiler=str(compiler),
             compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),flags=flags,rows=rows,
             limits='Exact raw IEEE-754 result bits and FPSCR across tested signed64 values; linked GCC libgcc __aeabi_l2d source/toolchain dependency. Other registers, stack writes and code identity differ.')
(HERE/'i64-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows),'cases',len(values),'unique values')
