#!/usr/bin/env python3
"""Native/C parser comparison with real source math and explicit output callbacks."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-formatter-core';SP=0x2003f000;FMT=0x20010000;ARGS=0x20011000;STR=0x20012000;TARGET=0x20013000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cases():
    flags=[''.join(c for k,c in enumerate(' #+-0') if n&(1<<k)) for n in range(32)]
    for code,length,value,flag,width,precision in itertools.product('diuoxXp',['','h','hh','l','ll','j','t','z','L'],[0,42,0xffffffffffffffff],flags,['','8'],['','.0','.4']):
        yield ('integer',('%'+flag+width+precision+length+code).encode(),[('q' if length in ['ll','j'] else 'u',value)],0,ARGS)
    for code,length,value,width,precision in itertools.product('diuoxXp',['','h','hh','ll'],[1,0x80000000,0x8000000000000000],[-12,0,12],[-1,0,5]):
        yield ('stars',('%#0*.*'+length+code).encode(),[('u',width&0xffffffff),('u',precision&0xffffffff),('q' if length=='ll' else 'u',value)],0,ARGS+4)
    for code,bits,precision,flag,width in itertools.product('eEfFgG',[0,0x8000000000000000,0x3ff0000000000000,0x400921fb54442d18,1,0x7fefffffffffffff,0x7ff0000000000000,0x7ff8000000000000],['','.0','.3','.17'],['','+','#','-0'],['','24']):
        yield ('float',('%'+flag+width+precision+code).encode(),[('q',bits)],0,ARGS)
    for code,value,precision,width in itertools.product('cs',[0,65,128,255],['','.0','.3'],['','12','-12','012']):
        yield ('string',('%'+width+precision+code).encode(),[('u',STR if code=='s' else value)],0,ARGS)
    for byte in range(1,256):yield ('literal',bytes([byte]),[],0,ARGS)
    for length in ['','h','hh','l','ll','j','z','t','L']:
        for offset in [0,1,3,4]:yield ('count',('abc%'+length+'n|%08x').encode(),[('u',TARGET+offset),('u',42)],0,ARGS)
        yield ('null-count',('%'+length+'n').encode(),[('u',0)],0,ARGS)
    for fmt in [b'%',b'%ll',b'%L',b'%a',b'%q',b'%v',b'%%',b'%ls',b'%Lc',b'%hhq']:
        yield ('unknown',fmt,[('u',STR)],0,ARGS)
    for fmt,args in [(b'%s',[('u',0)]),(b'%.0s',[('u',0)]),(b'%c:%d:%lld',[('u',0),('u',0xffffffff),('q',0x8000000000000000)]),(b'%n%d',[('u',ARGS+4),('u',42)])]:yield ('edge',fmt,args,0,ARGS)
    for fmt,args,mode in itertools.product([b'A%d',b'%12s|%d',b'%-12s:%u'],[[('u',STR),('u',42)]],range(4)):yield ('mutation',fmt,args,mode,ARGS)

def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_formatter_core.o';assert sha(obj)==r['units'][0]['object_sha256'];objects=[obj];providers={}
    for directory,name,key in [('native-formatter-math','native-formatter-math.o','linked_sha256'),('native-formatter-output','native_formatter_output.o',None)]:
        p=BASE/directory/'report.json';report=json.loads(p.read_text());o=p.parent/name;assert sha(o)==(report[key] if key else report['units'][0]['object_sha256']);objects.append(o);providers[str(p.relative_to(BASE))]=sha(p)
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={p.name:sha(p) for p in OUT.glob('ghidra-*.json')};evidence['rea-43080.json']=sha(OUT/'rea-43080.json')
    raw=json.loads((OUT/'rea-43080.json').read_text());rea=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'));assert rea['normalized_result']['body']['total_bytes']==1656
    for a,n in [(0x43080,484),(0x43266,536),(0x434ac,636),(0x43480,44),(0x43728,12)]:assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    counts={};trace=hashlib.sha256();callback_calls=0;faults=0;states={}
    with tempfile.TemporaryDirectory(prefix='r1-core-') as tmp:
        d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .flags 0x43480 : { *(.r1.format.flags) } .lower 0x43484 : { *(.r1.format.lower) } .upper 0x43498 : { *(.r1.format.upper) } .minus 0x43728 : { *(.r1.format.minus) } .plus 0x4372c : { *(.r1.format.plus) } .space 0x43730 : { *(.r1.format.space) } .zero 0x3f6a8 : { *(.r1.format.decimal_zero) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_format_core',*map(str,objects),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        def hook(u,address,size,_):
            if address!=0x1100000:return
            st=states[id(u)];st['output'].append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);assert len(st['output'])<1024
            if len(st['output'])==1:
                if st['mode']==1:u.mem_write(FMT+2,b'x')
                if st['mode']==2:u.mem_write(ARGS+4,struct.pack('<I',99))
                if st['mode']==3:u.mem_write(STR,b'X\0YZ')
            for reg,value in [(UC_ARM_REG_R0,0xffffffff-len(st['output'])),(UC_ARM_REG_R1,0x87654321),(UC_ARM_REG_R2,0x76543210),(UC_ARM_REG_R3,0xfedcba98)]:u.reg_write(reg,value)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size];return False
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for group,fmt,args,mode,argbase in cases():
            results=[]
            for candidate,u in enumerate(machines):
                u.mem_write(FMT,fmt+b'\0'+b'\xa5'*128);u.mem_write(ARGS,b'\xa5'*128);u.mem_write(STR,b'ab\x80\xffcd\0'+b'\xa5'*64);u.mem_write(TARGET,b'\xa5'*32);u.mem_write(SP-1024,b'\x96'*2048)
                cursor=argbase
                for kind,value in args:
                    if kind=='q':cursor=(cursor+7)&~7;u.mem_write(cursor,struct.pack('<Q',value));cursor+=8
                    else:u.mem_write(cursor,struct.pack('<I',value&0xffffffff));cursor+=4
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[FMT,argbase,TARGET,0x1100001]):u.reg_write(reg,value)
                u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                st={'output':[],'fault':None,'mode':mode};states[id(u)]=st
                try:u.emu_start((syms['r1_format_core'] if candidate else 0x43080)|1,0x20000100,count=2000000)
                except UcError:assert st['fault'],(group,fmt,args,candidate,hex(u.reg_read(UC_ARM_REG_PC)))
                if not st['fault']:
                    assert u.reg_read(UC_ARM_REG_PC)==0x20000100,(group,fmt,args,candidate,hex(u.reg_read(UC_ARM_REG_PC)))
                    assert u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                results.append(dict(result=None if st['fault'] else u.reg_read(UC_ARM_REG_R0),output=st['output'],fault=st['fault'],target=bytes(u.mem_read(TARGET,32)).hex(),arguments=bytes(u.mem_read(ARGS,128)).hex()))
            assert results[0]==results[1],(group,fmt,args,mode,argbase,results)
            counts[group]=counts.get(group,0)+1;faults+=int(bool(results[0]['fault']));callback_calls+=len(results[0]['output']);trace.update(json.dumps([group,fmt.hex(),args,mode,argbase,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_calls_per_side=callback_calls,matching_faults=faults,all_flag_subsets=True,length_modifiers=['','h','hh','l','ll','j','t','z','L'],negative_dynamic_precision=True,varargs_64bit_alignment=True,callback_unsigned_byte_arguments_checked=True,callback_scratch_clobbers_and_returns_ignored=True,callback_mutation_modes=4,actual_source_math_and_padding=True,r0_stack_and_callee_saved_checked=True,trace_sha256=trace.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),provider_reports=providers,driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Output callback is an explicit boundary fixture; complete callback/private native136-byte frame alias identity remains gated.','Bounded widths/precisions and input corpus do not exhaust arbitrary u32 overflow/long-running formats or all callback mutations.','Caller-saved r1/r2/r3, APSR and original instruction identity remain unproven.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
