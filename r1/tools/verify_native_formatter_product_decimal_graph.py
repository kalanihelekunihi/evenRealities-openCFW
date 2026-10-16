#!/usr/bin/env python3
"""Compare recovered C decimal control flow with native arithmetic executing."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-formatter-product';DOUT=BASE/'native-formatter-decimal';SP=0x2003f000;BUF=0x20010000;RESULT=BUF+64
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vp=OUT/'decimal-integration-verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_formatter_product.o';assert sha(obj)==report['units'][0]['object_sha256']
    ap=BASE/'native-formatter-add/report.json';ar=json.loads(ap.read_text());addition=ap.parent/'native_formatter_add.o';assert sha(addition)==ar['units'][0]['object_sha256']
    up=BASE/'native-formatter-unsigned/report.json';ur=json.loads(up.read_text());unsigned=up.parent/'native_formatter_unsigned.o';assert sha(unsigned)==ur['units'][0]['object_sha256']
    dp=DOUT/'report.json';dr=json.loads(dp.read_text());decimal=DOUT/'native_formatter_decimal.o';assert sha(decimal)==dr['units'][0]['object_sha256']
    ip=BASE/'integer-runtime/report.json';ir=json.loads(ip.read_text());integer=ip.parent/'integer-runtime.o';assert sha(integer)==ir['relocatable_sha256']
    for r in [report,ir,dr,ur,ar]:
        for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    evidence={p.name:sha(p) for p in [DOUT/'rea-3f530.json',DOUT/'ghidra-3f530.json',DOUT/'ghidra-3f6a0.json']}
    for a,n in [(0x3f530,366),(0x3f6a0,20)]:assert bytes(json.loads((DOUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    helpers={0x27c4a:'multiply',0x27d2e:'divide',0x27afc:'add',0x28334:'to_unsigned'};counts={k:0 for k in helpers.values()};digest=hashlib.sha256();comparisons=0;zero_cases=0;aliases=0
    with tempfile.TemporaryDirectory(prefix='r1-decimal-') as tmp:
        d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';zero=d/'zero.bin';ld.write_text('SECTIONS { .zero 0x3f6a8 : { *(.r1.format.decimal_zero) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
        cmd=['arm-none-eabi-ld','-T',str(ld),'-e','r1_format_decimal_digits']
        for name,address in []:cmd+=['--defsym=r1_format_double_'+name+'_bits='+hex(address)]
        subprocess.run([*cmd,str(obj),str(addition),str(unsigned),str(decimal),str(integer),'-o',str(elf)],check=True,capture_output=True)
        for section,path in [('.text',binary),('.zero',zero)]:subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(path)],check=True)
        assert zero.read_bytes()==app.read_bytes()[0x3f6a8-0x27000:0x3f6ac-0x27000]
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};helpers[syms['r1_format_double_to_unsigned_bits']&~1]='to_unsigned';helpers[syms['r1_format_double_add_bits']&~1]='add';helpers[syms['r1_format_double_multiply_bits']&~1]='multiply';helpers[syms['r1_format_double_divide_bits']&~1]='divide';machines=[];states={}
        def hook(u,address,size,_):
            st=states[id(u)]
            target={0x27fd0:'r1_format_signed_shift_bits',0x28122:'r1_format_double_round_bits',0x28140:'r1_format_double_normalize_bits'}.get(address)
            if st['candidate'] and target:u.reg_write(UC_ARM_REG_PC,syms[target]|1);return
            if address in helpers:
                st=states[id(u)];st['counts'][helpers[address]]+=1
                st['trace'].append([helpers[address],*[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]][:2 if helpers[address]=='to_unsigned' else 4]])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
        edge=[0,1,0xfffffffffffff,0x10000000000000,0x3ff0000000000000,0x3fefffffffffffff,0x3ff0000000000001,0x400921fb54442d18,0x7fefffffffffffff,0x7ff0000000000000,0x7ff0000000000001,0x7ff8000000000000,0x7fffffffffffffff]
        rng=random.Random(0x3f530);edge += [rng.getrandbits(63) for _ in range(64)]
        cases=itertools.chain(((bits,precision,mode,RESULT) for bits,(precision,mode) in itertools.product(edge,[(1,0),(6,0),(17,0),(0,1),(6,1),(20,1)])),((exponent<<52,precision,mode,RESULT) for exponent,(precision,mode) in itertools.product(range(2048),[(17,0),(6,1)])),((bits,precision,mode,result) for bits,(precision,mode),result in itertools.product(edge[:13],[(1,0),(17,0),(0,1),(6,1)],[BUF-4,BUF,BUF+1,BUF+8,BUF+16])))
        for bits,precision,mode,result in cases:
            results=[]
            for candidate,u in enumerate(machines):
                u.mem_write(BUF-16,b'\xa5'*160);u.mem_write(SP-512,b'\x96'*1024);u.mem_write(SP,struct.pack('<II',precision,mode));u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
                regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
                for reg,value in zip(regs,[result,BUF,bits&0xffffffff,bits>>32]):u.reg_write(reg,value)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                st={'candidate':candidate,'counts':dict.fromkeys(counts,0),'trace':[]};states[id(u)]=st
                u.emu_start((syms['r1_format_decimal_digits'] if candidate else 0x3f530)|1,0x20000100,count=2000000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100,(hex(bits),precision,mode,candidate,hex(u.reg_read(UC_ARM_REG_PC)))
                assert u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                results.append(dict(result=u.reg_read(UC_ARM_REG_R0),memory=bytes(u.mem_read(BUF-16,160)).hex(),trace=st['trace'],counts=st['counts']))
            assert results[0]==results[1],(hex(bits),precision,mode,hex(result),results)
            comparisons+=1;zero_cases+=int(bits==0);aliases+=int(result!=RESULT)
            for name,count in results[0]['counts'].items():counts[name]+=count
            digest.update(json.dumps([bits,precision,mode,result,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=comparisons,zero_cases=zero_cases,result_buffer_alias_cases=aliases,native_math_calls_per_side=counts,all_nonnegative_binary64_exponents=True,precision_modes_tested=[[1,0],[6,0],[17,0],[0,1],[6,1],[20,1]],source_owned_zero_bytes=4,native_math_argument_traces_checked=True,actual_source_integer_division=True,r0_stack_and_callee_saved_checked=True,trace_sha256=digest.hexdigest(),addition_report_sha256=sha(ap),addition_object_sha256=sha(addition),unsigned_report_sha256=sha(up),unsigned_object_sha256=sha(unsigned),decimal_report_sha256=sha(dp),decimal_object_sha256=sha(decimal),report_sha256=sha(rp),object_sha256=sha(obj),integer_report_sha256=sha(ip),integer_object_sha256=sha(integer),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Every decimal binary64 arithmetic provider now executes C source, along with integer division and shifts. This does not establish whole-image source or instruction closure.','Native caller clears sign before this entry; direct corpus covers nonnegative binary64 patterns only.','Signed-overflow precision/extreme mode paths, callback/private stack aliases and r1/r2/r3 scratch identity remain gated.','No whole-image or hardware proof.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
