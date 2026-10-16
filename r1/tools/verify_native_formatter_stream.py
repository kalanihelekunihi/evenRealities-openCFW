#!/usr/bin/env python3
"""Native/source string/stdout formatting; backend remains an explicit boundary."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-formatter-stream';SP=0x2003f000;D=0x20010000;F=D+0x1000;S=D+0x2000;C=D+0x3000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_formatter_stream.o';assert sha(obj)==r['units'][0]['object_sha256'];ep=BASE/'native-formatter-engine/report.json';engine=json.loads(ep.read_text());eo=ep.parent/'native-formatter-engine.o';assert sha(eo)==engine['linked_sha256'] and not engine['undefined_symbols']
    for report in [r,engine]:
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={p.name:sha(p) for p in OUT.glob('ghidra-*.json')};evidence.update({p.name:sha(p) for p in OUT.glob('rea-*.json')})
    for a,n in [(0x38060,22),(0x380b4,34),(0x44a6c,10),(0x6570a,16)]:assert bytes(json.loads((OUT/f'ghidra-{a:x}.json').read_text())['data'])==app.read_bytes()[a-0x27000:a-0x27000+n]
    counts=dict(sprintf=0,printf=0,buffer_putc=0,stdout_putc=0);calls={'native':0,'source':0};r1_differences=0;faults=0;digest=hashlib.sha256();states={}
    with tempfile.TemporaryDirectory(prefix='r1-stream-') as tmp:
        d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';leaf=d/'putc.bin';ld=d/'layout.ld';ld.write_text('SECTIONS { .flags 0x43480 : { *(.r1.format.flags) } .lower 0x43484 : { *(.r1.format.lower) } .upper 0x43498 : { *(.r1.format.upper) } .minus 0x43728 : { *(.r1.format.minus) } .plus 0x4372c : { *(.r1.format.plus) } .space 0x43730 : { *(.r1.format.space) } .zero 0x3f6a8 : { *(.r1.format.decimal_zero) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
        subprocess.run(['arm-none-eabi-objcopy','-j','.text.r1_format_unbounded_putc','-O','binary',str(obj),str(leaf)],check=True);assert leaf.read_bytes()==app.read_bytes()[0x44a6c-0x27000:0x44a76-0x27000];leaf_hash=sha(leaf)
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','sprintf','--defsym=r1_stdout_write=0x1100001',str(obj),str(eo),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
        syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
        def hook(u,a,size,_):
            if a not in [0x319e0,0x1100000]:return
            st=states[id(u)];r=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];assert r[0]==0 and r[2]==1
            record=bytes(u.mem_read(r[1],8));st['trace'].append([r[1],record.hex()]);calls[st['side']]+=1
            if st['mode']==1:u.mem_write(r[1],struct.pack('<II',0x12345678,0xabcdef01))
            elif st['mode']==2:u.mem_write(r[1],bytes([0x80]));u.mem_write(r[1]+4,struct.pack('<I',0x77777777))
            for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0xffffffff,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size];return False
        for _ in range(2):
            u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
        forms=[(b'literal',[]),(b'%s',[('u',S)]),(b'%c',[('u',128)]),(b'%d:%#x',[('u',0xffffffff),('u',0x123)]),(b'%lld:%u',[('q',0x8000000000000000),('u',42)]),(b'%*.*s',[('u',12),('u',3),('u',S)]),(b'%nZ',[('u',D+200)])]
        for fmt,bits in itertools.product([b'%f',b'%.9g',b'%e'],[0,0x8000000000000000,0x400921fb54442d18,1,0x7fefffffffffffff,0x7ff0000000000000,0x7ff8000000000000]):forms.append((fmt,[('q',bits)]))
        wrapper_cases=((kind,fmt,args,mode,extra) for kind,(fmt,args),mode,extra in itertools.product(['sprintf','printf'],forms,range(3),[0,1]))
        leaf_cases=(('buffer_putc',b'',[],0,(byte,dest)) for byte,dest in itertools.product([*range(256),256,0x12345678,0xffffffff],[D,C,C+1,C+2,C+3,0]))
        stdout_cases=(('stdout_putc',b'',[],mode,(byte,ctx)) for byte,ctx,mode in itertools.product([*range(256),0x12345678,0xffffffff],[0,0x20007db8,0xffffffff],range(3)))
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        for kind,fmt,args,mode,extra in itertools.chain(wrapper_cases,leaf_cases,stdout_cases):
            results=[]
            for candidate,u in enumerate(machines):
                u.mem_write(D,b'\xa5'*256);u.mem_write(C,b'\xa5'*32);u.mem_write(F,fmt+b'\0'+b'\xa5'*64);u.mem_write(S,b'ab\x80\xffcd\0');u.mem_write(SP-1024,b'\x96'*2048);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
                for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
                if kind in ['sprintf','printf']:
                    slots={};slot=2 if kind=='sprintf' else 1
                    for typ,value in args:
                        if typ=='q':slot=(slot+1)&~1;slots[slot]=value&0xffffffff;slots[slot+1]=value>>32;slot+=2
                        else:slots[slot]=value&0xffffffff;slot+=1
                    if kind=='sprintf':regs=[0 if extra else D,F,slots.get(2,0x87654321),slots.get(3,0x76543210)]
                    else:regs=[F,slots.get(1,0x87654321),slots.get(2,0x76543210),slots.get(3,0xabcdef01)]
                    for n,value in slots.items():
                        if n>=4:u.mem_write(SP+(n-4)*4,struct.pack('<I',value))
                    name=kind;entry=0x380b4 if kind=='sprintf' else 0x38060
                elif kind=='buffer_putc':
                    byte,destination=extra;u.mem_write(C,struct.pack('<I',destination));regs=[byte,C,0x87654321,0x76543210];name='r1_format_unbounded_putc';entry=0x44a6c
                else:byte,ctx=extra;regs=[byte,ctx,0x87654321,0x76543210];name='r1_format_stdout_putc';entry=0x6570a
                for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],regs):u.reg_write(reg,value)
                st={'trace':[],'fault':None,'mode':mode,'side':'source' if candidate else 'native'};states[id(u)]=st
                try:u.emu_start((syms[name] if candidate else entry)|1,0x20000100,count=2000000)
                except UcError:assert st['fault'],(kind,fmt,extra,candidate,hex(u.reg_read(UC_ARM_REG_PC)))
                if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
                # Only the direct stdout leaf has the same backend frame pointer;
                # printf's parser-private callback frame is normalized separately.
                trace=[([p if kind=='stdout_putc' else 0,record]) for p,record in st['trace']]
                results.append(dict(regs=None if st['fault'] else [u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R2,UC_ARM_REG_R3]],r1=None if st['fault'] else u.reg_read(UC_ARM_REG_R1),fault=st['fault'],trace=trace,frame=bytes(u.mem_read(SP-(24 if kind in ['printf','sprintf'] else 16),24 if kind in ['printf','sprintf'] else 16)).hex() if kind!='buffer_putc' else None,destination=bytes(u.mem_read(D,256)).hex(),context=bytes(u.mem_read(C,32)).hex()))
            r1_differences+=int(results[0]['r1']!=results[1]['r1']);a=dict(results[0]);b=dict(results[1]);a.pop('r1');b.pop('r1')
            if kind=='printf':a.pop('regs');b.pop('regs')
            if kind=='sprintf' or kind=='buffer_putc':assert results[0]['r1']==results[1]['r1']
            assert a==b,(kind,fmt,args,mode,extra,results)
            if kind=='printf' and not results[0]['fault']:assert results[0]['regs'][0]==results[1]['regs'][0]
            counts[kind]+=1;faults+=int(bool(results[0]['fault']));digest.update(json.dumps([kind,fmt.hex(),args,mode,extra,results[0]],sort_keys=True).encode())
    receipt=dict(comparisons=sum(counts.values()),counts=counts,backend_calls=calls,matching_faults=faults,r1_scratch_differences=r1_differences,backend_record_mutation_modes=3,sprintf_and_buffer_full_r0_r1_r2_r3_checked=True,stdout_leaf_r0_r2_r3_and_frame16_checked=True,printf_r0_frame24_checked=True,sprintf_frame24_checked=True,unbounded_putc_instruction_bytes_equal=True,unbounded_putc_instruction_bytes=10,unbounded_putc_section_sha256=leaf_hash,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),engine_report_sha256=sha(ep),engine_object_sha256=sha(eo),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Only the10-byte buffer-putc section is instruction-byte equal; final image placement and whole-image identity remain unproven.','Stdout0x319e0 is an explicit backend fixture, not source/hardware delivery proof. Its direct16-byte record and mutations are checked.','Printf callback private frame pointers are normalized; caller-saved printf registers and stdout-leaf r1 remain gated.','Worker/parser private frames and arbitrary destination/return-address aliases, full input domains and hardware remain gated.'])
    vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
