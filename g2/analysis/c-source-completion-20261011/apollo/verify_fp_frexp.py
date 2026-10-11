#!/usr/bin/env python3
"""Bounded native wrapper/source comparison for selected IAR binary64 frexp provider."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[4]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SOURCE=ROOT/'g2/components/bootloader/initializer_callbacks/iar_format_native/fp_primitives.c'
LOCKED='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
assert hashlib.sha256(STOCK.read_bytes()).hexdigest()==LOCKED
with tempfile.TemporaryDirectory(prefix='boot-frexp-') as tmp:
 d=Path(tmp);obj=d/'fp.o';elfpath=d/'fp.elf'
 cc=['clang','--target=arm-none-eabi','-mcpu=cortex-m33','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=softfp','-O2','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections']
 subprocess.run(cc+['-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','--gc-sections','-u','opencfw_fp_frexp','-Ttext=0x500000',str(obj),'-o',str(elfpath)],check=True)
 with elfpath.open('rb') as f:
  elf=ELFFile(f);sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()};segments=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD']
 cases=[]
 for value in [0,0x8000000000000000,1,0x8000000000000001,0xfffff,0x100000000,0x0008000000000000,0x0010000000000000,0x3ff0000000000000,0x400921fb54442d18,0xbfe0000000000000,0x7fefffffffffffff,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001]:
  pair=[]
  for native in [True,False]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x410000,0x40000);u.mem_write(0x410000,STOCK.read_bytes())
   u.mem_map(0x500000,0x10000)
   if not native:
    for a,b in segments:u.mem_write(a,b)
   u.mem_map(0x20000000,0x10000)
   for reg,v in [(UC_ARM_REG_R0,value&0xffffffff),(UC_ARM_REG_R1,value>>32),(UC_ARM_REG_R2,0x20000100),(UC_ARM_REG_SP,0x20008000),(UC_ARM_REG_LR,0x50f001)]:u.reg_write(reg,v)
   entry=0x422628 if native else sym['opencfw_fp_frexp']&~1
   u.emu_start(entry|1,0x50f000,count=10000)
   pair.append({'result':hex(u.reg_read(UC_ARM_REG_R0)|(u.reg_read(UC_ARM_REG_R1)<<32)),'exponent':struct.unpack('<i',u.mem_read(0x20000100,4))[0]})
  assert pair[0]==pair[1],(hex(value),pair)
  cases.append({'input':hex(value),**pair[0]})
 out={'status':'PASS_BOUNDED_FP_FREXP','original_sha256':LOCKED,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'cases':cases,'limits':['15 selected binary64 words compare native/source R0:R1 and exponent output. This is finite arithmetic qualification, not all 64-bit inputs or formatter consumer behavior.']}
 Path(__file__).with_name('fp-frexp-oracle.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'cases':len(cases)}))
