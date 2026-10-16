#!/usr/bin/env python3
"""Compare native raw-bit square root with the actual combined source runtime."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-float-sqrt';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'sqrt64':('r1_binary64_square_root_bits',0x2820a,162,'64')}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_float_sqrt.o';assert sha(obj)==r['units'][0]['object_sha256'];mp=BASE/'native-float-sqrt-runtime/report.json';m=json.loads(mp.read_text());mo=mp.parent/'native-float-sqrt-runtime.o';assert sha(mo)==m['linked_sha256'] and not m['undefined_symbols']
    for report in [r,m]:
        for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n,_ in TARGETS.values():
        for prefix in ['rea','ghidra']:p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();positive_cases=0
    with tempfile.TemporaryDirectory(prefix='r1-float-bits-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';leaf=d/'environment.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','r1_binary64_square_root_bits',str(mo),'-o',str(elf)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
        rng=random.Random(0x38110);wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        squares=[struct.unpack('<Q',struct.pack('<d',float(i*i)))[0] for i in range(4096)]
        samples=(('sqrt64',x,0) for x in itertools.chain(wide,squares))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for index,(kind,a,b) in enumerate(samples):
            name,entry,_,returns=TARGETS[kind];seed=(index*997)&0xffffffff;regs=[a&0xffffffff,a>>32,b&0xffffffff,b>>32]
            regs[2:]=[seed^0x76543210,seed^0xfedcba98]
            initial_fpscr=(index%4)<<22;results=[]
            for candidate,u in enumerate(machines):
                u.mem_write(0x2003ef00,b'\x96'*512);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,initial_fpscr)
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,value)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=5000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)] and u.reg_read(UC_ARM_REG_FPSCR)==initial_fpscr
                result=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];results.append(result if returns=='all' else result[:2] if returns=='64' else result[:1])
            assert results[0]==results[1],(kind,hex(a),hex(b),list(map(hex,regs)),results)
            counts[kind]+=1
            positive_cases+=int(0<a<1<<63)
            digest.update(json.dumps([kind,a,b,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),counts=counts,positive_cases=positive_cases,nonpositive_return_zero_cases=sum(counts.values())-positive_cases,perfect_integer_square_samples=4096,all_binary64_exponents=True,both_signs=True,seeded_random_patterns=True,return_values_stack_callee_saved_and_fpscr_checked=True,source_round_and_shifts=True,runtime_no_unresolved=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(mp),runtime_object_sha256=sha(mo),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Native integer recurrence is not generic IEEE sqrt: signed-nonpositive encodings return+0 and positive exceptional/subnormal encodings use a forced hidden bit.','Every exponent/sign with selected fractions,4096 integer squares and random patterns does not exhaust all input bits.','Typed result, stack/callee registers and FPSCR checked; scratch/APSR/private frame, full-domain and instruction/image/hardware identity remain open.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
