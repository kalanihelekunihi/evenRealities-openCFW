#!/usr/bin/env python3
"""Compare compiled Nordic HAL callbacks with all native TWI callback copies."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/software-twi'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'gpio-verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'gpio-report.json').read_text());row=report['units'][0];obj=Path(row['command'][-1]);assert sha(obj)==row['object_sha256']
    for p,digest in report['inputs'].items():assert sha(ROOT/p)==digest,p
    initial=json.loads((BASE/'stock-initialization.json').read_text());assert initial['application_sha256']==sha(app)
    names={'drive_low':'r1_twi_gpio_low','release_high':'r1_twi_gpio_high','set_output':'r1_twi_gpio_output','set_input':'r1_twi_gpio_input','pin_release':'r1_twi_gpio_release','read_pin':'r1_twi_gpio_read'}
    counts={};mapping={}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'test.elf';binary=tmp/'test.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000',str(obj),'-o',str(elf),'--entry=r1_twi_gpio_low'],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):
            uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
            uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events[id(u)].append((p,s,v)),begin=0x50000000,end=0x50000fff)
        candidate.mem_write(0x1000000,binary.read_bytes())
        def run(uc,entry,pin,pull,pattern,read):
            uc.mem_write(0x50000000,struct.pack('<I',pattern)*1024);events[id(uc)].clear();uc.reg_write(UC_ARM_REG_R0,pin);uc.reg_write(UC_ARM_REG_R1,pull);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
            uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
            return (uc.reg_read(UC_ARM_REG_R0) if read else None,list(events[id(uc)]),bytes(uc.mem_read(0x50000000,4096)))
        for record in initial['records']:
            for role,name in names.items():
                entry=int(record['callbacks'][role],16)&~1;count=0
                for pin in range(48):
                    for pull in ((0,1,3) if role=='set_input' else (0,)):
                        for pattern in (0,0xffffffff,0xa55a33cc):
                            a=run(stock,entry,pin,pull,pattern,role=='read_pin');b=run(candidate,syms[name],pin,pull,pattern,role=='read_pin');assert a==b,(record['name'],role,pin,pull,pattern,a,b);count+=1
                counts[hex(entry)]=count;mapping[hex(entry)]=name
    result=dict(application_sha256=sha(app),gpio_report_sha256=sha(BASE/'gpio-report.json'),stock_initialization_sha256=sha(BASE/'stock-initialization.json'),object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,entry_symbols=mapping,scope='24 stock callbacks versus compiled Nordic inline HAL wrappers; all 48 valid GPIO pins, pull 0/1/3 and three MMIO patterns; ordered writes, full peripheral snapshot and read return compared',limitations=['Electrical line behavior and timing remain unverified.','Invalid GPIO pins and unsupported pull values are excluded.','Native callback relocation and delay providers remain open.'],instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} GPIO comparisons passed across {len(counts)} native callbacks')
if __name__=='__main__':main()
