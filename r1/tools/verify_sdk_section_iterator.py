#!/usr/bin/env python3
"""Authenticate the legacy SDK multi-range cursor against stock init/next."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SET=0x20001000;SECTIONS=0x20001100;CURSOR=0x20001200
def main():
    receipt=BASE/'sdk-ble-dispatch/iterator-verification.json';receipt.unlink(missing_ok=True);report_path=BASE/'sdk-ble-dispatch/report.json';report=json.loads(report_path.read_text());obj=BASE/'sdk-ble-dispatch/nrf_section_iter.o';assert sha(obj)==next(r for r in report['units'] if r['source'].endswith('/nrf_section_iter.c'))['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    comparisons=0;cases=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_section_iter_init',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        def run(uc,kind):
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,CURSOR);uc.reg_write(UC_ARM_REG_R1,SET)
            for i,r in enumerate(saved):uc.reg_write(r,0x12345600+i)
            entry=({'init':0x7a53c,'next':0x7a56a}[kind] if uc is stock else syms['nrf_section_iter_'+kind]);uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000;assert [uc.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
            return bytes(uc.mem_read(CURSOR-4,20))
        def compare(kind,expected):
            nonlocal comparisons
            a=run(stock,kind);b=run(candidate,kind);assert a==b==b'LEFT'+struct.pack('<3I',*expected)+b'RGHT',(kind,a,b,expected);comparisons+=1
        for counts,stride in itertools.product(itertools.product(range(4),repeat=4),(1,2,4,8,12,16,0x10000)):
            ranges=[(0x20002000+i*0x40000,0x20002000+i*0x40000+count*stride) for i,count in enumerate(counts)];size=stride
            for uc in (stock,candidate):uc.mem_write(SET,struct.pack('<3I',SECTIONS,SECTIONS+32,size));uc.mem_write(SECTIONS,b''.join(struct.pack('<2I',*pair) for pair in ranges));uc.mem_write(CURSOR-4,b'LEFT'+bytes([0xa5])*12+b'RGHT')
            current=0
            while current<4 and ranges[current][0]==ranges[current][1]:current+=1
            item=ranges[current][0] if current<4 else 0;compare('init',(SET,SECTIONS+current*8,item))
            for _ in range(sum(counts)+2):
                if item:
                    item=(item+size)&0xffffffff
                    if item==ranges[current][1]:
                        current+=1
                        while current<4 and ranges[current][0]==ranges[current][1]:current+=1
                        item=ranges[current][0] if current<4 else 0
                compare('next',(SET,SECTIONS+current*8,item))
            cases+=1
        for first,last,size,item in ((SECTIONS,SECTIONS,8,0),(0,0,0,0)):
            for uc in (stock,candidate):uc.mem_write(SET,struct.pack('<3I',first,last,size));uc.mem_write(CURSOR-4,b'LEFT'+struct.pack('<3I',SET,first,item)+b'RGHT')
            compare('init',(SET,first,0));compare('next',(SET,first,0));cases+=1
        for stride,replacement in itertools.product((0,1,4,8,0xffffffff),(0,1,8,0x80000000,0xffffffff)):
            start=0x20002000;end=start+16
            for uc in (stock,candidate):uc.mem_write(SET,struct.pack('<3I',SECTIONS,SECTIONS+8,stride));uc.mem_write(SECTIONS,struct.pack('<2I',start,end));uc.mem_write(CURSOR-4,b'LEFT'+bytes(12)+b'RGHT')
            compare('init',(SET,SECTIONS,start));item=start
            for uc in (stock,candidate):uc.mem_write(SET+8,struct.pack('<I',replacement))
            current=SECTIONS
            for _ in range(4):
                if item:
                    item=(item+replacement)&0xffffffff
                    if item==end:current=SECTIONS+8;item=0
                compare('next',(SET,current,item))
            cases+=1
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report_path),object_sha256=sha(obj),comparisons=comparisons,range_cases=cases,cursor_bytes=12,scope='Unchanged SDK non-GNU multi-range branch under localized Clang compiler-abstraction compatibility; full cursor/guards, empty priority skips, boundaries, terminal cursor, strides/mutation/wrapping and saved registers/stack',limitations=['Mapped descriptor/cursor fixtures are used; invalid pointers and partial-record faults are outside this contract.','Zero/mismatched strides and wide arithmetic are bounded pinned-target observations, not guarantees of termination or portable pointer arithmetic.','Original instructions, live dispatcher ownership and physical BLE delivery remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{comparisons} legacy section-iterator comparisons passed across {cases} range cases')
if __name__=='__main__':main()
