#!/usr/bin/env python3
"""Differential formatter experiment with explicit heap/lock boundary fixtures."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/newlib-stdio';SP=0x2003f000;DEST=0x20010000;FMT=0x20011000;STRING=0x20012000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=OUT/'formatter-experiment.json';receipt.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'newlib-stdio.o';assert sha(obj)==report['relocatable_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    evidence={p.name:sha(p) for p in [OUT/'rea-38080.json',OUT/'ghidra-38080.json']}
    assert bytes(json.loads((OUT/'ghidra-38080.json').read_text())['data'])==app.read_bytes()[0x11080:0x110b0]
    with tempfile.TemporaryDirectory(prefix='r1-newlib-formatter-') as tmp:
        d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';text=d/'text.bin';data=d/'data.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .data 0x20020000 : { *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
        link=subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','snprintf','--defsym=__assert_func=0x1100101','--defsym=__malloc_lock=0x1100201','--defsym=__malloc_unlock=0x1100301','--defsym=_sbrk_r=0x1100401',str(obj),'-o',str(elf)],check=True,capture_output=True,text=True)
        for section,path in [('.text',text),('.data',data)]:subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(path)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
        state={};native_reads=set()
        def hook(u,addr,size,_):
            if addr==0x1100100:raise AssertionError('Newlib assertion reached')
            if addr in [0x1100200,0x1100300,0x1100400]:
                state['calls'][hex(addr)]=state['calls'].get(hex(addr),0)+1
                if addr==0x1100400:
                    amount=u.reg_read(UC_ARM_REG_R1);amount=amount if amount<0x80000000 else amount-0x100000000;old=state['brk'];new=old+amount
                    if not 0x20028000<=new<=0x20038000:u.reg_write(UC_ARM_REG_R0,0xffffffff)
                    else:state['brk']=new;u.reg_write(UC_ARM_REG_R0,old)
                u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,hook)
        def read_hook(u,access,address,size,value,_):
            if state.get('candidate') or not 0x20000000<=address<0x20040000:return
            if SP-4096<=address<SP+1024 or DEST<=address<DEST+256 or FMT<=address<FMT+256 or STRING<=address<STRING+64:return
            native_reads.add((address,size))
        u.hook_add(UC_HOOK_MEM_READ,read_hook)
        cases=[(b'%s',[('u',STRING)]),(b'literal',[]),(b'%d',[('u',0xffffffff)]),(b'%u',[('u',0xffffffff)]),(b'%08x',[('u',0x123)]),(b'%#x',[('u',0x123)]),(b'%+06d',[('u',42)]),(b'%.*s',[('u',3),('u',STRING)]),(b'%*d',[('u',8),('u',123)]),(b'%p',[('u',STRING)]),(b'%lld',[('q',0x8000000000000000)]),(b'%llu',[('q',0xffffffffffffffff)]),(b'%s:%08x:%d',[('u',STRING),('u',0xabc),('u',0xfffffff9)])]
        for fmt in [b'%f',b'%.9g',b'%e',b'%a']:
            for bits in [0,0x8000000000000000,0x3ff0000000000000,0x400921fb54442d18,1,0x7fefffffffffffff,0x7ff0000000000000,0x7ff8000000000000]:cases.append((fmt,[('q',bits)]))
        differences=[];errors=[];compared=0;matched=0;trace=hashlib.sha256();provider_calls={}
        for index,(fmt,args) in enumerate(cases):
            for capacity in [0,1,4,16,128]:
                results=[]
                for candidate in [False,True]:
                    u.mem_write(0x20000000,bytes(0x40000));u.mem_write(0x20020000,data.read_bytes());u.mem_write(DEST,b'\xa5'*256);u.mem_write(FMT,fmt+b'\0');u.mem_write(STRING,b'2.2.6.0009\0');u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
                    vals={};slot=3
                    for kind,value in args:
                        if kind=='q':slot=(slot+1)&~1;vals[slot]=value&0xffffffff;vals[slot+1]=value>>32;slot+=2
                        else:vals[slot]=value;slot+=1
                    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[DEST,capacity,FMT,vals.get(3,0x87654321)]):u.reg_write(reg,value)
                    for n,value in vals.items():
                        if n>=4:u.mem_write(SP+(n-4)*4,struct.pack('<I',value))
                    state.update(brk=0x20028000,calls={},candidate=candidate)
                    for k,reg in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]):u.reg_write(reg,0x12345600+k)
                    try:
                        u.emu_start((syms['snprintf'] if candidate else 0x38080)|1,0x20000100,count=500000)
                        assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP
                        assert [u.reg_read(reg) for reg in [UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]]==[0x12345600+k for k in range(8)]
                        result=dict(return_value=u.reg_read(UC_ARM_REG_R0),buffer=bytes(u.mem_read(DEST,256)).hex())
                    except (UcError,AssertionError) as exc:result=dict(error=str(exc),pc=hex(u.reg_read(UC_ARM_REG_PC)))
                    if candidate:
                        for name,count in state['calls'].items():provider_calls[name]=provider_calls.get(name,0)+count
                    results.append(result)
                compared+=1;trace.update(json.dumps([index,capacity,results],sort_keys=True).encode())
                row=dict(format=fmt.decode(),arguments=args,capacity=capacity,native=results[0],candidate=results[1])
                if any('error' in r for r in results):errors.append(row)
                elif results[0]!=results[1]:differences.append(row)
                else:matched+=1
    r=dict(native_sram_reads_outside_arguments_output_and_stack=[dict(address=hex(a),size=n) for a,n in sorted(native_reads)],callee_saved_registers_checked=True,link_diagnostics=link.stderr,cases=compared,matched=matched,differences=differences,execution_errors=errors,provider_calls=provider_calls,report_sha256=sha(rp),object_sha256=sha(obj),application_sha256=sha(app),evidence=evidence,driver_sha256=sha(Path(__file__)),trace_sha256=trace.hexdigest(),native_equivalence_proven=False,instruction_identity=False,limitations=['Heap growth and locks are explicit Unicorn boundary fixtures, not source providers or firmware allocation contracts. Assertion entry fails the experiment.','Fresh zeroed SRAM and source initialized Newlib data per case; no native startup or concurrent locale/heap state proof.','Compare r0, output bytes and stack return only; caller-saved scratch registers are not identity evidence.','Bounded format corpus is an experiment, not generic formatter coverage.'])
    receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['cases','matched','provider_calls','trace_sha256']}));print('differences',len(differences),'execution errors',len(errors))
if __name__=='__main__':main()
