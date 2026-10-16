#!/usr/bin/env python3
"""Compare native hard-float Horner evaluation with source arithmetic."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-polynomial';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt_path=OUT/'verification.json';receipt_path.unlink(missing_ok=True)
    rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_polynomial.o';assert sha(obj)==r['units'][0]['object_sha256']
    mp=BASE/'native-float-bits-runtime/report.json';m=json.loads(mp.read_text());mo=mp.parent/'native-float-bits-runtime.o';assert sha(mo)==m['linked_sha256'] and not m['undefined_symbols']
    for report in [r,m]:
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert bytes(json.loads((OUT/'ghidra-3b40c.json').read_text())['data'])==app.read_bytes()[0x1440c:0x14504]
    rea=json.loads((OUT/'rea-3b40c.json').read_text());rea=rea.get('structuredContent') or json.loads(rea['content'][0]['text']);assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea['normalized_result']['body']['total_bytes']==248
    digest=hashlib.sha256();counts={};helper_counts={'multiply':0,'add':0};states={}
    with tempfile.TemporaryDirectory(prefix='r1-polynomial-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';combined=OUT/'native-polynomial-runtime.o'
        subprocess.run(['arm-none-eabi-ld','-r',str(obj),str(mo),'-o',str(combined)],check=True)
        from build_source_candidates import undefined_symbols
        unresolved,_=undefined_symbols(combined);assert not unresolved,unresolved
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','r1_native_polynomial',str(combined),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        mapping={0x27c4a:'multiply',0x27afc:'add',syms['r1_format_double_multiply_bits']:'multiply',syms['r1_format_double_add_bits']:'add'}
        def hook(u,a,size,_):
            if a in mapping:states[id(u)][mapping[a]]+=1
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
        edges=[0,1,0xfffffffffffff,0x10000000000000,0x3fe0000000000000,0x3ff0000000000000,0x4000000000000000,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000000];edges += [v|1<<63 for v in edges];rng=random.Random(0x3b40c)
        samples=[(x,tuple(edges[(i+j)%len(edges)] for j in range(n)),mode) for i,x in enumerate(edges) for n,mode in itertools.product(range(1,33),range(4))]
        samples += [(rng.getrandbits(64),tuple(rng.getrandbits(64) for _ in range(rng.randrange(1,33))),i%4) for i in range(1024)]
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];dsaved=list(range(UC_ARM_REG_D8,UC_ARM_REG_D15+1))
        for x,coeff,mode in samples:
            raw=struct.pack('<'+'Q'*len(coeff),*coeff);results=[]
            for candidate,u in enumerate(machines):
                states[id(u)]={'multiply':0,'add':0};u.mem_write(0x20001000,raw);u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_R0,0x20001000);u.reg_write(UC_ARM_REG_R1,len(coeff));u.reg_write(UC_ARM_REG_D0,x);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,mode<<22)
                for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
                for i,reg in enumerate(dsaved):u.reg_write(reg,0x123456789abcdef0+i)
                u.emu_start((syms['r1_native_polynomial'] if candidate else 0x3b40c)|1,0x20000100,count=1000000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000
                assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and [u.reg_read(reg) for reg in dsaved]==[0x123456789abcdef0+i for i in range(8)]
                assert bytes(u.mem_read(0x20001000,len(raw)))==raw
                results.append([u.reg_read(UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),states[id(u)].copy()])
            assert results[0]==results[1],(hex(x),coeff,mode,results)
            assert results[0][2]=={'multiply':len(coeff)-1,'add':len(coeff)-1}
            for k,v in results[0][2].items():helper_counts[k]+=v
            counts[str(len(coeff))]=counts.get(str(len(coeff)),0)+1;digest.update(json.dumps([x,coeff,mode,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),coefficient_count_cases=counts,source_helper_calls=helper_counts,all_four_fpscr_rounding_modes=True,return_fpscr_stack_callee_saved_integer_fp_and_coefficients_checked=True,source_arithmetic=True,runtime_no_unresolved=True,runtime_object_sha256=sha(combined),trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),provider_report_sha256=sha(mp),provider_object_sha256=sha(mo),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in [OUT/'rea-3b40c.json',OUT/'ghidra-3b40c.json',OUT/'pseudocode-3b40c.c.txt']},instruction_identity=False,limitations=['Valid coefficient arrays with counts1..32 only; zero/unbounded counts, invalid pointers, faults, mutation and private stack aliases remain unproven.','Raw caller-saved registers, flags, private frame, whole input domain and instruction/whole-image/hardware identity remain open.'])
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
