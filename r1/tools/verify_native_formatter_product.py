#!/usr/bin/env python3
"""Differential native multiplication/division with source packing helpers."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-formatter-product';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_formatter_product.o';assert sha(obj)==r['units'][0]['object_sha256']
    ap=BASE/'native-formatter-add/report.json';ar=json.loads(ap.read_text());addition=ap.parent/'native_formatter_add.o';assert sha(addition)==ar['units'][0]['object_sha256']
    ip=BASE/'integer-runtime/report.json';ir=json.loads(ip.read_text());integer=ip.parent/'integer-runtime.o';assert sha(integer)==ir['relocatable_sha256']
    for report in [r,ir,ar]:
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for a,n in [(0x27c4a,228),(0x27d2e,222)]:
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
            if prefix=='ghidra':assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    counts=dict(multiply=0,divide=0);digest=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='r1-add-') as tmp:
        elf=Path(tmp)/'test.elf';binary=Path(tmp)/'test.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','r1_format_double_multiply_bits',str(obj),str(addition),str(integer),'-o',str(elf)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
        rng=random.Random(0x27afc);edges=[0,1,0xfffffffffffff,0x10000000000000,0x3fefffffffffffff,0x3ff0000000000000,0x3ff0000000000001,0x4000000000000000,0x43efffffffffffff,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000000,0x7fffffffffffffff];edges += [v|1<<63 for v in edges]
        cases=itertools.chain(((kind,a,b,0,0) for kind,a,b in itertools.product(['multiply','divide'],edges,edges)),((kind,rng.getrandbits(64),rng.getrandbits(64),0,0) for kind in ['multiply','divide'] for _ in range(32768)),((kind,((e<<52)|f)|(signa<<63),((other<<52)|g)|(signb<<63),0,0) for kind,e,other,f,g,signa,signb in itertools.product(['multiply','divide'],range(2048),[0,1023,2047],[0,0xfffffffffffff],[0,1],range(2),range(2))))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        names={'multiply':('r1_format_double_multiply_bits',0x27c4a),'divide':('r1_format_double_divide_bits',0x27d2e)}
        for kind,a,b,sign,exponent in cases:
            results=[]
            for candidate,u in enumerate(machines):
                regs=[a&0xffffffff,a>>32,b&0xffffffff,b>>32]
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,value)
                u.mem_write(0x2003ef00,b'\xa5'*512);u.mem_write(0x2003f000,struct.pack('<QI',sign,exponent));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                name,entry=names[kind];u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=4000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                results.append(u.reg_read(UC_ARM_REG_R0)|(u.reg_read(UC_ARM_REG_R1)<<32))
            assert results[0]==results[1],(kind,hex(a),hex(b),hex(sign),hex(exponent),list(map(hex,results)))
            counts[kind]+=1;digest.update(kind.encode()+struct.pack('<QQQIQ',a,b,sign,exponent,results[0]))
    receipt=dict(comparisons=sum(counts.values()),counts=counts,all_binary64_exponents=True,both_signs=True,operand_exponent_edges=[0,1023,2047],source_packing_and_rounding=True,source_integer_shifts=True,r0_r1_stack_and_callee_saved_checked=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),addition_report_sha256=sha(ap),addition_object_sha256=sha(addition),integer_report_sha256=sha(ip),integer_object_sha256=sha(integer),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Native encoded-bit arithmetic, not generic IEEE compliance, defines this source contract.','Every exponent and sign with selected fractions plus random pairs does not exhaust all input pairs.','Caller-saved scratch registers, APSR/private frame and instruction identity remain gated.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
