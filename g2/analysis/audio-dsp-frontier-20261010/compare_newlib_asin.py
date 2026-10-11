#!/usr/bin/env python3
"""Diagnostic comparison of bundled GNU Arm libm against stock IAR asin."""
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import (UC_ARM_REG_D0,UC_ARM_REG_SP,UC_ARM_REG_LR,
    UC_ARM_REG_PC,UC_ARM_REG_FPSCR,UC_ARM_REG_C1_C0_2,UC_ARM_REG_FPEXC)
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent
compiler=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
elf_path=Path('/tmp/audio_newlib_asin.elf')
flags=['-mcpu=cortex-m55','-mthumb','-mfpu=fpv5-d16','-mfloat-abi=hard',
       '-O0','-ffreestanding','-fno-builtin','-nostdlib',
       '-Wl,-Ttext=0x10001000','-Wl,-e,g2_audio_newlib_asin_probe']
libm=Path(subprocess.check_output([str(compiler),*flags[:4],'-print-file-name=libm.a'],text=True).strip()).resolve()
subprocess.run([str(compiler),*flags,str(HERE/'newlib_asin_probe.c'),
                '-lm','-lgcc','-o',str(elf_path)],check=True)
with elf_path.open('rb') as stream:
  elf=ELFFile(stream)
  entry=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_audio_newlib_asin_probe')
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']

def run(value,preset):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x10000000,0x100000)
  for a,data in segments:u.mem_write(a,data)
  u.mem_map(0x20000000,0x800000)
  u.mem_write(0x20074f14,struct.pack('<I',0xa5a5a5a5))
  u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000)
  u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
  u.reg_write(UC_ARM_REG_D0,value);u.reg_write(UC_ARM_REG_FPSCR,preset)
  u.reg_write(UC_ARM_REG_SP,0x207ff000);u.reg_write(UC_ARM_REG_LR,0x10000001)
  u.emu_start(entry|1,0x10000000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x10000000
  return (u.reg_read(UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),
          struct.unpack('<I',u.mem_read(0x20074f14,4))[0])

stock=json.loads((HERE/'asin-frontier-receipt.json').read_text())
rows=[];bits_match=0;full_match=0
for row in stock['rows']:
  value=int(row['input'],16);preset=int(row['initial_fpscr'],16)
  try:newlib=run(value,preset)
  except Exception as exc:
    rows.append(dict(input=row['input'],preset=row['initial_fpscr'],error=str(exc)))
    continue
  expected=(int(row['output'],16),int(row['fpscr'],16),int(row['errno'],16))
  bits_match+=int(newlib[0]==expected[0]);full_match+=int(newlib==expected)
  rows.append(dict(input=row['input'],preset=row['initial_fpscr'],
                   stock=[hex(x) for x in expected],newlib=[hex(x) for x in newlib]))
receipt=dict(cases=len(rows),newlib_output_bit_matches=bits_match,
             newlib_full_state_matches=full_match,
             elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),
             compiler=str(compiler),compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),
             libm=str(libm),libm_sha256=hashlib.sha256(libm.read_bytes()).hexdigest(),
             flags=flags,rows=rows,
             limits='Bundled GNU Arm newlib __ieee754_asin binary is only an alternative diagnostic, not identified stock IAR source. Public newlib asin wrapper/errno behavior is not tested.')
(HERE/'newlib-asin-comparison.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('newlib exact output',bits_match,'/',len(rows),'full',full_match,'/',len(rows))
