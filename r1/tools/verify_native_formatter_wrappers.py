#!/usr/bin/env python3
"""Native bounded wrapper frames/registers with actual C engine execution."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-formatter-wrappers';SP=0x2003f000;DEST=0x20010000;FMT=0x20011000;STRING=0x20012000;ARGS=0x20018000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_formatter_wrappers.o';assert sha(obj)==r['units'][0]['object_sha256'];ep=BASE/'native-formatter-engine/report.json';engine=json.loads(ep.read_text());eo=ep.parent/'native-formatter-engine.o';assert sha(eo)==engine['linked_sha256'] and not engine['undefined_symbols']
    for report in [r,engine]:
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={p.name:sha(p) for p in OUT.glob('ghidra-*.json')};evidence.update({p.name:sha(p) for p in OUT.glob('rea-*.json')})
    for a,n in [(0x38080,48),(0x380dc,46)]:assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    counts={'snprintf':0,'vsnprintf':0};faults=0;r1_differences=0;alias_cases=0;digest=hashlib.sha256();callcounts={'core':0,'output':0};states={}
    with tempfile.TemporaryDirectory(prefix='r1-wrappers-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';ld=d/'layout.ld';ld.write_text('SECTIONS { .flags 0x43480 : { *(.r1.format.flags) } .lower 0x43484 : { *(.r1.format.lower) } .upper 0x43498 : { *(.r1.format.upper) } .minus 0x43728 : { *(.r1.format.minus) } .plus 0x4372c : { *(.r1.format.plus) } .space 0x43730 : { *(.r1.format.space) } .zero 0x3f6a8 : { *(.r1.format.decimal_zero) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','snprintf',str(obj),str(eo),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        def hook(u,a,size,_):
            st=states[id(u)]
            if a in [0x43080,syms['r1_format_core']&~1]:
                regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];assert regs==[FMT,st['argbase'],st['context']],(st,regs);st['counts']['core']+=1;st['context_initial']=bytes(u.mem_read(regs[2],8)).hex()
            if a in [0x43bbc,syms['r1_format_bounded_putc']&~1]:st['counts']['output']+=1
        def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size];return False
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
        fmt_cases=[(b'literal',[]),(b'%s',[('u',STRING)]),(b'%c',[('u',128)]),(b'%08x',[('u',0x123)]),(b'%+d',[('u',0x80000000)]),(b'%lld:%u',[('q',0x8000000000000000),('u',42)]),(b'%u:%llu',[('u',7),('q',0xffffffffffffffff)]),(b'%*.*s',[('u',12),('u',3),('u',STRING)]),(b'%p',[('u',STRING)]),(b'%#.0o',[('u',0)]),(b'%nX',[('u',DEST+200)])]
        for f in [b'%f',b'%e',b'%.9g',b'%#G']:
            for bits in [0,0x8000000000000000,0x400921fb54442d18,1,0x7fefffffffffffff,0x7ff0000000000000,0x7ff8000000000000]:fmt_cases.append((f,[('q',bits)]))
        cases=itertools.chain(((kind,fmt,args,capacity,destination,offset,False) for kind,(fmt,args),capacity,destination,offset in itertools.product(counts,fmt_cases,[0,1,2,8,16,128,0x80000000,0xffffffff],[DEST,0],[0,4])),((kind,b'A',[],size,SP-(40 if kind=='snprintf' else 24)+offset,0,True) for kind,size,offset in itertools.product(counts,[0,1,2],[4,5,6,7])),((kind,b'%nB',[('u',SP-(40 if kind=='snprintf' else 24)+offset)],size,DEST,0,True) for kind,offset,size in itertools.product(counts,[0,4],[0,1,8])))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for kind,fmt,args,capacity,destination,offset,alias in cases:
            results=[];frame=40 if kind=='snprintf' else 24;context=SP-frame;argbase=SP-4 if kind=='snprintf' else ARGS+offset
            for candidate,u in enumerate(machines):
                u.mem_write(DEST,b'\xa5'*256);u.mem_write(FMT,fmt+b'\0'+b'\xa5'*64);u.mem_write(STRING,b'ab\x80\xffcd\0');u.mem_write(ARGS,b'\xa5'*256);u.mem_write(SP-1024,b'\x96'*2048);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
                first=0x87654321;cursor=argbase
                for typ,value in args:
                    if typ=='q':cursor=(cursor+7)&~7;u.mem_write(cursor,struct.pack('<Q',value));cursor+=8
                    else:
                        if kind=='snprintf' and cursor==SP-4:first=value&0xffffffff
                        else:u.mem_write(cursor,struct.pack('<I',value&0xffffffff))
                        cursor+=4
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[destination,capacity,FMT,first if kind=='snprintf' else argbase]):u.reg_write(reg,value)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                st={'context':context,'argbase':argbase,'counts':dict.fromkeys(callcounts,0),'fault':None};states[id(u)]=st
                try:u.emu_start((syms[kind] if candidate else 0x38080 if kind=='snprintf' else 0x380dc)|1,0x20000100,count=2000000)
                except UcError:assert st['fault'],(kind,fmt,capacity,destination,candidate,hex(u.reg_read(UC_ARM_REG_PC)))
                if not st['fault']:
                    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP
                    if not alias:assert [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                    if capacity:assert u.reg_read(UC_ARM_REG_R1)==0
                results.append(dict(registers=None if st['fault'] else [u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R2,UC_ARM_REG_R3,*saved]],r1=None if st['fault'] else u.reg_read(UC_ARM_REG_R1),fault=st['fault'],counts=st['counts'],context_initial=st['context_initial'],outer_frame=bytes(u.mem_read(context,frame)).hex(),destination=bytes(u.mem_read(DEST,256)).hex(),arguments=bytes(u.mem_read(ARGS,256)).hex(),caller_stack=bytes(u.mem_read(SP,128)).hex()))
            r1_differences+=int(results[0]['r1']!=results[1]['r1']);r0=dict(results[0]);r1=dict(results[1]);r0.pop('r1');r1.pop('r1');assert r0==r1,(kind,fmt,args,capacity,hex(destination),offset,alias,results)
            counts[kind]+=1;faults+=int(bool(results[0]['fault']));alias_cases+=int(alias)
            for k,v in results[0]['counts'].items():callcounts[k]+=v
            digest.update(json.dumps([kind,fmt.hex(),args,capacity,destination,offset,alias,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,alias_cases=alias_cases,r1_scratch_differences=r1_differences,r1_zero_for_nonzero_capacity=True,r0_r2_r3_and_callee_saved_checked=True,native_outer_frames_checked=dict(snprintf=40,vsnprintf=24),native_argument_stream_and_context_checked=True,actual_source_engine=True,actual_source_provider_calls_per_side=callcounts,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),engine_report_sha256=sha(ep),engine_object_sha256=sha(eo),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['r1 on zero-capacity calls is observed separately; source core scratch register identity remains unresolved.','Exact native wrapper outer frame is compared; worker/parser private stack below it and arbitrary aliases remain gated.','Bounded formats and selected capacities/aliases do not exhaust all u32 inputs, callback effects or return-address corruption.','Original instruction, full image integration and hardware behavior remain unproven.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
