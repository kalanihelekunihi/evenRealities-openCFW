#!/usr/bin/env python3
"""Memory providers: bounded C contracts plus stock memset/strcmp/clear."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'verification.json';receipt.unlink(missing_ok=True);report=json.loads((BASE/'report.json').read_text());obj=BASE/'memory-runtime.o';assert sha(obj)==report['relocatable_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    counts={};differential=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'test.elf';binary=tmp/'test.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--entry=memcpy',str(obj),'-o',str(elf)],check=True,capture_output=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
        for uc in (candidate,stock):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        candidate.mem_write(0x1000000,binary.read_bytes())
        seed=bytes((i*37+5)&255 for i in range(4096))
        def run(uc,entry,args,initial):
            uc.mem_write(0x20001000,initial);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):uc.reg_write(reg,value)
            uc.emu_start(entry|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
            return uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(0x20001000,4096))
        for name in ('memcpy','memset','__aeabi_memcpy4','__aeabi_memclr','__aeabi_memclr4','__aeabi_memclr8'):
            count=0;alignment=8 if name.endswith('8') else 4 if name.endswith('4') else 1
            for dest_offset in range(0,16,alignment):
                for length in (0,1,2,3,4,7,8,15,16,31,32,63,64,127,128,257,513):
                    for value in ((0,1,255,0x1234) if name=='memset' else (0,1,3)):
                        dest=0x20001000+dest_offset;source=0x20001800+(value if name=='memcpy' else 0);expected=bytearray(seed)
                        if 'memcpy' in name:expected[dest_offset:dest_offset+length]=seed[source-0x20001000:source-0x20001000+length];args=[dest,source,length]
                        elif name=='memset':expected[dest_offset:dest_offset+length]=bytes([value&255])*length;args=[dest,value,length]
                        else:expected[dest_offset:dest_offset+length]=bytes(length);args=[dest,length,0]
                        result=run(candidate,syms[name],args,seed);assert result[1]==bytes(expected),(name,dest_offset,length,value)
                        if name in ('memcpy','memset'):assert result[0]==dest
                        original={'memset':0x277ae,'__aeabi_memclr':0x277aa}.get(name)
                        if original:
                            observed=run(stock,original,args,seed);assert observed[1]==result[1]
                            if name=='memset':assert observed[0]==result[0]
                            differential+=1
                        count+=1
            counts[name]=count
        count=0
        strings=[b'',b'a',b'ab',b'abc',b'\x80',b'\xff',bytes(range(1,128)),b'x'*257,b'x'*256+b'y']
        for left in strings:
            for right in strings:
                initial=bytearray(seed);initial[:len(left)+1]=left+b'\0';initial[2048:2048+len(right)+1]=right+b'\0';args=[0x20001000,0x20001800,0]
                a=run(candidate,syms['strcmp'],args,bytes(initial));b=run(stock,0x277fe,args,bytes(initial));assert a==b;(count:=count+1);differential+=1
        counts['strcmp']=count
        for value in strings:
            initial=bytearray(seed);initial[:len(value)+1]=value+b'\0'
            a=run(candidate,syms['strlen'],[0x20001000,0,0],bytes(initial));b=run(stock,0x277f0,[0x20001000,0,0],bytes(initial));assert a==b and a[0]==len(value);differential+=1
        counts['strlen']=len(strings)
    receipt.write_text(json.dumps(dict(application_sha256=sha(app),runtime_report_sha256=sha(BASE/'report.json'),relocatable_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,stock_differential_comparisons=differential,scope='Compiled upstream C bodies and EABI wrappers; guarded memory snapshots, return contracts, unaligned/general and aligned EABI cases; stock memset/strcmp/clear differential',limitations=['memcpy overlap is excluded by its C contract.','Invalid pointers, fault granularity, cycle timing and original instruction identity remain unproven.','These are attributable provider candidates, not original Arm runtime source.'],instruction_identity_proven=False),indent=2)+'\n');print(f'{sum(counts.values())} memory/string comparisons passed, including {differential} stock comparisons')
if __name__=='__main__':main()
