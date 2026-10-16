#!/usr/bin/env python3
"""Compare native atan with source VFP range reduction, constants and dependencies."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-log';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'log':('r1_native_log',0x39320,872)}
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_log.o';assert sha(obj)==report['units'][0]['object_sha256']
    bp=BASE/'native-log-runtime/report.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-log-runtime.o';assert sha(bo)==bundle['linked_sha256'] and not bundle['undefined_symbols']
    for r in [report,bundle]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
    for _,a,n in TARGETS.values():
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
        assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    layout=ROOT/'r1/source-config/runtime/native_log_verification.ld';counts=dict.fromkeys(TARGETS,0);errno_writes=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-public-sqrt-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_native_log',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_math_errno']==0x20007dbc and syms['r1_log_prefix']==0x39688;machines=[]
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
        rng=random.Random(0x381f0)
        wide=[(sign<<63)|(e<<52)|frac for sign,e,frac in itertools.product(range(2),range(2048),[0,0xfffffffffffff])]+[rng.getrandbits(64) for _ in range(512)]
        centers=[high<<32 for high in [0,0x00100000,0x3ff00000,0x3fe6a09c,0x3ff6a09c,0x7ff00000]]
        boundaries=[(c+d)&0xffffffffffffffff for c,d in itertools.product(centers,range(-2,3))];boundaries += [x^0x8000000000000000 for x in boundaries]
        for exponent in [-1074,-1022,-54,-1,0,1,54,1023]:
            import math
            center=struct.unpack('<Q',struct.pack('<d',math.ldexp(1.0,exponent)))[0]
            boundaries += [(center+d)&0xffffffffffffffff for d in range(-2,3)]
        for mantissa in [0,1,2,0x6147a,0x6b851,0x6a09c,0xffffe,0xfffff]:
            center=0x3ff0000000000000|(mantissa<<32)
            boundaries += [(center+d)&0xffffffffffffffff for d in range(-2,3)]
        grid=[struct.unpack('<Q',struct.pack('<d',i/64.0))[0] for i in range(-256,257)]
        modes=[r<<22 for r in range(4)]
        basic=[(kind,x,mode) for kind,x,mode in itertools.product(TARGETS,itertools.chain(wide,boundaries,grid),modes)]
        control_values=[0,1,0x8000000000000000,0x8000000000000001,0x3fe0000000000000,0x3ff0000000000000,0x7ff0000000000000,0x7ff8000000000001,0x7ff0000000000001]
        controls=[(r<<22)|(fz<<24)|(dn<<25)|flags for r,fz,dn,flags in itertools.product(range(4),range(2),range(2),[0,0x10])]
        samples=itertools.chain(basic,itertools.product(TARGETS,control_values,controls))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];dsaved=list(range(UC_ARM_REG_D8,UC_ARM_REG_D15+1))
        for index,(kind,bits,fpscr) in enumerate(samples):
            name,entry,_=TARGETS[kind];initial_errno=(index*997)&0xffffffff;results=[]
            for candidate,u in enumerate(machines):
                states[id(u)]=[];u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.mem_write(0x20007dbc,struct.pack('<I',initial_errno));states[id(u)].clear();u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,fpscr)
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[bits&0xffffffff,bits>>32,0x76543210,0xfedcba98]):u.reg_write(reg,value)
                u.reg_write(UC_ARM_REG_D0,bits)
                for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
                for i,reg in enumerate(dsaved):u.reg_write(reg,0x123456789abcdef0+i)
                u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=10000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000,(kind,hex(bits),candidate)
                assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)] and [u.reg_read(reg) for reg in dsaved]==[0x123456789abcdef0+i for i in range(8)]
                results.append([u.reg_read(UC_ARM_REG_D0),u.reg_read(UC_ARM_REG_FPSCR),bytes(u.mem_read(0x20007dbc,4)).hex(),states[id(u)].copy()])
            assert results[0]==results[1],(kind,hex(bits),hex(fpscr),results)
            counts[kind]+=1;errno_writes[kind]+=len(results[0][3]);digest.update(json.dumps([kind,bits,fpscr,initial_errno,results[0]],sort_keys=True).encode())
    with tempfile.TemporaryDirectory() as tmp:
        for name,address,length in [('prefix',0x39688,48),('suffix',0x396bc,32),('zero',0xbdb50,8),('even',0xbd810,24),('odd',0xbd828,32)]:
            p=Path(tmp)/'data.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.math.log_'+name,'-O','binary',str(obj),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+length]
    for address,length in [(0x39688,92),(0xbdb50,8),(0xbd810,56)]:
        p=OUT/f'ghidra-{address:x}.json';assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[address-0x27000:address-0x27000+length];evidence[p.name]=sha(p)
    receipt=dict(comparisons=sum(counts.values()),counts=counts,errno_writes_per_side=errno_writes,all_binary64_exponents=True,both_signs=True,all_four_rounding_modes=True,selected_values_all_fz_dn_initial_inexact_controls=True,initial_inexact_flag_zero_and_one_selected_values=True,threshold_adjacent_bits=True,dense_numeric_grid=True,return_fpscr_stack_callee_integer_fp_errno_and_nonstack_writes_checked=True,actual_source_log_and_dependencies=True,independent_calls_reset_xpsr=True,source_owned_numeric_bytes=144,shared_existing_numeric_bytes=8,unique_new_numeric_bytes=136,runtime_no_unresolved=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),parent_layouts={path:sha(ROOT/path) for path in ['r1/source-config/runtime/native_exp_verification.ld','r1/source-config/runtime/native_expm1_verification.ld','r1/source-config/runtime/native_atan_verification.ld','r1/source-config/runtime/native_tanf_verification.ld','r1/source-config/runtime/native_sinf_verification.ld','r1/source-config/runtime/native_cosf_verification.ld','r1/source-config/runtime/native_trig_reduce_consumers.ld', 'r1/source-config/runtime/native_atan2f_verification.ld', 'r1/source-config/runtime/native_atanf_verification.ld', 'r1/source-config/runtime/native_float_logs_verification.ld', 'r1/source-config/runtime/native_expf_tanhf_verification.ld', 'r1/source-config/runtime/native_math_special_verification.ld', 'r1/source-config/runtime/native_math_round_verification.ld', 'r1/source-config/runtime/native_double_directed_verification.ld', 'r1/source-config/runtime/native_math_selection_verification.ld', 'r1/source-config/runtime/native_math_verification.ld']},driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Typed D0/FPSCR/errno/callee/nonstack checks do not establish remaining caller scratch/APSR/private frames.','Selected exponent/mantissa/threshold/grid/control cases do not exhaust input domain or physical FPU behavior.','Recovered numeric constants and verification placement are separate from original instruction/image identity.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
