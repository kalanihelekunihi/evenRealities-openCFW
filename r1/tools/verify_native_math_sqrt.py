#!/usr/bin/env python3
"""Compare complete source sqrt/sqrtf/errno with authenticated native entries."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-math-sqrt';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'sqrt':('r1_native_sqrt',0x3af94,122),'sqrtf':('r1_native_sqrtf',0x3b00e,58),'errno':('r1_native_errno_set',0x3bc9c,6)}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_math_sqrt.o';assert sha(obj)==report['units'][0]['object_sha256']
    bp=BASE/'native-math-sqrt-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-math-sqrt-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
    for r in [report,bundle]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n in TARGETS.values():
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    pointer=OUT/'ghidra-3bca4.json';assert bytes(json.loads(pointer.read_text())['data'])==struct.pack('<I',0x20007dbc);evidence[pointer.name]=sha(pointer)
    layout=ROOT/'r1/source-config/runtime/native_math_verification.ld';counts=dict.fromkeys(TARGETS,0);errno_writes=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-public-sqrt-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_native_sqrt',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_math_errno']==0x20007dbc;machines=[]
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
        rng=random.Random(0x3af94)
        wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        narrow=[(sign<<31)|(e<<23)|frac for sign,e,frac in itertools.product(range(2),range(256),[0,1,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
        samples=itertools.chain((('sqrt',x,(i%4)<<22) for i,x in enumerate(wide)),(('sqrtf',x,(rounding<<22)|(fz<<24)|(dn<<25)|0x10) for x,rounding,fz,dn in itertools.product(narrow,range(4),range(2),range(2))),(('errno',x,0) for x in itertools.chain(range(65536),[rng.getrandbits(32) for _ in range(4096)])))
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
                results.append([u.reg_read(UC_ARM_REG_R0 if kind=='errno' else UC_ARM_REG_S0 if kind=='sqrtf' else UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),bytes(u.mem_read(0x20007dbc,4)).hex(),states[id(u)].copy()])
            assert results[0]==results[1],(kind,hex(bits),hex(fpscr),results)
            counts[kind]+=1;errno_writes[kind]+=len(results[0][3]);digest.update(json.dumps([kind,bits,fpscr,initial_errno,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),counts=counts,errno_writes_per_side=errno_writes,all_binary32_and_binary64_exponents=True,both_signs=True,all_four_rounding_modes=True,sqrtf_flush_to_zero_and_default_nan_modes=True,sqrtf_preexisting_inexact_flag=True,all_low16_errno_words=True,return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked=True,actual_source_root_errno_and_memory=True,runtime_no_unresolved=True,errno_storage_address='0x20007dbc',trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Observed public return/FPSCR/errno/callee state only; arbitrary caller scratch/APSR/private-frame aliases remain open.','Native sqrt error branch is not independently forced; source helper results are used without a numerical boundary fixture.','Native sqrtf uses emulated VFP; physical FPU/interrupt behavior remains unproven.','Errno storage is source-owned and verification-placed; cold initialization and final firmware placement remain gated.','Bounded patterns do not prove full numerical domain or instruction/whole-image identity.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
