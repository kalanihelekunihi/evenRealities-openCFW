#!/usr/bin/env python3
"""Pinned Nordic error-string C provider, all 16-bit codes and 32-bit boundaries."""
import hashlib,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/watchdog-logging'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'strerror-verification.json';receipt.unlink(missing_ok=True)
    report=json.loads((BASE/'report.json').read_text());row=next(r for r in report['units'] if r['source'].endswith('/nrf_strerror.c'));obj=BASE/'nrf_strerror.o';assert sha(obj)==row['object_sha256']
    for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'text.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_strerror_get',str(obj),'-o',str(elf)],check=True,capture_output=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        symbols={r.split()[-1]:(int(r.split()[0],16),int(r.split()[1],16)) for r in subprocess.check_output(['arm-none-eabi-nm','-S',str(elf)],text=True).splitlines() if len(r.split())==4}
        assert symbols['nrf_strerror_array'][1]==296
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());cache={}
        def string(uc,address):
            if not address:return None
            key=(id(uc),address)
            if key not in cache:
                data=bytearray()
                while True:
                    b=uc.mem_read(address+len(data),1)[0]
                    if not b:break
                    data.append(b);assert len(data)<128
                cache[key]=data.decode()
            return cache[key]
        def table(uc,address):
            return [(code,string(uc,pointer)) for code,pointer in struct.iter_unpack('<II',bytes(uc.mem_read(address,296)))]
        original=table(stock,0x9c8a0);recovered=table(candidate,symbols['nrf_strerror_array'][0]);assert original==recovered
        expected=dict(original);assert len(expected)==37 and list(expected)==sorted(expected)
        unknown=string(stock,0x9c88c);assert unknown=='Unknown error code' and string(candidate,symbols['m_unknown_str'][0])==unknown
        saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
        seed=[0x12345600+i for i in range(8)]
        def run(uc,entry,code):
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,code)
            for r,v in zip(saved,seed):uc.reg_write(r,v)
            uc.emu_start(entry|1,0x20000100,count=10000)
            assert uc.reg_read(UC_ARM_REG_PC)==0x20000100 and uc.reg_read(UC_ARM_REG_SP)==0x2003f000
            assert [uc.reg_read(r) for r in saved]==seed
            return string(uc,uc.reg_read(UC_ARM_REG_R0))
        rng=random.Random(0x7a594);codes=list(range(65536))+[0x7fffffff,0x80000000,0xfffffffe,0xffffffff]+[rng.getrandbits(32) for _ in range(4096)]
        for name,entry in (('nrf_strerror_find',0x7a594),('nrf_strerror_get',0x7a5cc)):
            for code in codes:
                a=run(stock,entry,code);b=run(candidate,symbols[name][0],code);assert a==b==expected.get(code,None if name.endswith('find') else unknown),(name,code,a,b)
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(BASE/'report.json'),object_sha256=sha(obj),comparisons=2*len(codes),codes_per_entry=len(codes),table_rows_compared=37,table_bytes_pointer_normalized=296,table_entries=original,scope='Actual unchanged Nordic C binary-search/fallback providers; all 65536 low-word codes, 4096 deterministic 32-bit codes and signed boundaries, exact normalized code/name table, null versus fallback and saved registers/stack',limitations=['Returned string addresses are relocated and compared by content; original instruction and pointer identity remain open.','No physical-device or whole-image execution proof.'],instruction_identity_proven=False),indent=2)+'\n')
    print(f'{2*len(codes)} Nordic error-string comparisons passed; all 37 table entries match')
if __name__=='__main__':main()
