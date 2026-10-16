#!/usr/bin/env python3
"""Native floating conversion and rounding with real source shifts."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-float-rounding';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'signed_to32':('r1_signed64_to_binary32_bits',0x27e0c,136),'pack32':('r1_binary32_pack_words',0x2808a,92),'remainder32':('r1_log_round_float_bits',0x28078,18),'integral32':('r1_binary32_round_integral_bits',0x280e6,60),'integral64':('r1_binary64_round_integral_bits',0x282ac,132)}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_float_rounding.o';assert sha(obj)==r['units'][0]['object_sha256'];mp=BASE/'native-formatter-math/report.json';m=json.loads(mp.read_text());mo=mp.parent/'native-formatter-math.o';assert sha(mo)==m['linked_sha256'] and not m['undefined_symbols']
    for report in [r,m]:
        for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    sp=BASE/'structured-float/report.json';sr=json.loads(sp.read_text());so=sp.parent/'structured_float.o';assert sha(so)==sr['units'][0]['object_sha256']
    for path,digest in sr['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for a,n in [(0x27e0c,44),(0x2808a,92),(0x28078,18),(0x280e6,60),(0x282ac,132),(0x28330,4)]:
        p=OUT/f'ghidra-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    for _,a,_ in TARGETS.values():
        p=OUT/f'rea-{a:x}.json';evidence[p.name]=sha(p)
    counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='r1-float-bits-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';leaf=d/'round_one.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','r1_signed64_to_binary32_bits',str(obj),str(mo),str(so),'-o',str(elf)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.r1.float.round_one','-O','binary',str(obj),str(leaf)],check=True);assert leaf.read_bytes()==app.read_bytes()[0x28330-0x27000:0x28334-0x27000];literal_hash=sha(leaf)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
        rng=random.Random(0x2808a)
        wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        narrow=[(sign<<31)|(e<<23)|frac for sign,e,frac in itertools.product(range(2),range(256),[0,1,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
        integers=[*range(65536),*[(-n)&0xffffffffffffffff for n in range(65536)],*[rng.getrandbits(64) for _ in range(8192)],*[((1<<n)+offset)&0xffffffffffffffff for n,offset in itertools.product(range(64),[-1,0,1])]]
        samples=itertools.chain((('integral64',[x&0xffffffff,x>>32,0x76543210,0xfedcba98]) for x in wide),(('integral32',[x,0x76543210,0xfedcba98,0xabcdef01]) for x in narrow),(('signed_to32',[x&0xffffffff,x>>32,0x76543210,0xfedcba98]) for x in integers),(('remainder32',[x,r,0x76543210,0xfedcba98]) for x,r in itertools.product([0,1,2,0x7fffffff,0x80000000,0xffffffff],[0,1,0x7fffffff,0x80000000,0x80000001,0xffffffff])),(('remainder32',[rng.getrandbits(32),rng.getrandbits(32),0x76543210,0xfedcba98]) for _ in range(8192)),(('pack32',[high,low,sign,exp]) for high,low,sign,exp in itertools.product([0,1,2,0x7fffffff,0x80000000,0xffffffff],[0,1,0x7fffffff,0x80000000,0xffffffff],[0,0x80000000],[0,1,24,25,31,32,126,127,150,182,255,0x7fffffff,0x80000000,0xffffffff])),(('pack32',[rng.getrandbits(32) for _ in range(4)]) for _ in range(8192)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for index,(kind,regs) in enumerate(samples):
            name,entry,_=TARGETS[kind]
            initial_fpscr=(index%4)<<22;results=[]
            for candidate,u in enumerate(machines):
                u.mem_write(0x2003ef00,b'\x96'*512);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,initial_fpscr)
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,value)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=5000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)] and u.reg_read(UC_ARM_REG_FPSCR)==initial_fpscr
                result=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1]];results.append(result if kind=='integral64' else result[:1])
            assert results[0]==results[1],(kind,list(map(hex,regs)),results)
            counts[kind]+=1;digest.update(json.dumps([kind,regs,results[0]],sort_keys=True).encode())
    receipt=dict(reused_remainder_report_sha256=sha(sp),reused_remainder_object_sha256=sha(so),comparisons=sum(counts.values()),counts=counts,all_binary32_and_binary64_exponents=True,both_signs=True,all_positive_negative_low16_integer_words=True,seeded_random_patterns=True,return_values_stack_callee_saved_and_fpscr_checked=True,source_round_and_shifts=True,round_one_literal_bytes_equal=True,round_one_literal_sha256=literal_hash,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),math_report_sha256=sha(mp),math_object_sha256=sha(mo),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['0x2808a is a shared interior entry of native0x27e0c, not92 additional unique native bytes.','Selected exponent/sign/fraction patterns and seeded words do not exhaust all inputs.','Only typed return registers, stack/callee-saved registers and FPSCR checked; other scratch/APSR/private frame and whole-image identity remain open.','Source-owned4-byte round-one literal equals native bytes; placement and hardware remain unproven.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
