#!/usr/bin/env python3
"""Execute pinned SDK NVIC critical regions against locked application routines."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/sdk-critical'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
STATE=0x2002c2fc;OUT=0x20001000;NVIC=0xe000e000;MASK=0xbdff06fc
def main():
    receipt=BASE/'verification.json';receipt.unlink(missing_ok=True)
    report=json.loads((BASE/'report.json').read_text());obj=BASE/'critical-only.o'
    assert sha(obj)==report['selected_object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
    assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    counts={'enter':0,'exit':0,'nested_sequence_calls':0};fault_count=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=app_util_critical_region_enter',str(obj),'-o',str(elf)],check=True,capture_output=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        assert syms['nrf_nvic_state']==STATE
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        writes={};faults={}
        def write(uc,access,address,size,value,user):
            if NVIC<=address<NVIC+4096:writes[id(uc)].append((address,size,value))
        def fault(uc,access,address,size,value,user):faults[id(uc)].append((address,size,value));return False
        for uc in (stock,candidate):
            uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(NVIC,4096)
            uc.hook_add(UC_HOOK_MEM_WRITE,write);uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
        # Compare all source-owned BSS bytes with the stock C runtime initializer.
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000)
        assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(STATE,12))==bytes(12)
        def setup(uc,state,irq0,irq1,primask):
            uc.mem_write(STATE,struct.pack('<3I',*state));uc.mem_write(OUT,bytes([0xa5])*16);uc.mem_write(NVIC,bytes(4096));uc.mem_write(NVIC+0x180,struct.pack('<2I',irq0,irq1));uc.reg_write(UC_ARM_REG_PRIMASK,primask)
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def run(uc,kind,arg):
            writes[id(uc)]=[];faults[id(uc)]=[]
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,arg)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            entry=({'enter':0x4ebec,'exit':0x4ec34}[kind] if uc is stock else syms['app_util_critical_region_'+kind])
            try:uc.emu_start(entry|1,0x20000100,count=10000)
            except UcError:assert faults[id(uc)],hex(uc.reg_read(UC_ARM_REG_PC))
            else:
                assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
                assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            return (bytes(uc.mem_read(STATE,12)),bytes(uc.mem_read(OUT,16)),uc.reg_read(UC_ARM_REG_PRIMASK),list(writes[id(uc)]),list(faults[id(uc)]))
        def compare(kind,arg):
            a=run(stock,kind,arg);b=run(candidate,kind,arg);assert a==b,(kind,arg,a,b);return a
        rng=random.Random(0x4ebec)
        patterns=[0,1,0xffffffff,MASK,~MASK&0xffffffff,0x80000000,0x55aa55aa,0xaa55aa55]
        cases=[(f,m0,m1,i0,i1,p) for f,m0,m1,i0,i1,p in itertools.product((0,1,2,0xffffffff),patterns[:3],patterns[:3],patterns,patterns[:3],(0,1))]
        cases += [(rng.getrandbits(32) if i%2 else 0,*(rng.getrandbits(32) for _ in range(4)),i%2) for i in range(1024)]
        for flag,m0,m1,irq0,irq1,primask in cases:
            for uc in (stock,candidate):setup(uc,(m0,m1,flag),irq0,irq1,primask)
            result=compare('enter',OUT);expected=(m0,m1,flag) if flag else (irq0&MASK,irq1,1)
            assert result[0]==struct.pack('<3I',*expected) and result[1]==bytes([1 if flag else 0])+bytes([0xa5])*15 and result[2]==primask
            assert result[3]==([] if flag else [(NVIC+0x180,4,MASK),(NVIC+0x184,4,0xffffffff)])
            counts['enter']+=1
        for flag,nested,primask,m0,m1 in itertools.product((0,1,2,0xffffffff),range(256),(0,1),patterns,patterns[:3]):
            for uc in (stock,candidate):setup(uc,(m0,m1,flag),0x12345678,0x87654321,primask)
            result=compare('exit',nested);active=bool(flag and not nested)
            assert result[0]==struct.pack('<3I',m0,m1,0 if active else flag) and result[1]==bytes([0xa5])*16 and result[2]==primask
            assert result[3]==([(NVIC+0x100,4,m0),(NVIC+0x104,4,m1)] if active else [])
            counts['exit']+=1
        for flag,primask,pointer in itertools.product((0,1,2,0xffffffff),(0,1),(0,0x20040000)):
            for uc in (stock,candidate):setup(uc,(1,2,flag),0x55555555,0xaaaaaaaa,primask)
            result=compare('enter',pointer);assert result[4] and result[2]==1;fault_count+=1
        for depth,primask in itertools.product(range(1,17),(0,1)):
            for uc in (stock,candidate):setup(uc,(0,0,0),0x12345678,0x87654321,primask)
            flags=[]
            for _ in range(depth):flags.append(compare('enter',OUT)[1][0]);counts['nested_sequence_calls']+=1
            assert flags==[0]+[1]*(depth-1)
            for nested in reversed(flags):compare('exit',nested);counts['nested_sequence_calls']+=1
            assert bytes(stock.mem_read(STATE,12))==struct.pack('<3I',0x12345678&MASK,0x87654321,0)
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(BASE/'report.json'),selected_object_sha256=sha(obj),comparisons=sum(counts.values())+fault_count,comparisons_by_kind=counts,null_or_unmapped_pointer_faults=fault_count,state_address=hex(STATE),initial_zero_bytes_compared=12,scope='Actual pinned Nordic critical-region C bodies; raw NVIC write order/value, masks, nested byte, PRIMASK, preserved registers/stack, repeated nesting and unmapped writes; no provider interceptions',limitations=['NVIC registers are a deterministic mapped register model; real interrupt delivery and hardware alias semantics are not exercised.','Void return scratch registers and original instruction identity are outside this contract.','No physical-device, whole-image or cycle-timing proof.'],instruction_identity_proven=False),indent=2)+'\n')
    print(f'{sum(counts.values())+fault_count} Nordic critical-region comparisons passed; {fault_count} faults')
if __name__=='__main__':main()
