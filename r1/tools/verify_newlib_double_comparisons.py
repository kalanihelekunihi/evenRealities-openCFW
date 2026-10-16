#!/usr/bin/env python3
"""Check compiled EABI adapters against binary64 ordering, not stock identity."""
import hashlib,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/newlib-stdio'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    objs=[OUT/'llvm-comparedf2.o',OUT/'double-comparisons.o'];report=OUT/'report.json';r=json.loads(report.read_text())
    for p in objs:assert any(row['object_sha256']==sha(p) for row in r['units'])
    with tempfile.TemporaryDirectory(prefix='r1-double-compare-') as tmp:
        elf=Path(tmp)/'compare.elf';binary=Path(tmp)/'compare.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','__aeabi_dcmpeq',*map(str,objs),'-o',str(elf)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,65536);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
        edges=[0,1,0xfffffffffffff,0x10000000000000,0x3fefffffffffffff,0x3ff0000000000000,0x3ff0000000000001,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000000,0x7fffffffffffffff]
        edges += [x|0x8000000000000000 for x in edges]
        rng=random.Random(0x38080);pairs=[(a,b) for a in edges for b in edges]+[(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(8192)]
        digest=hashlib.sha256();count=0
        for a,b in pairs:
            x,y=[struct.unpack('<d',struct.pack('<Q',z))[0] for z in (a,b)]
            for name,expected in [('__aeabi_dcmpeq',int(x==y)),('__aeabi_dcmplt',int(x<y)),('__aeabi_dcmple',int(x<=y)),('__aeabi_dcmpgt',int(x>y))]:
                for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[a&0xffffffff,a>>32,b&0xffffffff,b>>32]):u.reg_write(reg,val)
                u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
                for k,reg in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]):u.reg_write(reg,0x12345600+k)
                u.emu_start(syms[name]|1,0x20000100,count=1000)
                got=u.reg_read(UC_ARM_REG_R0);assert got==expected,(name,hex(a),hex(b),got,expected)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
                assert [u.reg_read(reg) for reg in [UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]]==[0x12345600+k for k in range(8)]
                digest.update(struct.pack('<QQI',a,b,got));count+=1
    receipt=dict(comparisons=count,pairs=len(pairs),reference='Python binary64 comparisons; signed zero, subnormals, infinities, quiet/signaling NaN and seeded random bit patterns',core_register_eabi_inputs=True,stack_and_callee_saved_checked=True,report_sha256=sha(report),driver_sha256=sha(Path(__file__)),objects={p.name:sha(p) for p in objs},trace_sha256=digest.hexdigest(),native_stock_comparison=False,instruction_identity=False)
    (OUT/'double-comparisons-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
