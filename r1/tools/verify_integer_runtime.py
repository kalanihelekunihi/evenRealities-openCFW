#!/usr/bin/env python3
"""Execute locked Arm integer routines against pinned C providers and Python math."""
import hashlib,json,random,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/integer-runtime'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MASK=(1<<64)-1
def main():
    receipt=BASE/'verification.json';receipt.unlink(missing_ok=True)
    report=json.loads((BASE/'report.json').read_text());obj=BASE/'integer-runtime.o'
    assert sha(obj)==report['relocatable_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
    assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    entries={'__aeabi_uldivmod':0x274e8,'__aeabi_ldivmod':0x2754a,'__aeabi_llsl':0x275ac,'__aeabi_llsr':0x275ca}
    registers=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
    saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
    seed=[0x13570000+i*0x101 for i in range(8)];counts={}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'integer.elf';binary=tmp/'integer.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--entry=__aeabi_uldivmod',str(obj),'-o',str(elf)],check=True,capture_output=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={r.split()[-1]:int(r.split()[0],16) for r in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(r.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        for uc in (stock,candidate):
            uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
        def run(uc,entry,args,name):
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R12,0xdeadbeef)
            for reg,value in zip(registers,args):uc.reg_write(reg,value)
            for reg,value in zip(saved,seed):uc.reg_write(reg,value)
            uc.emu_start(entry|1,0x20000100,count=100000)
            assert uc.reg_read(UC_ARM_REG_PC)==0x20000100,(name,args)
            assert uc.reg_read(UC_ARM_REG_SP)==0x2003f000
            assert [uc.reg_read(r) for r in saved]==seed
            result=[uc.reg_read(r) for r in registers]
            if name=='__aeabi_uldivmod':assert uc.reg_read(UC_ARM_REG_R12)==0xdeadbeef
            if name=='__aeabi_ldivmod':assert uc.reg_read(UC_ARM_REG_R12)==result[3] and uc.reg_read(UC_ARM_REG_LR)==result[0]
            return result
        rng=random.Random(0x274e8)
        boundaries=sorted({0,1,2,3,7,10,1000,MASK,*((1<<b)+d for b in range(1,64) for d in (-1,0,1))})
        pairs=[(n,d) for n in boundaries for d in (0,1,2,3,7,1000,1<<32,1<<63,MASK)]
        pairs += [(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(10000)]
        pairs += [(MASK,1<<b) for b in range(64)]
        for name in ('__aeabi_uldivmod','__aeabi_ldivmod'):
            for n,d in pairs:
                args=[n&0xffffffff,n>>32,d&0xffffffff,d>>32]
                a=run(stock,entries[name],args,name);b=run(candidate,syms[name],args,name)
                assert a==b,(name,hex(n),hex(d),a,b)
                if name=='__aeabi_uldivmod':q,r=divmod(n,d) if d else (MASK,n)
                else:
                    sn=n-(1<<64) if n>>63 else n;sd=d-(1<<64) if d>>63 else d
                    q=abs(sn)//abs(sd) if sd else MASK
                    if (sn<0)!=(sd<0):q=-q
                    r=sn-q*sd if sd else sn
                assert a==[q&0xffffffff,(q&MASK)>>32,r&0xffffffff,(r&MASK)>>32],(name,n,d,a,q,r)
            counts[name]=len(pairs)
        values=[0,1,0xffffffff,1<<32,1<<63,MASK,0x123456789abcdef0]
        shiftcases=[(v,c) for v in values for c in (*range(512),0x7fffffff,0x80000000,0x80000001,0xffffff00,0xffffffff)]
        shiftcases += [(rng.getrandbits(64),rng.getrandbits(32)) for _ in range(10000)]
        def lsl(v,c):
            c&=255;return (v<<c)&0xffffffff if c<32 else 0
        def lsr(v,c):
            c&=255;return v>>c if c<32 else 0
        for name in ('__aeabi_llsl','__aeabi_llsr'):
            for v,c in shiftcases:
                args=[v&0xffffffff,v>>32,c,0xaabbccdd]
                a=run(stock,entries[name],args,name)[:2];b=run(candidate,syms[name],args,name)[:2]
                assert a==b,(name,hex(v),hex(c),a,b)
                lo=v&0xffffffff;hi=v>>32
                if name=='__aeabi_llsl':
                    expected=[0,lsl(lo,c-32)] if c<0x80000000 and c>=32 else [lsl(lo,c),lsl(hi,c)|lsr(lo,32-c)]
                else:
                    expected=[lsr(hi,c-32),0] if c<0x80000000 and c>=32 else [lsr(lo,c)|lsl(hi,32-c),lsr(hi,c)]
                assert a==expected
            counts[name]=len(shiftcases)
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),runtime_report_sha256=sha(BASE/'report.json'),relocatable_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,scope='Stock differential and independent integer model; quotient/remainder registers, signed overflow and zero divisors, all count-byte patterns and wide count words, callee-saved registers and stack; unsigned IP preservation and signed IP/LR side effects',limitations=['Attributable replacement source, not original Arm runtime source or instruction identity.','No cycle timing, interrupt interaction or physical-device execution proof.'],instruction_identity_proven=False),indent=2)+'\n')
    print(f'{sum(counts.values())} integer runtime comparisons passed: {counts}')
if __name__=='__main__':main()
