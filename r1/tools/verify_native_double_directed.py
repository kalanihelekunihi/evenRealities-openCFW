#!/usr/bin/env python3
"""Compare source double ceil/floor with native arithmetic, masks and carry behavior."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-double-directed';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'ceil':('r1_native_ceil',0x388d8,252),'floor':('r1_native_floor',0x39108,252)}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_double_directed.o';assert sha(obj)==report['units'][0]['object_sha256']
    bp=BASE/'native-double-directed-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-double-directed-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
    for r in [report,bundle]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n in TARGETS.values():
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    layout=ROOT/'r1/source-config/runtime/native_double_directed_verification.ld';counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-public-sqrt-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_native_ceil',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_ceil_data']==0x389d8 and syms['r1_native_floor_data']==0x39208;machines=[]
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
        rng=random.Random(0x3af94)
        wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        low16=[(sign<<63)|(1043<<52)|low for sign,low in itertools.product(range(2),range(65536))]
        carries=[(sign<<63)|((e+1023)<<52)|(high<<32)|low for sign,e,high,low in itertools.product(range(2),range(20,52),[0,1,0xfffff],[0,1,0x7fffffff,0x80000000,0xffffffff])]
        samples=((kind,x,(i%4)<<22) for kind in TARGETS for i,x in enumerate(itertools.chain(wide,low16,carries)))
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
                results.append([u.reg_read(UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),states[id(u)].copy()])
            assert results[0]==results[1],(kind,hex(bits),hex(fpscr),results)
            counts[kind]+=1;digest.update(json.dumps([kind,bits,fpscr,results[0]],sort_keys=True).encode())
    data_spans={}
    for section,address in [('.r1.math.ceil_data',0x389d8),('.r1.math.floor_data',0x39208)]:
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data.bin';subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(obj),str(p)],check=True);raw=p.read_bytes();assert raw==app.read_bytes()[address-0x27000:address-0x27000+24]==bytes(json.loads((OUT/f'ghidra-{address:x}.json').read_text())['data']);data_spans[section]=dict(address=hex(address),bytes=24,sha256=sha(p))
    receipt=dict(comparisons=sum(counts.values()),counts=counts,all_binary64_exponents=True,both_signs=True,all_low16_fraction_words_at_exponent20=True,high_low_carry_samples=True,all_four_rounding_modes=True,return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked=True,actual_source_add_subtract_and_flag_providers=True,source_owned_data_spans=data_spans,runtime_no_unresolved=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),parent_layouts={path:sha(ROOT/path) for path in ['r1/source-config/runtime/native_math_selection_verification.ld','r1/source-config/runtime/native_math_verification.ld']},driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Typed D0 result/FPSCR/callee state and nonstack writes checked; caller-saved/APSR/private-frame aliases remain open.','Native encoded arithmetic and comparison calls are executed from source, not generic libm replacements.','Selected exponents, low16 fractions and carry samples do not exhaust all inputs or hardware behavior.','Source data/verification layout are separate from final placement and whole-image instruction/byte identity.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
