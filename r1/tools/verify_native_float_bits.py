#!/usr/bin/env python3
"""Native scalar floating-bit contracts with real source math providers."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-float-bits';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'class64':('r1_binary64_classify_bits',0x38110,48,'all'),'class32':('r1_binary32_classify_bits',0x38140,38,'all'),'signed_to64':('r1_signed32_to_binary64_bits',0x27e38,34,'64'),'unsigned_to64':('r1_unsigned32_to_binary64_bits',0x27e5a,26,'64'),'to_signed':('r1_binary64_to_signed32_bits',0x27e74,62,'32'),'to_unsigned':('r1_binary64_to_unsigned32_bits',0x27eb2,50,'32'),'from32':('r1_binary32_to_binary64_bits',0x27ee4,38,'64'),'subtract':('r1_binary64_subtract_bits',0x27c3e,6,'64'),'reverse_subtract':('r1_binary64_reverse_subtract_bits',0x27c44,6,'64'),'scale':('r1_binary64_scale_power2_bits',0x281dc,46,'64'),'environment':('r1_native_floating_environment_control',0x2839a,4,'all')}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_float_bits.o';assert sha(obj)==r['units'][0]['object_sha256'];mp=BASE/'native-formatter-math/report.json';m=json.loads(mp.read_text());mo=mp.parent/'native-formatter-math.o';assert sha(mo)==m['linked_sha256'] and not m['undefined_symbols']
    for report in [r,m]:
        for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n,_ in TARGETS.values():
        for prefix in ['rea','ghidra']:p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();class_tags={'class64':{},'class32':{}}
    with tempfile.TemporaryDirectory(prefix='r1-float-bits-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';leaf=d/'environment.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','r1_binary64_classify_bits',str(obj),str(mo),'-o',str(elf)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.text.r1_native_floating_environment_control','-O','binary',str(obj),str(leaf)],check=True);assert leaf.read_bytes()==app.read_bytes()[0x2839a-0x27000:0x2839e-0x27000];leaf_hash=sha(leaf)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
        rng=random.Random(0x38110);wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        narrow=[(sign<<31)|(e<<23)|frac for sign,e,frac in itertools.product(range(2),range(256),[0,1,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
        words=[*range(65536),0x7fffffff,0x80000000,0xffffffff,*[rng.getrandbits(32) for _ in range(8192)]]
        edges=[0,1,0xfffffffffffff,0x10000000000000,0x3ff0000000000000,0x3ff0000000000001,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000000];edges += [x|1<<63 for x in edges]
        samples=itertools.chain(((kind,x,0) for kind,x in itertools.product(['class64','to_signed','to_unsigned'],wide)),((kind,x,0) for kind,x in itertools.product(['class32','from32'],narrow)),((kind,x,0) for kind,x in itertools.product(['signed_to64','unsigned_to64'],words)),((kind,a,b) for kind,a,b in itertools.product(['subtract','reverse_subtract'],edges,edges)),((kind,rng.getrandbits(64),rng.getrandbits(64)) for kind in ['subtract','reverse_subtract'] for _ in range(8192)),(('scale',(sign<<63)|(e<<52)|frac,scale&0xffffffff) for sign,e,frac,scale in itertools.product(range(2),range(2048),[0,0xfffffffffffff],[-2048,-1024,-1,0,1,1024,2047,-0x80000000,0x7fffffff])),(('environment',rng.getrandbits(64),rng.getrandbits(64)) for _ in range(256)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for index,(kind,a,b) in enumerate(samples):
            name,entry,_,returns=TARGETS[kind];seed=(index*997)&0xffffffff;regs=[a&0xffffffff,a>>32,b&0xffffffff,b>>32]
            if kind in ['class32','from32','signed_to64','unsigned_to64']:regs=[a,seed,seed^0x76543210,seed^0xfedcba98]
            elif kind in ['class64','to_signed','to_unsigned']:regs[2:]=[seed^0x76543210,seed^0xfedcba98]
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
            if kind in class_tags:
                tag=str(results[0][0]);class_tags[kind][tag]=class_tags[kind].get(tag,0)+1
            digest.update(json.dumps([kind,a,b,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),counts=counts,class_tags=class_tags,all_binary32_and_binary64_exponents=True,both_signs=True,all_low16_integer_words=True,seeded_random_patterns=True,classifier_r0_r1_r2_r3_checked=True,return_values_stack_callee_saved_and_fpscr_checked=True,source_math_and_shifts=True,environment_instruction_bytes_equal=True,environment_instruction_bytes=4,environment_section_sha256=leaf_hash,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),math_report_sha256=sha(mp),math_object_sha256=sha(mo),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Raw bit conversion follows native behavior, not generic C/IEEE saturation or exceptional-value rules.','Every exponent/sign with selected fractions and integer/random samples does not exhaust all inputs or combinations.','Classifier/environment r0-r3 are checked; other helpers only their typed return fields. Private frames, other caller scratch/APSR and image identity remain gated.','Only the4-byte control leaf object section is byte-equal; image placement, complete identity and hardware remain unproven.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
