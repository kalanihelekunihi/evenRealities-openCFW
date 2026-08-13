#!/usr/bin/env python3
"""Compare clean-room frexpf/ldexpf candidates with authenticated IAR stock."""
import argparse,hashlib,random,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import apollo_overlay
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';LOAD=0x437FE0;SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
STOCK={'frexpf':0x59D244,'frexpf_bits':0x59D258,'ldexpf':0x59D28C};BASE=0x100000;OFF={'frexpf':0,'frexpf_bits':0x100,'ldexpf':0x200};STOP=0x100F00;SRAM=0x20000000;STACK=0x20010000;OUT=0x20010100;ERRNO=0x20074F14
FILES={'frexpf':'open_cfw_iar_frexpf.bin','frexpf_bits':'open_cfw_iar_frexpf_bits.bin','ldexpf':'open_cfw_iar_ldexpf.bin'}
class QualificationError(RuntimeError):pass
def qualify(binary_dir:Path,iterations=4000,seed=0x59D244):
 try:
  from unicorn import Uc,UcError,UC_ARCH_ARM,UC_HOOK_CODE,UC_MODE_MCLASS,UC_MODE_THUMB
  from unicorn.arm_const import UC_ARM_REG_CONTROL,UC_ARM_REG_CPSR,UC_ARM_REG_FPSCR,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_S0,UC_ARM_REG_SP,UC_CPU_ARM_CORTEX_M33
 except ImportError as e:raise QualificationError('Python unicorn is required') from e
 blob=IMAGE.read_bytes()
 if hashlib.sha256(blob).hexdigest()!=SHA:raise QualificationError('image changed')
 bodies={k:bytearray((binary_dir/v).read_bytes()) for k,v in FILES.items()}
 bodies['frexpf'][8:12]=apollo_overlay.encode_thumb_bl(BASE+OFF['frexpf']+8,BASE+OFF['frexpf_bits'])
 bodies['ldexpf'][-6:-2]=apollo_overlay.encode_thumb_b_w(BASE+OFF['ldexpf']+len(bodies['ldexpf'])-6,0x439CB2)
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 mb=LOAD&~0xfff;prefix=LOAD-mb;u.mem_map(mb,(prefix+len(blob)+0xfff)&~0xfff);u.mem_write(LOAD,blob);u.mem_map(BASE,0x1000);u.mem_map(SRAM,0x100000);u.mem_map(0xE000E000,0x2000);u.mem_write(0xE000ED88,struct.pack('<I',0x00F00000))
 for k,v in bodies.items():u.mem_write(BASE+OFF[k],bytes(v))
 last_pc=[0]
 u.hook_add(UC_HOOK_CODE,lambda uc,address,size,user_data:last_pc.__setitem__(0,address))
 regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
 def reset(bits,arg,mark):
  for r,v in zip(regs,(arg,mark^0x11111111,mark^0x22222222,mark^0x33333333)):u.reg_write(r,v&0xffffffff)
  u.reg_write(UC_ARM_REG_S0,bits);u.reg_write(UC_ARM_REG_SP,STACK);u.reg_write(UC_ARM_REG_LR,STOP|1);u.reg_write(UC_ARM_REG_FPSCR,mark&0x00c00000);u.reg_write(UC_ARM_REG_CONTROL,u.reg_read(UC_ARM_REG_CONTROL)|(1<<2));u.reg_write(UC_ARM_REG_CPSR,u.reg_read(UC_ARM_REG_CPSR)|(1<<5));u.mem_write(OUT,struct.pack('<I',0xa5a5a5a5));u.mem_write(ERRNO,struct.pack('<I',0x5a5a5a5a))
 def run(addr):
  try:u.emu_start(addr|1,STOP,count=10000)
  except UcError as error:raise QualificationError(f'emulation failed after {last_pc[0]:#x}, pc={u.reg_read(UC_ARM_REG_PC):#x}: {error}') from error
  return (u.reg_read(UC_ARM_REG_S0)&0xffffffff,u.reg_read(UC_ARM_REG_R0)&0xffffffff,u.reg_read(UC_ARM_REG_R1)&0xffffffff,struct.unpack('<I',u.mem_read(OUT,4))[0],struct.unpack('<I',u.mem_read(ERRNO,4))[0],u.reg_read(UC_ARM_REG_FPSCR)&0xffffffff,u.reg_read(UC_ARM_REG_SP)&0xffffffff)
 def compare(name,bits,arg,mark):
  reset(bits,arg,mark);a=run(STOCK[name]);reset(bits,arg,mark);z=run(BASE+OFF[name])
  if a!=z:raise QualificationError(f'{name} mismatch bits={bits:#x} arg={arg:#x}: {a!r} != {z!r}')
 rng=random.Random(seed);fixed=(0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f000000,0x3f800000,0x7f7fffff,0x7f800000,0xff800000,0x7fc00001,0x7f800001)
 done={'frexpf':0,'frexpf_bits':0,'ldexpf':0}
 for i in range(iterations):
  bits=fixed[i] if i<len(fixed) else rng.getrandbits(32);mark=rng.getrandbits(32)
  compare('frexpf',bits,OUT,mark);done['frexpf']+=1
  compare('frexpf_bits',0,bits,mark);done['frexpf_bits']+=1
  exp=(-1000,-150,-127,-126,-25,-24,-1,0,1,24,25,126,127,150,1000)[i%15] if i<30 else rng.randrange(-1000,1001)
  compare('ldexpf',bits,exp&0xffffffff,mark);done['ldexpf']+=1
 return done
def main():
 p=argparse.ArgumentParser();p.add_argument('binary_dir',type=Path);p.add_argument('--iterations',type=int,default=4000);a=p.parse_args();print(qualify(a.binary_dir,a.iterations));return 0
if __name__=='__main__':raise SystemExit(main())
