#!/usr/bin/env python3
"""Compare native binary64 bit conversion with C and actual recovered shifts."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-formatter-unsigned';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_formatter_unsigned.o';assert sha(obj)==r['units'][0]['object_sha256']
    ip=BASE/'integer-runtime/report.json';ir=json.loads(ip.read_text());integer=ip.parent/'integer-runtime.o';assert sha(integer)==ir['relocatable_sha256']
    for report in [r,ir]:
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert bytes(json.loads((OUT/'ghidra-28334.json').read_text())['data'])==app.read_bytes()[0x1334:0x1364]
    raw=json.loads((OUT/'rea-28334.json').read_text());rea=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'));assert rea['normalized_result']['body']['total_bytes']==48 and rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    digest=hashlib.sha256();comparisons=0;nonstandard=0;examples=[]
    with tempfile.TemporaryDirectory(prefix='r1-unsigned-') as tmp:
        elf=Path(tmp)/'test.elf';binary=Path(tmp)/'test.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','r1_format_double_to_unsigned_bits',str(obj),str(integer),'-o',str(elf)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
        rng=random.Random(0x28334);cases=itertools.chain((((sign<<63)|(exponent<<52)|(fraction<<32)|low) for sign,exponent,fraction,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])),(rng.getrandbits(64) for _ in range(16384)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for bits in cases:
            results=[]
            for candidate,u in enumerate(machines):
                u.reg_write(UC_ARM_REG_R0,bits&0xffffffff);u.reg_write(UC_ARM_REG_R1,bits>>32);u.reg_write(UC_ARM_REG_R2,0x87654321);u.reg_write(UC_ARM_REG_R3,0x76543210);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                u.emu_start((syms['r1_format_double_to_unsigned_bits'] if candidate else 0x28334)|1,0x20000100,count=1000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                results.append(u.reg_read(UC_ARM_REG_R0)|(u.reg_read(UC_ARM_REG_R1)<<32))
            assert results[0]==results[1],(hex(bits),list(map(hex,results)))
            comparisons+=1;digest.update(struct.pack('<QQ',bits,results[0]))
            if ((bits>>52)&2047)>1086 and results[0]:
                nonstandard+=1
                if len(examples)<8:examples.append(dict(input_bits=hex(bits),result=hex(results[0])))
    receipt=dict(comparisons=comparisons,all_binary64_exponents=True,both_signs=True,fraction_high_patterns=4,fraction_low_patterns=4,seeded_random_patterns=16384,oversized_exponent_nonzero_cases=nonstandard,oversized_examples=examples,actual_source_shift_providers=True,r0_r1_stack_and_callee_saved_checked=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),integer_report_sha256=sha(ip),integer_object_sha256=sha(integer),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in [OUT/'rea-28334.json',OUT/'ghidra-28334.json']},instruction_identity=False,limitations=['Sign is discarded by the native conversion; this is not standard double-to-unsigned saturation.','All exponent/sign patterns and selected fractions do not exhaust all 2^64 inputs.','Caller-saved r2/r3, APSR/private stack and instruction identity remain gated.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
