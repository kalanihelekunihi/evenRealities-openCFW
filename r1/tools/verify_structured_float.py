#!/usr/bin/env python3
"""Compare native float bit-pattern source against original Arm runtime."""
import hashlib,json,random,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'structured-float/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 report=BASE/'structured-float/report.json';data=json.loads(report.read_text());obj=BASE/'structured-float/structured_float.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());candidate.mem_map(0x1000000,0x10000);candidate.mem_write(0x1000000,binary.read_bytes())
  for uc in (stock,candidate):uc.mem_map(0x20000000,0x40000)
  def run(uc,entry,low,high):
   uc.reg_write(UC_ARM_REG_R0,low);uc.reg_write(UC_ARM_REG_R1,high);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=1000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100;return uc.reg_read(UC_ARM_REG_R0)
  comparisons=0;rng=random.Random(0x27f6c)
  cases=[(low,(sign<<31)|(exponent<<20)|fraction) for sign in (0,1) for exponent in range(2048) for fraction in (0,1,0xfffff) for low in (0,1,0x0fffffff,0x10000000,0x10000001,0x1fffffff,0xffffffff)]
  cases += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(8192)]
  for low,high in cases:
   a=run(stock,0x27f6c,low,high);b=run(candidate,syms['r1_log_double_to_float_bits'],low,high);assert a==b,(hex(low),hex(high),hex(a),hex(b));comparisons+=1
  rounding=0
  for value in (0,1,2,0x7fffffff,0x80000000,0xfffffffe,0xffffffff):
   for remainder in (0,1,0x7fffffff,0x80000000,0x80000001,0xffffffff):
    assert run(stock,0x28078,value,remainder)==run(candidate,syms['r1_log_round_float_bits'],value,remainder);rounding+=1
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),conversion_comparisons=comparisons,rounding_comparisons=rounding,scope='All double exponent fields, both signs, rounding boundaries, random bit patterns and direct tie-to-even helper cases; actual original and candidate execution without interception',limitations=['Stock bit-pattern arithmetic is preserved, including non-IEEE exceptional-value behavior.','Original compiler output and complete runtime reconstruction remain open.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} conversion and {rounding} rounding comparisons passed')
if __name__=='__main__':main()
