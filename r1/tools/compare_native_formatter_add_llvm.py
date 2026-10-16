#!/usr/bin/env python3
"""Bounded upstream reuse experiment; retain counterexamples, never admit by name."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-formatter-add';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rp=BASE/'newlib-stdio/report.json';r=json.loads(rp.read_text());objects=[rp.parent/'llvm-adddf3.o',rp.parent/'llvm-fp_mode.o']
    for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    for obj in objects:assert any(row['object_sha256']==sha(obj) for row in r['units'])
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    differences=[];counts=dict(matched=0,different=0);trace=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='r1-llvm-add-') as tmp:
        elf=Path(tmp)/'test.elf';binary=Path(tmp)/'test.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','__aeabi_dadd',*map(str,objects),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);machines.append(u)
        edges=[0,1,0xfffffffffffff,0x10000000000000,0x3fe0000000000000,0x3ff0000000000000,0x3ff0000000000001,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000000,0x7fffffffffffffff];edges += [v|1<<63 for v in edges];rng=random.Random(0xadd)
        for a,b in itertools.chain(itertools.product(edges,repeat=2),((rng.getrandbits(64),rng.getrandbits(64)) for _ in range(2048))):
            results=[]
            for candidate,u in enumerate(machines):
                for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[a&0xffffffff,a>>32,b&0xffffffff,b>>32]):u.reg_write(reg,v)
                u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms['__aeabi_dadd'] if candidate else 0x27afc)|1,0x20000100,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000;results.append(u.reg_read(UC_ARM_REG_R0)|(u.reg_read(UC_ARM_REG_R1)<<32))
            counts['matched' if results[0]==results[1] else 'different']+=1;trace.update(struct.pack('<QQQQ',a,b,*results))
            if results[0]!=results[1]:differences.append(dict(a=hex(a),b=hex(b),native=hex(results[0]),llvm=hex(results[1])))
    receipt=dict(cases=sum(counts.values()),counts=counts,differences=differences,source_report_sha256=sha(rp),objects={p.name:sha(p) for p in objects},driver_sha256=sha(Path(__file__)),application_sha256=sha(app),trace_sha256=trace.hexdigest(),generic_upstream_replacement_admitted=False,limitations=['Pinned LLVM default rounding mode is nearest/even; native bit results are compared without treating either implementation as a language-level compliance oracle.','Bounded input corpus establishes counterexamples, not exhaustive interchangeability or instruction identity.'])
    (OUT/'llvm-add-experiment.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['cases','counts','trace_sha256']}));print('first differences',differences[:5])
if __name__=='__main__':main()
