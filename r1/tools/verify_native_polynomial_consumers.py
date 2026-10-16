#!/usr/bin/env python3
"""Native libm consumers with source polynomial and eleven bit helpers substituted."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from verify_native_float_bits import TARGETS as BIT_TARGETS
TARGETS={**BIT_TARGETS,'polynomial':('r1_native_polynomial',0x3b40c,248,'d0')}
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-float-bits';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CONSUMERS=[('atan',0x381f0,64,1),('atan2f',0x384c8,32,2),('atanf',0x38774,32,1),('ceil',0x388d8,64,1),('ceilf',0x389f0,32,1),('cosf',0x38a5c,32,1),('exp',0x38bb0,64,1),('expf',0x38f08,32,1),('floor',0x39108,64,1),('floorf',0x39220,32,1),('log',0x39320,64,1),('log10f',0x396e4,32,1),('logf',0x39864,32,1),('pow',0x399d0,64,2),('powf',0x3a620,32,2),('round',0x3ac88,64,1),('roundf',0x3ad68,32,1),('sinf',0x3ae04,32,1),('sqrt',0x3af94,64,1),('sqrtf',0x3b00e,32,1),('tanf',0x3b048,32,1),('tanh',0x3b1c8,64,1),('tanhf',0x3b328,32,1)]
def main():
    rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_float_bits.o';assert sha(obj)==r['units'][0]['object_sha256'];mp=BASE/'native-formatter-math/report.json';m=json.loads(mp.read_text());mo=mp.parent/'native-formatter-math.o';assert sha(mo)==m['linked_sha256']
    for report in [r,m]:
        for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    bp=BASE/'native-polynomial/verification.json';bundle=json.loads(bp.read_text());bo=bp.parent/'native-polynomial-runtime.o';assert sha(bo)==bundle['runtime_object_sha256'] and bundle['runtime_no_unresolved']
    assert bundle['report_sha256']==sha(bp.parent/'report.json') and bundle['provider_report_sha256']==sha(BASE/'native-float-bits-runtime/report.json')
    for path,digest in json.loads((bp.parent/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';counts={name:0 for name,_,_,_ in CONSUMERS};helper_counts=dict.fromkeys(TARGETS,0);trace=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-float-consumers-') as tmp:
        d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .zero 0x3f6a8 : { *(.r1.format.decimal_zero) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_binary64_classify_bits',str(bo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[];mapping={address:(kind,name) for kind,(name,address,_,_) in TARGETS.items()}
        def hook(u,a,size,_):
            st=states[id(u)]
            if a in mapping:
                kind,name=mapping[a];st['helpers'][kind]+=1
                if st['source']:u.reg_write(UC_ARM_REG_PC,syms[name]|1)
        def write(u,access,address,size,value,_):
            if 0x20000000<=address<0x2003e000:states[id(u)]['writes'].append([address,size,value])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);machines.append(u)
        # Observational native cold state; this is not source startup proof.
        machines[0].reg_write(UC_ARM_REG_SP,0x2003f000);machines[0].emu_start(0x283a1,0x27208,count=2000000);assert machines[0].reg_read(UC_ARM_REG_PC)==0x27208;cold=bytes(machines[0].mem_read(0x20000000,0x40000))
        for u in machines:u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
        bits32=[0,0x80000000,1,0x7fffff,0x800000,0x3f000000,0x3f800000,0x40000000,0xbf800000,0x40490fdb,0x7f7fffff,0x7f800000,0xff800000,0x7fc00000]
        bits64=[0,0x8000000000000000,1,0xfffffffffffff,0x10000000000000,0x3fe0000000000000,0x3ff0000000000000,0x4000000000000000,0xbff0000000000000,0x400921fb54442d18,0x7fefffffffffffff,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000000]
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];dsaved=[UC_ARM_REG_D8,UC_ARM_REG_D9,UC_ARM_REG_D10,UC_ARM_REG_D11,UC_ARM_REG_D12,UC_ARM_REG_D13,UC_ARM_REG_D14,UC_ARM_REG_D15]
        for name,entry,width,arity in CONSUMERS:
            values=bits32 if width==32 else bits64
            pairs=[(a,values[(i+5)%len(values)]) for i,a in enumerate(values)] if arity==1 else list(itertools.product(values[4:10],repeat=2))
            for (a,b),rounding in itertools.product(pairs,range(4)):
                results=[]
                for candidate,u in enumerate(machines):
                    u.mem_write(0x20000000,cold);u.mem_write(0x2003e000,b'\x96'*8192);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,rounding<<22)
                    if width==32:u.reg_write(UC_ARM_REG_D0,(b<<32)|a)
                    else:u.reg_write(UC_ARM_REG_D0,a);u.reg_write(UC_ARM_REG_D1,b)
                    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[a&0xffffffff,a>>32,b&0xffffffff,b>>32]):u.reg_write(reg,value)
                    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                    for k,reg in enumerate(dsaved):u.reg_write(reg,0x123456789abcdef0+k)
                    st={'source':candidate,'helpers':dict.fromkeys(TARGETS,0),'writes':[]};states[id(u)]=st;u.emu_start(entry|1,0x20000100,count=1000000)
                    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000,(name,hex(a),hex(b),rounding,candidate,hex(u.reg_read(UC_ARM_REG_PC)))
                    assert [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)] and [u.reg_read(reg) for reg in dsaved]==[0x123456789abcdef0+k for k in range(8)]
                    results.append(dict(result=u.reg_read(UC_ARM_REG_S0 if width==32 else UC_ARM_REG_D0),fpscr=u.reg_read(UC_ARM_REG_FPSCR),helpers=st['helpers'],writes=st['writes']))
                assert results[0]==results[1],(name,hex(a),hex(b),rounding,results)
                counts[name]+=1
                for kind,value in results[0]['helpers'].items():helper_counts[kind]+=value
                trace.update(json.dumps([name,a,b,rounding,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),consumer_counts=counts,source_helper_calls=helper_counts,consumer_bodies_remain_native=True,all_four_fpscr_rounding_modes=True,return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked=True,native_initialized_state_fixture=True,trace_sha256=trace.hexdigest(),runtime_report_sha256=sha(bp),runtime_object_sha256=sha(bo),runtime_no_unresolved=True,report_sha256=sha(rp),object_sha256=sha(obj),math_report_sha256=sha(mp),math_object_sha256=sha(mo),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),instruction_identity=False,limitations=['Twenty-three native libm consumers remain native executable observations, not newly source-compiled bodies.','Native cold-state fixture and bounded values/rounding modes do not prove source startup, full-domain numerical or hardware behavior.','Other native arithmetic/helpers beyond source polynomial, complete caller-saved/APSR/private frame and image identity remain gated.'])
    (BASE/'native-polynomial/consumer-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
