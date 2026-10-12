#!/usr/bin/env python3
"""Bounded raw-word comparison of IAR 0x422700 and C exponent scaler."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[4]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/initializer_callbacks/iar_format_native/fp_primitives.c'
LOCKED='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert hashlib.sha256(STOCK.read_bytes()).hexdigest()==LOCKED
with tempfile.TemporaryDirectory(prefix='boot-scale2-') as td:
 d=Path(td);obj=d/'scale.o';elfpath=d/'scale.elf'
 cc=['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin']
 subprocess.run(cc+['-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x500000',str(obj),'-o',str(elfpath)],check=True)
 with elfpath.open('rb') as f:
  e=ELFFile(f);symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
  segments=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
 inputs=[('normal-up',0x3ff4000000000000,5),('normal-down',0x4058000000000000,-3),('normal-to-max-exp',0x7fd0000000000001,1),('normal-to-overflow',0x7fd0000000000001,2),('min-normal-to-min-normal',0x0020000000000000,-1),('zero',0,500),('negative-zero',0x8000000000000000,-500),('infinity',0x7ff0000000000000,-100),('nan',0x7ff8000000000012,3),('hard-underflow',0x0010000000000000,-60),('negative-hard-underflow',0x8010000000000000,-60),('overflow',0x7fefffffffffffff,1),('hex-fraction-low',0x3fe0000000000000,28),('hex-fraction-near-one',0x3fefffffffffffff,28),('hex-fraction-rounding',0x3fe123456789abcd,28),('hex-fraction-negative',0xbfe123456789abcd,28)]
 cases=[]
 for label,x,n in inputs:
  pair=[]
  for native in (True,False):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x410000,0x40000);u.mem_write(0x410000,STOCK.read_bytes())
   u.mem_map(0x500000,0x10000)
   if not native:
    for a,b in segments:u.mem_write(a,b)
   u.mem_map(0x20000000,0x40000)
   u.mem_map(0xe000e000,0x1000);u.mem_write(0xe000ed88,struct.pack('<I',0x00f00000))
   u.reg_write(UC_ARM_REG_R0,x&0xffffffff);u.reg_write(UC_ARM_REG_R1,x>>32);u.reg_write(UC_ARM_REG_R2,n&0xffffffff)
   u.reg_write(UC_ARM_REG_SP,0x2002f000);u.reg_write(UC_ARM_REG_LR,0x50f001)
   entry=0x422700 if native else symbols['opencfw_fp_scale2']&~1
   try:u.emu_start(entry|1,0x50f000,count=10000)
   except Exception as ex:raise RuntimeError((label,native,hex(u.reg_read(UC_ARM_REG_PC)))) from ex
   pair.append({'result':f'{(u.reg_read(UC_ARM_REG_R1)<<32)|u.reg_read(UC_ARM_REG_R0):016x}','errno':struct.unpack('<I',u.mem_read(0x20027194,4))[0]})
  assert pair[0]==pair[1],(label,pair)
  cases.append({'case':label,'result':pair[0]})
 report={'status':'PASS_BOUNDED_FP_SCALE2','cases':cases,'original_sha256':LOCKED,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'limits':['Finite raw-word inputs only; Unicorn M-class cannot execute the stock double-precision VMUL at 0x42276a, so multiplying denormal and gradual-underflow paths remain untested.','FPSCR exception flags and all exponent boundary values are not yet fully qualified.']}
 Path(__file__).with_name('fp-scale2-oracle.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'cases':len(cases)}))
