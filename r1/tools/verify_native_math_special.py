#!/usr/bin/env python3
"""Compare native shared special-value leaf entries with actual source providers."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-math-special';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'divzero64': ('r1_math_divzero64', 242952, 28, 64, 0), 'self64': ('r1_math_self_add64', 243000, 20, 64, 1), 'add64': ('r1_math_add64', 243020, 20, 64, 2), 'invalid64': ('r1_math_invalid64', 243040, 24, 64, 0), 'high64': ('r1_math_high_square64', 243072, 24, 64, 0), 'low64': ('r1_math_low_square64', 243104, 24, 64, 0), 'divzero32': ('r1_math_divzero32', 244404, 14, 32, 0), 'self32': ('r1_math_self_add32', 244424, 6, 32, 1), 'add32': ('r1_math_add32', 244430, 6, 32, 2), 'invalid32': ('r1_math_invalid32', 244436, 10, 32, 0), 'high32': ('r1_math_high_square32', 244452, 10, 32, 0), 'low32': ('r1_math_low_square32', 244468, 10, 32, 0)}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_math_special.o';assert sha(obj)==report['units'][0]['object_sha256']
    bp=BASE/'native-math-special-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-math-special-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
    for r in [report,bundle]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n,_,_ in TARGETS.values():
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    layout=ROOT/'r1/source-config/runtime/native_math_special_verification.ld';counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-public-sqrt-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_math_divzero64',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_divzero64_data']==0x3b528;machines=[]
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
        rng=random.Random(0x3af94)
        wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        narrow=[(sign<<31)|(e<<23)|frac for sign,e,frac in itertools.product(range(2),range(256),[0,1,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
        edges32=[0,0x80000000,1,0x80000001,0x7fffff,0x800000,0x3f800000,0xbf800000,0x7f7fffff,0x7f800000,0xff800000,0x7f800001,0xff800001,0x7fc00000]
        edges64=[0,0x8000000000000000,1,0x8000000000000001,0xfffffffffffff,0x10000000000000,0x3ff0000000000000,0xbff0000000000000,0x7fefffffffffffff,0x7ff0000000000000,0xfff0000000000000,0x7ff0000000000001,0xfff0000000000001,0x7ff8000000000000]
        modes=[(r<<22)|(fz<<24)|(dn<<25)|flags for r,fz,dn,flags in itertools.product(range(4),range(2),range(2),[0,0x10])]
        pairs32=list(itertools.product(edges32,repeat=2))+[(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(1024)]
        pairs64=list(itertools.product(edges64,repeat=2))+[(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(4096)]
        samples=itertools.chain((('self64',a,0,(i%4)<<22) for i,a in enumerate(wide)),(('add64',a,b,(i%4)<<22) for i,(a,b) in enumerate(pairs64)),(('self32',a,0,mode) for a,mode in itertools.product(narrow,modes)),(('add32',a,b,mode) for (a,b),mode in itertools.product(pairs32,modes)),((kind,0,0,mode) for kind,mode in itertools.product([key for key,value in TARGETS.items() if value[4]==0],modes)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];dsaved=list(range(UC_ARM_REG_D8,UC_ARM_REG_D15+1))
        for index,(kind,bits,other,fpscr) in enumerate(samples):
            name,entry,_,width,_=TARGETS[kind];initial_errno=(index*997)&0xffffffff;results=[]
            for candidate,u in enumerate(machines):
                states[id(u)]=[];u.mem_write(0x20007dbc,struct.pack('<I',initial_errno));states[id(u)].clear();u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,fpscr)
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[bits&0xffffffff,bits>>32,other&0xffffffff,other>>32]):u.reg_write(reg,value)
                u.reg_write(UC_ARM_REG_D0,(other<<32)|bits if width==32 else bits);u.reg_write(UC_ARM_REG_D1,other if width==64 else 0x123456789abcdef0)
                for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
                for i,reg in enumerate(dsaved):u.reg_write(reg,0x123456789abcdef0+i)
                u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=10000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000,(kind,hex(bits),candidate)
                assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and [u.reg_read(reg) for reg in dsaved]==[0x123456789abcdef0+i for i in range(8)]
                results.append([u.reg_read(UC_ARM_REG_S0 if width==32 else UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),states[id(u)].copy()])
            assert results[0]==results[1],(kind,hex(bits),hex(fpscr),results)
            counts[kind]+=1;digest.update(json.dumps([kind,bits,other,fpscr,results[0]],sort_keys=True).encode())
    spans={}
    for section,address,size in [('divzero64',0x3b528,16),('invalid64',0x3b578,8),('high64',0x3b598,8),('low64',0x3b5b8,8),('divzero32',0x3bac4,4),('invalid32',0x3bae0,4),('high32',0x3baf0,4),('low32',0x3bb00,4)]:
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.math.'+section+'_data','-O','binary',str(obj),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+size]==bytes(json.loads((OUT/f'ghidra-{address:x}.json').read_text())['data']);spans[section]=dict(address=hex(address),bytes=size,sha256=sha(p))
    receipt=dict(comparisons=sum(counts.values()),counts=counts,all_binary32_and_binary64_exponents=True,both_signs=True,seeded_random_pairs=True,all_four_rounding_modes=True,float_flush_to_zero_and_default_nan_modes=True,initial_inexact_flag_zero_and_one=True,return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked=True,actual_source_double_add_multiply_divide=True,source_float_vfp_arithmetic=True,source_owned_data_spans=spans,runtime_no_unresolved=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),parent_layouts={path:sha(ROOT/path) for path in ['r1/source-config/runtime/native_math_round_verification.ld','r1/source-config/runtime/native_double_directed_verification.ld','r1/source-config/runtime/native_math_selection_verification.ld','r1/source-config/runtime/native_math_verification.ld']},driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Twelve leaf-entry contracts include shared parent tails; parent transcendental bodies remain separate source requirements.','Double wrappers execute native software-bit arithmetic; float wrappers execute VFP. Their return/exception rules are not inferred from generic upstream helper names.','Typed FP result/FPSCR/callee/nonstack checks do not establish complete caller scratch, private frames or full input domain.','Live function metadata for0x3bace is absent; exact span/disassembly, locked corpus and native entry behavior provide bounded evidence.','Source data/verification placement and FPU emulation are not whole-image byte identity or hardware proof.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
