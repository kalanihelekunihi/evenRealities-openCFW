#!/usr/bin/env python3
"""Bounded stock/source comparison of the 728-byte correlation entry."""
from pathlib import Path
import hashlib,json,random,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
stock=blob[0x5918cc-0x437fe0:0x591ba4-0x437fe0]
assert hashlib.sha256(stock).hexdigest()=='60236d20621bee5d169103c082191c11bb5015491c16a288bf430f03a94d042f'
compiler=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
elf_path=Path('/tmp/audio_dsp_correlation.elf')
flags=['-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=hard',
       '-O0','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000',
       '-Wl,-e,g2_audio_dsp_correlate',
       '-Wl,--defsym=g2_audio_errno_slot=0x20074f14',
       '-Wl,--defsym=stock_asin=0x43c261']
subprocess.run([str(compiler),*flags,str(HERE/'dsp_correlation.c'),
                str(HERE/'i64_to_double.c'),str(HERE/'dsp_sqrt.c'),
                str(HERE/'delay_to_angle.c'),str(HERE/'dsp_clamp.c'),
                '-lgcc','-o',str(elf_path)],check=True)
with elf_path.open('rb') as stream:
  elf=ELFFile(stream)
  entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_audio_dsp_correlate')
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']

LEFT=0x20010000;RIGHT=0x20020000;OUT=0x20030000
def bits(x):return struct.unpack('<Q',struct.pack('<d',x))[0]
def run(source,left,right,n,limit,sample_rate=16000.,spacing=.14,speed=343.,rms_floor=0.,quality_floor=0.,mask=15):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
  u.mem_write(0x437fe0,blob)
  u.mem_map(0x10000000,0x100000)
  for a,data in segments:u.mem_write(a,data)
  u.mem_map(0x20000000,0x800000)
  u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  u.reg_write(UC_ARM_REG_SP,0x207ff000);u.reg_write(UC_ARM_REG_LR,0x10000001)
  if left:u.mem_write(LEFT,struct.pack('<%dh'%len(left),*left))
  if right:u.mem_write(RIGHT,struct.pack('<%dh'%len(right),*right))
  for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(LEFT,RIGHT,n,limit)):
    u.reg_write(reg,value)
  for reg,value in zip((UC_ARM_REG_D0,UC_ARM_REG_D1,UC_ARM_REG_D2,UC_ARM_REG_D3,UC_ARM_REG_D4),
                       (sample_rate,spacing,speed,rms_floor,quality_floor)):
    u.reg_write(reg,bits(value))
  for i in range(4):
    u.mem_write(0x207ff000+4*i,struct.pack('<I',OUT+i*8 if mask&(1<<i) else 0))
  u.mem_write(OUT,b'\xa5'*32)
  u.emu_start((entry if source else 0x5918cc)|1,0x10000000,count=3000000)
  assert u.reg_read(UC_ARM_REG_PC)==0x10000000
  return (u.mem_read(OUT,32).hex(),u.reg_read(UC_ARM_REG_FPSCR))

cases=[]
cases.append(('empty',[],[],0,10,0,0,15))
cases.append(('negative_count',[],[],-1,10,0,0,15))
cases.append(('one_equal',[10],[10],1,1,0,0,15))
cases.append(('silence',[0]*16,[0]*16,16,3,0,0,15))
cases.append(('default_lag',[0]*16,[0]*16,16,0,0,0,15))
cases.append(('energy_reject',[1]*16,[1]*16,16,3,2,0,15))
cases.append(('quality_reject',[1]*16,[1]*16,16,3,0,2,15))
cases.append(('null_outputs',[0]*16,[0]*16,16,3,0,0,0))
cases.append(('angle_only',[0]*16,[0]*16,16,3,0,0,1))
for lag in (-3,-1,0,1,3):
  l=[0]*16;r=[0]*16;l[8]=1000;r[8+lag]=1000
  cases.append((f'impulse_{lag}',l,r,16,3,0,0,15))
for mask in range(16):
  cases.append((f'pointer_mask_{mask}',[3,-2,7,0],[1,4,-5,2],4,2,0,0,mask))
for n in (1,2,8,16,32):
  generator=random.Random(0x5918cc+n)
  l=[generator.randrange(-32768,32768) for _ in range(n)]
  r=[generator.randrange(-32768,32768) for _ in range(n)]
  for limit in (-1,0,1,3,10,n+2):
    cases.append((f'random_{n}_{limit}',l,r,n,limit,0,0,15))
l=[0]*800;r=[0]*800;l[400]=1000;r[397]=1000
cases.append(('stock_size_800',l,r,800,10,0,0,15))
cases.extend([
  ('rms_equal',[1]*16,[1]*16,16,3,1,0,15),
  ('quality_equal_silence',[0]*16,[0]*16,16,3,0,0,15),
  ('nan_rms_floor',[1]*16,[1]*16,16,3,float('nan'),0,15),
  ('nan_quality_floor',[1]*16,[1]*16,16,3,0,float('nan'),15),
])
rows=[]
for name,l,r,n,limit,rms_floor,quality_floor,mask in cases:
  original=run(False,l,r,n,limit,rms_floor=rms_floor,quality_floor=quality_floor,mask=mask)
  compiled=run(True,l,r,n,limit,rms_floor=rms_floor,quality_floor=quality_floor,mask=mask)
  assert original==compiled,(name,original,compiled)
  rows.append(dict(name=name,n=n,limit=limit,rms_floor=rms_floor,quality_floor=quality_floor,
                   mask=mask,outputs=original[0],fpscr=hex(original[1])))
receipt=dict(status='PASS',cases=len(rows),image_sha256=SHA,body_sha256=hashlib.sha256(stock).hexdigest(),
             source_sha256=hashlib.sha256((HERE/'dsp_correlation.c').read_bytes()).hexdigest(),
             i64_source_sha256=hashlib.sha256((HERE/'i64_to_double.c').read_bytes()).hexdigest(),
             sqrt_source_sha256=hashlib.sha256((HERE/'dsp_sqrt.c').read_bytes()).hexdigest(),
             delay_source_sha256=hashlib.sha256((HERE/'delay_to_angle.c').read_bytes()).hexdigest(),
             clamp_source_sha256=hashlib.sha256((HERE/'dsp_clamp.c').read_bytes()).hexdigest(),
             elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),compiler=str(compiler),
             flags=flags,rows=rows,
             limits='Synthetic int16 PCM and bounded threshold parameters. Source i64-to-double uses toolchain libgcc; source sqrt binds errno RAM layout. Stock asin provider executes in both paths. This does not source-own asin or prove overflow, invalid pointers, hardware.')
(HERE/'correlation-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows))
