#!/usr/bin/env python3
"""Native differential output contracts; private frame/scratch identity gated."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-formatter-output';SP=0x2003f000;CTX=0x20010000;DST=CTX+64
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_formatter_output.o';assert sha(obj)==r['units'][0]['object_sha256']
    for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    evidence={}
    for a,n in [(0x43734,36),(0x43758,46),(0x43bbc,22)]:
        for prefix in ['rea','ghidra']:
            p=OUT/f'{prefix}-{a:x}.json';evidence[p.name]=sha(p)
            if prefix=='ghidra':assert bytes(json.loads(p.read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    digest=hashlib.sha256();counts={'left':0,'width':0,'putc':0};prefix_cases=0;faults=0;calls=0
    with tempfile.TemporaryDirectory(prefix='r1-format-output-') as tmp:
        elf=Path(tmp)/'test.elf';binary=Path(tmp)/'test.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','-e','r1_format_bounded_putc',str(obj),'-o',str(elf)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
        machines=[];states={};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def hook(u,address,size,_):
            if address!=0x1100000:return
            st=states[id(u)];st['trace'].append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
            if len(st['trace'])==16:st['prefix']=True;u.emu_stop();return
            for reg,value in [(UC_ARM_REG_R0,len(st['trace'])*997),(UC_ARM_REG_R1,0xdeadbeef),(UC_ARM_REG_R2,0x76543210),(UC_ARM_REG_R3,0xfedcba98)]:u.reg_write(reg,value)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size];return False
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
        padding=itertools.chain(((kind,3,flags|((flags&1)<<16)) for kind,flags in itertools.product(['left','width'],range(65536))),((kind,count,flags) for kind,count,flags in itertools.product(['left','width'],[0,1,2,7,0xffffffff,0xfffffffe,0x80000001,0x80000000,0x7fffffff],[0,0x2000,0x10000,0x12000,0xffffffff])))
        putc=(('putc',byte,dest,capacity) for byte,dest,capacity in itertools.product([*range(256),256,0x12345678,0xffffffff],[DST,CTX-1,*range(CTX,CTX+8),0],[0,1,2,3,0xffffffff]))
        for case in itertools.chain(padding,putc):
            kind=case[0];results=[]
            for candidate,u in enumerate(machines):
                u.mem_write(CTX-16,b'\xa5'*160);u.mem_write(SP-128,b'\x96'*256);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                st={'trace':[],'prefix':False,'fault':None};states[id(u)]=st
                if kind=='putc':
                    _,byte,dest,capacity=case;u.mem_write(CTX,struct.pack('<II',dest,capacity));regs=[byte,CTX,0x87654321,0x12345678];entry=syms['r1_format_bounded_putc'] if candidate else 0x43bbc
                else:
                    _,count,flags=case;regs=[count,flags,CTX,0x1100001];entry=syms['r1_format_'+kind+'_padding'] if candidate else 0x43734 if kind=='left' else 0x43758
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,value)
                try:u.emu_start(entry|1,0x20000100,count=10000)
                except UcError:assert st['fault']
                if not st['fault'] and not st['prefix']:
                    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP
                    assert [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                results.append(dict(trace=st['trace'],prefix=st['prefix'],fault=st['fault'],result=None if st['prefix'] or st['fault'] else u.reg_read(UC_ARM_REG_R0),memory=bytes(u.mem_read(CTX-16,160)).hex()))
            assert results[0]==results[1],(case,results)
            counts[kind]+=1;prefix_cases+=int(results[0]['prefix']);faults+=int(bool(results[0]['fault']));calls+=len(results[0]['trace']);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_calls_per_side=calls,callback_prefix_only_cases=prefix_cases,prefix_callback_limit=16,matching_faults=faults,all_low16_flag_patterns=True,all_byte_values=True,context_aliases_checked=True,callback_scratch_clobbers_and_results_ignored=True,r0_stack_and_callee_saved_checked=True,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['INT_MIN/INT_MAX active padding paths compare first 16 callback observations only; complete multi-billion-iteration execution is unproven.','Callback is a modeled boundary. Private stack aliases, exact callback-frame bytes and caller-saved r1/r2/r3 identity remain gated.','Bounded output manual ownership row lacks extent; 22-byte body bound from native return/disassembly and live Ghidra bytes.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
