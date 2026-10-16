#!/usr/bin/env python3
"""Actual native/source RTT wrapper, initializer, pinned ring writing and copy."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-rtt-write';CB=0x2002e62c;SP=0x2003f000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vp=OUT/'stdout-integration-verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_rtt_write.o';assert sha(obj)==r['units'][0]['object_sha256'];objects=[obj];providers={}
    for directory,name,key in [('sdk-segger-rtt','segger-rtt.o','selected_object_sha256'),('runtime','memory-runtime.o','relocatable_sha256'),('native-formatter-engine','native-formatter-engine.o','linked_sha256'),('native-formatter-stream','native_formatter_stream.o',None)]:
        path=BASE/directory/'report.json';q=json.loads(path.read_text());o=path.parent/name;assert sha(o)==(q[key] if key else q['units'][0]['object_sha256']);objects.append(o);providers[str(path.relative_to(BASE))]=sha(path)
        for p,d in q['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
    sp=BASE/'native-formatter-stdio/report.json';stdio=json.loads(sp.read_text());so=sp.parent/'native-formatter-stdio.o';assert sha(so)==stdio['linked_sha256'] and not stdio['undefined_symbols']
    for path,digest in stdio['inputs'].items():assert sha(ROOT/path)==digest,path
    providers['native-formatter-stdio/report.json']=sha(sp);objects=[so]
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';assert bytes(json.loads((OUT/'ghidra-319e0.json').read_text())['data'])==app.read_bytes()[0x319e0-0x27000:0x31a14-0x27000]
    count=0;init_count=0;trace=hashlib.sha256();states={};privileged={0:0,1:0};writes=0;r1_differences=0
    with tempfile.TemporaryDirectory(prefix='r1-rtt-write-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';ld=d/'layout.ld';ld.write_text('SECTIONS { .bss._SEGGER_RTT 0x2002e62c (NOLOAD) : { *(.bss._SEGGER_RTT) } .r1.rtt.up 0x2002e6a4 (NOLOAD) : { *(.r1.rtt.up) } .r1.rtt.down 0x2002e8a4 (NOLOAD) : { *(.r1.rtt.down) } .r1.rtt.terminal 0x36dbc : { *(.r1.rtt.terminal) } .r1.rtt.identifier 0x9ca04 : { *(.r1.rtt.identifier) } .flags 0x43480 : { *(.r1.format.flags) } .lower 0x43484 : { *(.r1.format.lower) } .upper 0x43498 : { *(.r1.format.upper) } .minus 0x43728 : { *(.r1.format.minus) } .plus 0x4372c : { *(.r1.format.plus) } .space 0x43730 : { *(.r1.format.space) } .zero 0x3f6a8 : { *(.r1.format.decimal_zero) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_stdout_write',*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['_SEGGER_RTT']==CB;machines=[]
        def hook(u,a,size,_):
            st=states[id(u)]
            if a in [0x36d68,syms['SEGGER_RTT_Init']&~1]:st['init']+=1
            if a in [0x31a18,syms['SEGGER_RTT_WriteNoLock']&~1]:st['calls'].append([u.reg_read(UC_ARM_REG_BASEPRI),u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(u.reg_read(UC_ARM_REG_R1),1)).hex(),u.reg_read(UC_ARM_REG_R2)])
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
        forms=[(b'literal',[]),(b'%s',[('u',0x20004000)]),(b'%c',[('u',128)]),(b'%d:%#x',[('u',0xffffffff),('u',0x123)]),(b'%lld:%u',[('q',0x8000000000000000),('u',42)]),(b'%*.*s',[('u',12),('u',3),('u',0x20004000)])]
        for fmt,bits in itertools.product([b'%f',b'%.9g',b'%e'],[0,0x8000000000000000,0x400921fb54442d18,1,0x7fefffffffffffff,0x7ff0000000000000,0x7ff8000000000000]):forms.append((fmt,[('q',bits)]))
        cases=((fmt,args,cold,size,mode,basepri,control) for (fmt,args),(cold,size,mode),basepri,control in itertools.product(forms,[(True,512,0),(False,7,0),(False,7,1),(False,64,0),(False,64,1),(False,64,2)],[0,32,255],range(2)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for fmt,args,cold,size,mode,basepri,control in cases:
            fill=0xa5;channel=0;rd=0;wr=0;length=0
            results=[]
            for candidate,u in enumerate(machines):
                u.mem_write(CB,bytes([fill])*696);u.mem_write(0x20002000,b'\x96'*1024);u.mem_write(0x20003000,bytes(range(64)))
                if not cold:
                    u.mem_write(CB,b'S'+b'\xa7'*15+struct.pack('<II',2,2));u.mem_write(CB+24+channel*24,struct.pack('<6I',0,0x20002000,size,wr,rd,mode))
                u.mem_write(SP-256,b'\x96'*512);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_CONTROL,control);u.reg_write(UC_ARM_REG_BASEPRI,basepri)
                u.mem_write(0x20004000,b'ab\x80\xffcd\0');u.mem_write(0x20005000,fmt+b'\0');slots={};slot=1
                for typ,value in args:
                    if typ=='q':slot=(slot+1)&~1;slots[slot]=value&0xffffffff;slots[slot+1]=value>>32;slot+=2
                    else:slots[slot]=value&0xffffffff;slot+=1
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x20005000,slots.get(1,0x87654321),slots.get(2,0x76543210),slots.get(3,0xabcdef01)]):u.reg_write(reg,value)
                for n,value in slots.items():
                    if n>=4:u.mem_write(SP+(n-4)*4,struct.pack('<I',value))
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                st={'calls':[],'init':0};states[id(u)]=st;u.emu_start((syms['printf'] if candidate else 0x38060)|1,0x20000100,count=2000000)
                assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                results.append(dict(result=u.reg_read(UC_ARM_REG_R0),r1=u.reg_read(UC_ARM_REG_R1),basepri=u.reg_read(UC_ARM_REG_BASEPRI),control=u.reg_read(UC_ARM_REG_CONTROL),init=st['init'],calls=st['calls'],rtt=bytes(u.mem_read(CB,696)).hex(),buffer=bytes(u.mem_read(0x20002000,1024)).hex()))
            r1_differences+=int(results[0]['r1']!=results[1]['r1']);a=dict(results[0]);b=dict(results[1]);a.pop('r1');b.pop('r1');assert a==b,(fmt,args,cold,size,mode,basepri,control,results)
            count+=1;init_count+=results[0]['init'];writes+=len(results[0]['calls']);privileged[control]+=1;trace.update(json.dumps([fmt.hex(),args,cold,size,mode,basepri,control,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=count,initializations_per_side=init_count,no_lock_calls_per_side=writes,control_mode_cases=privileged,basepri_values=[0,32,255],actual_source_initializer=True,actual_pinned_segger_ring=True,actual_source_memory_copy=True,r0_basepri_control_and_callee_saved_checked=True,r1_scratch_differences=r1_differences,actual_source_printf=True,stdout_backend_fixture=False,trace_sha256=trace.hexdigest(),stdio_report_sha256=sha(sp),stdio_object_sha256=sha(so),stdio_no_unresolved=True,report_sha256=sha(rp),object_sha256=sha(obj),provider_reports=providers,driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in [OUT/'rea-319e0.json',OUT/'ghidra-319e0.json']},instruction_identity=False,limitations=['Blocking mode is tested only with enough free space; live debugger drain and concurrent host/device updates remain gated.','Unicorn CONTROL/BASEPRI observations do not prove physical privilege/interrupt timing.','Printf caller-saved scratch, callback frame addresses and private frame identity remain gated; backend payloads, RTT data and BASEPRI are compared. Whole-image/hardware delivery remain unproven.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
