#!/usr/bin/env python3
"""Direct stock asin ABI, FP status and errno frontier; host math is diagnostic only."""
from pathlib import Path
import hashlib,json,math,random,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_D0,UC_ARM_REG_SP,UC_ARM_REG_LR,
    UC_ARM_REG_PC,UC_ARM_REG_FPSCR,UC_ARM_REG_C1_C0_2,UC_ARM_REG_FPEXC)

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
stock=blob[0x43c260-0x437fe0:0x43c36e-0x437fe0]
# Ghidra's body has two ranges: executable 0x43c260..0x43c2d7 and
# 0x43c2e8..0x43c36d; 0x43c2d8..e7 is literal data.
body=stock[:0x78]+stock[0x88:]
assert hashlib.sha256(stock).hexdigest()=='b69e1f84d2bade8702adfb2fd50ac4cb218a8d50af0fbc28a9c8f92d7692b558'

def bits(value):return struct.unpack('<Q',struct.pack('<d',value))[0]
def number(value):return struct.unpack('<d',struct.pack('<Q',value))[0]
def run(value,preset):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000)
  u.mem_write(0x437fe0,blob)
  u.mem_map(0x10000000,0x1000)
  u.mem_map(0x20000000,0x800000)
  u.mem_write(0x20074f14,struct.pack('<I',0xa5a5a5a5))
  u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000)
  u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  u.reg_write(UC_ARM_REG_D0,value)
  u.reg_write(UC_ARM_REG_FPSCR,preset)
  u.reg_write(UC_ARM_REG_SP,0x207ff000)
  u.reg_write(UC_ARM_REG_LR,0x10000001)
  u.emu_start(0x43c261,0x10000000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x10000000
  return (u.reg_read(UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),
          struct.unpack('<I',u.mem_read(0x20074f14,4))[0])

values={bits(v) for v in (-2.,-1.5,-1.,-.9999999999999999,-.9,-.5,-.125,
                          -1e-20,-0.0,0.,1e-20,.125,.5,.9,.9999999999999999,
                          1.,1.5,2.,float('inf'),-float('inf'))}
values.update((0x7ff8000000000001,0xfff8000000000001,
               0x7ff0000000000001,0xfff0000000000001,1,0x8000000000000001))
for power in range(1,54):
  value=2.**-power
  values.add(bits(value));values.add(bits(-value))
rng=random.Random(0x43c260)
for _ in range(128):
  value=rng.uniform(-1.,1.)
  values.add(bits(value))
rows=[];host_bit_matches=0;host_compared=0
for preset in (0,0x00400000,0x00800000):
  for input_bits in sorted(values):
    out,fpscr,errno=run(input_bits,preset)
    x=number(input_bits)
    host=None
    if preset==0 and math.isfinite(x) and -1.<=x<=1.:
      host=bits(math.asin(x));host_compared+=1
      host_bit_matches+=int(host==out)
    rows.append(dict(input=hex(input_bits),initial_fpscr=hex(preset),
                     output=hex(out),fpscr=hex(fpscr),errno=hex(errno),
                     host_asin_bits=hex(host) if host is not None else None))
receipt=dict(status='PASS',cases=len(rows),unique_inputs=len(values),image_sha256=SHA,
             body_and_literals_sha256=hashlib.sha256(stock).hexdigest(),
             executable_ranges_sha256=hashlib.sha256(body).hexdigest(),
             host_math_bit_matches=host_bit_matches,host_math_compared=host_compared,rows=rows,
             limits='Direct stock D0/FPSCR/errno observations in Unicorn; host math.asin only diagnostic, not replacement. No source candidate or hardware proof. Enabled FP traps and nondefault RAM initialization not tested.')
(HERE/'asin-frontier-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS',len(rows),'stock cases; host exact',host_bit_matches,'/',host_compared)
