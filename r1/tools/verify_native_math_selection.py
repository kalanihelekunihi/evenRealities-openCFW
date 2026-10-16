#!/usr/bin/env python3
"""Compare native selection, absolute values and directed rounding with C providers."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-math-selection';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'compare':('r1_binary32_compare_flags',0x28364,54),'ceilf':('r1_native_ceilf',0x389f0,98),'floorf':('r1_native_floorf',0x39220,98),'fmaxf':('r1_native_fmaxf',0x39290,72),'fminf':('r1_native_fminf',0x392d8,72),'fabs':('r1_native_fabs',0x390f0,20),'fabs_core':('r1_native_fabs_core_bits',0x620f4,24),'compare_absf':('r1_native_compare_absf',0x98eca,16)}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_math_selection.o';assert sha(obj)==report['units'][0]['object_sha256']
    bp=BASE/'native-math-selection-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-math-selection-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
    for r in [report,bundle]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n in TARGETS.values():
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    layout=ROOT/'r1/source-config/runtime/native_math_selection_verification.ld';counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-public-sqrt-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_native_ceilf',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_ceilf_data']==0x38a54 and syms['r1_native_floorf_data']==0x39284;machines=[]
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
        rng=random.Random(0x3af94)
        wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        narrow=[(sign<<31)|(e<<23)|frac for sign,e,frac in itertools.product(range(2),range(256),[0,1,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
        edges=[0,0x80000000,1,0x80000001,0x7fffff,0x807fffff,0x800000,0x80800000,0x3f000000,0xbf000000,0x3f800000,0xbf800000,0x40000000,0xc0000000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7f800001,0xff800001,0x7fc00000,0xffc00000]
        pairs=list(itertools.product(edges,repeat=2))+[(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(1024)]
        modes=[(rounding<<22)|(fz<<24)|(dn<<25)|0x10 for rounding,fz,dn in itertools.product(range(4),range(2),range(2))]
        samples=itertools.chain(((kind,x,0,mode) for kind,x,mode in itertools.product(['ceilf','floorf','compare_absf'],narrow,modes)),((kind,x,0,(i%4)<<22) for kind in ['fabs','fabs_core'] for i,x in enumerate(wide)),((kind,a,b,mode) for kind,(a,b),mode in itertools.product(['fminf','fmaxf'],pairs,modes)),(('compare',a,b,(i%4)<<22) for i,(a,b) in enumerate(pairs)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];dsaved=list(range(UC_ARM_REG_D8,UC_ARM_REG_D15+1))
        for index,(kind,bits,other,fpscr) in enumerate(samples):
            name,entry,_=TARGETS[kind];initial_errno=(index*997)&0xffffffff;results=[]
            for candidate,u in enumerate(machines):
                states[id(u)]=[];u.mem_write(0x20007dbc,struct.pack('<I',initial_errno));states[id(u)].clear();u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,fpscr)
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[bits&0xffffffff,other if kind in ['compare','fminf','fmaxf'] else bits>>32,0x76543210,0xfedcba98]):u.reg_write(reg,value)
                u.reg_write(UC_ARM_REG_D0,(other<<32)|bits if kind in ['fminf','fmaxf'] else bits);u.reg_write(UC_ARM_REG_APSR,(index%2)<<27)
                for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
                for i,reg in enumerate(dsaved):u.reg_write(reg,0x123456789abcdef0+i)
                u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=10000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000,(kind,hex(bits),candidate)
                assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and [u.reg_read(reg) for reg in dsaved]==[0x123456789abcdef0+i for i in range(8)]
                result=u.reg_read(UC_ARM_REG_D0 if kind=='fabs' else UC_ARM_REG_R0 if kind in ['fabs_core','compare'] else UC_ARM_REG_S0)
                if kind=='fabs_core':result=[result|(u.reg_read(UC_ARM_REG_R1)<<32),u.reg_read(UC_ARM_REG_D0)]
                results.append([result,u.reg_read(UC_ARM_REG_FPSCR),u.reg_read(UC_ARM_REG_APSR)&0xf8000000 if kind=='compare' else None,states[id(u)].copy()])
            assert results[0]==results[1],(kind,hex(bits),hex(fpscr),results)
            counts[kind]+=1;digest.update(json.dumps([kind,bits,other,fpscr,results[0]],sort_keys=True).encode())
    data_spans={}
    for section,address,size in [('.r1.math.ceilf_data',0x38a54,8),('.r1.math.floorf_data',0x39284,12)]:
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data.bin';subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(obj),str(p)],check=True);raw=p.read_bytes();assert raw==app.read_bytes()[address-0x27000:address-0x27000+size]==bytes(json.loads((OUT/f'ghidra-{address:x}.json').read_text())['data']);data_spans[section]=dict(address=hex(address),bytes=size,sha256=sha(p))
    receipt=dict(comparisons=sum(counts.values()),counts=counts,all_binary32_and_binary64_exponents=True,both_signs=True,all_rounding_flush_to_zero_default_nan_modes=True,preexisting_inexact_flag=True,compare_return_and_apsr_nzcvq_checked=True,compare_initial_q_zero_and_one=True,core_fabs_d0_side_result_checked=True,return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked=True,source_owned_data_spans=data_spans,runtime_no_unresolved=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),parent_layout_sha256=sha(ROOT/'r1/source-config/runtime/native_math_verification.ld'),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Native raw ordering and comparison-based fabsf are not generic IEEE fmin/fmax/fabs behavior.','Only compare helper return and APSR NZCVQ are checked; other helpers caller scratch/APSR/private frames remain open.','Bounded exponent patterns/pairs/FPSCR controls do not exhaust inputs or hardware timing.','Data is source-owned and verification-placed; final image identity/integration remain gated.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
