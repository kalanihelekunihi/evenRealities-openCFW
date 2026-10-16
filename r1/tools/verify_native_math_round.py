#!/usr/bin/env python3
"""Compare native public round/roundf with source integral rounding and arithmetic."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-math-round';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'round':('r1_native_round',0x3ac88,192),'roundf':('r1_native_roundf',0x3ad68,154)}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_math_round.o';assert sha(obj)==report['units'][0]['object_sha256']
    bp=BASE/'native-math-round-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-math-round-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
    for r in [report,bundle]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n in TARGETS.values():
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    layout=ROOT/'r1/source-config/runtime/native_math_round_verification.ld';counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-public-sqrt-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_native_round',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_round_data']==0x3ad50;machines=[]
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
        rng=random.Random(0x3af94)
        wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        narrow=[(sign<<31)|(e<<23)|frac for sign,e,frac in itertools.product(range(2),range(256),[0,1,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
        tie64=[struct.unpack('<Q',struct.pack('<d',i+0.5))[0]+offset for i,offset in itertools.product(range(-2048,2048),[-1,0,1])]
        tie32=[struct.unpack('<I',struct.pack('<f',i+0.5))[0]+offset for i,offset in itertools.product(range(-2048,2048),[-1,0,1])]
        samples=itertools.chain((('round',x,(i%4)<<22) for i,x in enumerate(itertools.chain(wide,tie64))),(('roundf',x,(rounding<<22)|(fz<<24)|(dn<<25)|0x10) for x,rounding,fz,dn in itertools.product(itertools.chain(narrow,tie32),range(4),range(2),range(2))))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];dsaved=list(range(UC_ARM_REG_D8,UC_ARM_REG_D15+1))
        for index,(kind,bits,fpscr) in enumerate(samples):
            name,entry,_=TARGETS[kind];initial_errno=(index*997)&0xffffffff;results=[]
            for candidate,u in enumerate(machines):
                states[id(u)]=[];u.mem_write(0x20007dbc,struct.pack('<I',initial_errno));states[id(u)].clear();u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,fpscr)
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[bits&0xffffffff,bits>>32,0x76543210,0xfedcba98]):u.reg_write(reg,value)
                u.reg_write(UC_ARM_REG_D0,bits)
                for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
                for i,reg in enumerate(dsaved):u.reg_write(reg,0x123456789abcdef0+i)
                u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=10000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000,(kind,hex(bits),candidate)
                assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and [u.reg_read(reg) for reg in dsaved]==[0x123456789abcdef0+i for i in range(8)]
                results.append([u.reg_read(UC_ARM_REG_S0 if kind=='roundf' else UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),states[id(u)].copy()])
            assert results[0]==results[1],(kind,hex(bits),hex(fpscr),results)
            counts[kind]+=1;digest.update(json.dumps([kind,bits,fpscr,results[0]],sort_keys=True).encode())
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'data.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.math.round_data','-O','binary',str(obj),str(p)],check=True);raw=p.read_bytes();assert raw==app.read_bytes()[0x3ad50-0x27000:0x3ad68-0x27000]==bytes(json.loads((OUT/'ghidra-3ad50.json').read_text())['data']);data_sha256=sha(p)
    receipt=dict(comparisons=sum(counts.values()),counts=counts,all_binary32_and_binary64_exponents=True,both_signs=True,halfway_integer_range=[-2048,2047],halfway_and_adjacent_bits=True,all_four_rounding_modes=True,roundf_flush_to_zero_and_default_nan_modes=True,roundf_preexisting_inexact_flag=True,return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked=True,actual_source_integral_round_subtract_add_and_flags=True,source_owned_data_bytes=24,source_owned_data_sha256=data_sha256,runtime_no_unresolved=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),parent_layouts={path:sha(ROOT/path) for path in ['r1/source-config/runtime/native_double_directed_verification.ld','r1/source-config/runtime/native_math_selection_verification.ld','r1/source-config/runtime/native_math_verification.ld']},driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Native encoded/software arithmetic and VFP float operations retained; no generic libm replacement.','Typed FP return/FPSCR/callee/nonstack observations only; arbitrary caller scratch/APSR/private frame aliases remain open.','Selected exponent patterns,halfway integers and adjacent bits do not exhaust full input domain.','Source data/verification layout and emulated VFP observations are not final placement, instruction identity, whole-image or hardware proof.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
