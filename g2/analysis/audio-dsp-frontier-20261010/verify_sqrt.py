#!/usr/bin/env python3
"""Stock 0x59c800 vs source VFP sqrt, including domain errno state."""
from pathlib import Path
import hashlib,json,random,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_D0,UC_ARM_REG_SP,UC_ARM_REG_LR,
    UC_ARM_REG_PC,UC_ARM_REG_FPSCR,UC_ARM_REG_C1_C0_2,UC_ARM_REG_FPEXC)
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
stock=blob[0x59c800-0x437fe0:0x59c81c-0x437fe0]
assert hashlib.sha256(stock).hexdigest()=='dbb01d401deb7e25eb46eaa901dfae2231f08896ef1eb4ab488c1cc61c2a35bd'
compiler=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
elf_path=Path('/tmp/audio_dsp_sqrt.elf')
flags=['-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=hard','-O0',
       '-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
       '-Wl,-e,g2_audio_dsp_sqrt','-Wl,--defsym=g2_audio_errno_slot=0x20074f14']
subprocess.run([str(compiler),*flags,str(HERE/'dsp_sqrt.c'),'-o',str(elf_path)],check=True)
with elf_path.open('rb') as stream:
  elf=ELFFile(stream)
  source_entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_audio_dsp_sqrt')
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']

def bits(x):return struct.unpack('<Q',struct.pack('<d',x))[0]
def run(source,value,preset):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
  u.mem_write(0x437fe0,blob)
  u.mem_map(0x10000000,0x100000)
  for a,data in segments:u.mem_write(a,data)
  u.mem_map(0x20000000,0x800000)
  u.mem_write(0x20074f14,struct.pack('<I',0xa5a5a5a5))
  u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000)
  u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  u.reg_write(UC_ARM_REG_D0,value)
  u.reg_write(UC_ARM_REG_FPSCR,preset)
  u.reg_write(UC_ARM_REG_SP,0x207ff000)
  u.reg_write(UC_ARM_REG_LR,0x10000001)
  u.emu_start((source_entry if source else 0x59c800)|1,0x10000000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x10000000
  return (u.reg_read(UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),
          struct.unpack('<I',u.mem_read(0x20074f14,4))[0])

values={0,bits(-0.0),bits(1),bits(2),bits(4),bits(0.5),bits(1e-300),
        bits(-1),bits(-2),bits(-4),bits(float('inf')),bits(-float('inf')),
        1,0x8000000000000001,0x7fefffffffffffff,0xffefffffffffffff,
        0x7ff8000000000001,0xfff8000000000001,0x7ff0000000000001,
        0xfff0000000000001}
for exp in range(0,1024,31):
  for fraction in (0,1,0x7ffffffffffff):
    for sign in (0,1):values.add((sign<<63)|(exp<<52)|fraction)
rng=random.Random(0x59c800)
for _ in range(128):values.add(bits(rng.uniform(0,1e8)))
rows=[]
for preset in (0,1,0x00400000,0x00800000,0x00c00000,0x01000000,0x02000000):
  for value in sorted(values):
    original=run(False,value,preset)
    compiled=run(True,value,preset)
    assert original==compiled,(hex(value),hex(preset),original,compiled)
    rows.append(dict(input=hex(value),initial_fpscr=hex(preset),output=hex(original[0]),
                     fpscr=hex(original[1]),errno=hex(original[2])))
receipt=dict(status='PASS',cases=len(rows),unique_inputs=len(values),image_sha256=SHA,
             stock_body_sha256=hashlib.sha256(stock).hexdigest(),
             source_sha256=hashlib.sha256((HERE/'dsp_sqrt.c').read_bytes()).hexdigest(),
             elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),compiler=str(compiler),
             compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),flags=flags,rows=rows,
             limits='Compares D0 bits, FPSCR and 0x20074f14 errno for synthetic inputs. Absolute errno RAM location is a linker/state-layout boundary. Enabled FP traps and hardware are untested.')
(HERE/'sqrt-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows),'cases',len(values),'unique inputs')
