#!/usr/bin/env python3
"""Verify source binary64 pow against its authenticated native implementation."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-pow-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'pow':('r1_native_pow',0x399d0,1056,64,2)}
def main():
    vp=OUT/'source-verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_pow_dispatch.o';assert sha(obj)==report['units'][0]['object_sha256']
    bp=BASE/'native-pow-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-pow-runtime.o';assert sha(bo)==bundle['linked_sha256'] and bundle['undefined_symbols']==[]
    for r in [report,bundle]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n,_,_ in TARGETS.values():
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    layout=ROOT/'r1/source-config/runtime/native_pow_verification.ld';counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-public-sqrt-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_native_pow',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_pow_dispatch_prefix']==0x39df0 and syms['r1_pow_reduced']>=0x1000000;machines=[]
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
        rng=random.Random(0x3af94)
        wide=[(sign<<63)|(e<<52)|(frac<<32)|low for sign,e,frac,low in itertools.product(range(2),range(2048),[0,1,0x80000,0xfffff],[0,1,0x80000000,0xffffffff])]+[rng.getrandbits(64) for _ in range(4096)]
        narrow=[(sign<<31)|(e<<23)|frac for sign,e,frac in itertools.product(range(2),range(256),[0,1,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
        edges=[0,0x8000000000000000,1,0x8000000000000001,0xfffffffffffff,0x800fffffffffffff,0x10000000000000,0x8010000000000000,0x3fe0000000000000,0xbfe0000000000000,0x3ff0000000000000,0xbff0000000000000,0x4000000000000000,0xc000000000000000,0x7fefffffffffffff,0xffefffffffffffff,0x7ff0000000000000,0xfff0000000000000,0x7ff0000000000001,0xfff0000000000001,0x7ff8000000000000,0xfff8000000000000]
        exponent_pairs=[((sx<<63)|(e<<52)|fraction,(sy<<63)|(e<<52)|(fraction^0x8000000000000)) for e,sx,sy,fraction in itertools.product(range(2048),range(2),range(2),[0,0xfffffffffffff])]
        parity=[struct.unpack('<Q',struct.pack('<d',x))[0] for x in [-2.0,-1.0,-0.5,0.5,1.0,2.0,4503599627370496.0,9007199254740992.0]]
        base_pairs=[((sign<<63)|(e<<52)|fraction,y) for sign,e,fraction,y in itertools.product(range(2),[0,1,1022,1023,1024,2046,2047],[0,1,0xfffffffffffff],parity)]
        grid=[struct.unpack('<Q',struct.pack('<d',i/8.0))[0] for i in range(-16,17)]
        pairs=list(itertools.product(edges,repeat=2))+exponent_pairs+base_pairs+list(itertools.product(grid,repeat=2))+[(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(512)]
        basic=(('pow',x,y,r<<22) for (x,y),r in itertools.product(pairs,range(4)))
        modes=[(r<<22)|(fz<<24)|(dn<<25)|flags for r,fz,dn,flags in itertools.product(range(4),range(2),range(2),[0,0x10])]
        samples=itertools.chain(basic,(('pow',x,y,mode) for (x,y),mode in itertools.product(itertools.product(edges,repeat=2),modes)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];dsaved=list(range(UC_ARM_REG_D8,UC_ARM_REG_D15+1))
        for index,(kind,bits,other,fpscr) in enumerate(samples):
            name,entry,_,width,_=TARGETS[kind];initial_errno=(index*997)&0xffffffff;results=[]
            for candidate,u in enumerate(machines):
                states[id(u)]=[];u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.mem_write(0x20007dbc,struct.pack('<I',initial_errno));states[id(u)].clear();u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,fpscr)
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[bits&0xffffffff,bits>>32,other&0xffffffff,other>>32]):u.reg_write(reg,value)
                u.reg_write(UC_ARM_REG_D0,(other<<32)|bits if width==32 else bits);u.reg_write(UC_ARM_REG_D1,other if width==64 else 0x123456789abcdef0)
                for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
                for i,reg in enumerate(dsaved):u.reg_write(reg,0x123456789abcdef0+i)
                u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=100000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000,(kind,hex(bits),candidate)
                assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and [u.reg_read(reg) for reg in dsaved]==[0x123456789abcdef0+i for i in range(8)]
                results.append([u.reg_read(UC_ARM_REG_S0 if width==32 else UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),states[id(u)].copy()])
            assert results[0]==results[1],(kind,hex(bits),hex(other),hex(fpscr),results)
            counts[kind]+=1;digest.update(json.dumps([kind,bits,other,fpscr,results[0]],sort_keys=True).encode())
    with tempfile.TemporaryDirectory() as tmp:
        for name,address,length in [('prefix',0x39df0,48),('suffix',0x39e24,28),('zero',0xbdb50,8)]:
            q=Path(tmp)/'data.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.math.pow_dispatch_'+name,'-O','binary',str(obj),str(q)],check=True);assert q.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+length]
    for address,length in [(0x39e68,1056),(0x3a2e8,744),(0x3b54c,44),(0x39df0,120),(0xbdb50,8)]:
        q=OUT/f'ghidra-{address:x}.json';assert bytes(json.loads(q.read_text())['data'])==app.read_bytes()[address-0x27000:address-0x27000+length];evidence[q.name]=sha(q)
    receipt=dict(comparisons=sum(counts.values()),counts=counts,all_binary64_exponents=True,both_signs=True,seeded_random_pairs=True,all_four_rounding_modes=True,selected_edge_pairs_all_fz_dn_controls=True,selected_edge_pairs_initial_inexact_zero_and_one=True,return_fpscr_stack_callee_integer_fp_and_nonstack_writes_checked=True,actual_source_pow_dispatch=True,source_owned_numeric_bytes=84,shared_existing_numeric_bytes=8,unique_new_numeric_bytes=76,base_and_exponent_signs=True,integer_parity_cases=True,independent_calls_reset_xpsr=True,signed_zero_and_infinity_pairs=True,runtime_no_unresolved=True,native_pow_core_fixture=False,source_pow_complete=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),parent_layouts={path:sha(ROOT/path) for path in ['r1/source-config/runtime/native_powf_verification.ld','r1/source-config/runtime/native_log_verification.ld','r1/source-config/runtime/native_exp_verification.ld','r1/source-config/runtime/native_expm1_verification.ld','r1/source-config/runtime/native_atan_verification.ld','r1/source-config/runtime/native_tanf_verification.ld','r1/source-config/runtime/native_sinf_verification.ld','r1/source-config/runtime/native_cosf_verification.ld','r1/source-config/runtime/native_trig_reduce_consumers.ld', 'r1/source-config/runtime/native_atan2f_verification.ld', 'r1/source-config/runtime/native_atanf_verification.ld', 'r1/source-config/runtime/native_float_logs_verification.ld', 'r1/source-config/runtime/native_expf_tanhf_verification.ld', 'r1/source-config/runtime/native_math_special_verification.ld', 'r1/source-config/runtime/native_math_round_verification.ld', 'r1/source-config/runtime/native_double_directed_verification.ld', 'r1/source-config/runtime/native_math_selection_verification.ld', 'r1/source-config/runtime/native_math_verification.ld']},driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Typed D0/FPSCR/callee/nonstack checks do not establish remaining caller scratch/APSR/private-frame aliases.','Selected paired exponents/mantissas,base/parity cases,grid/random pairs and controls do not exhaust full pair domain or physical FPU behavior.','Source numeric constants/verification placement are separate from final instruction/whole-image identity.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
