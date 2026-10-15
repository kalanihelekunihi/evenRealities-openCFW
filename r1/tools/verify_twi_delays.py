#!/usr/bin/env python3
"""Check recovered delay work without claiming instruction/cycle identity."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/software-twi';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'delay-verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'gpio-report.json').read_text());obj=Path(report['units'][0]['command'][-1]);assert sha(obj)==report['units'][0]['object_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest
    entries={0x7a6dc:'r1_twi_delay_busy',0x7a6ec:'r1_twi_delay_busy',0x7081c:'r1_twi_delay_noop',0x54af0:'r1_twi_delay_noop'};counts={};work={}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'test.elf';binary=tmp/'test.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--gc-sections','--entry=r1_twi_delay_busy','--undefined=r1_twi_delay_noop',str(obj),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());observed={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        candidate.mem_write(0x1000000,binary.read_bytes())
        def step(uc,address,size,data):
            if address in (0x9a642,0x9a652):observed[id(uc)].append(uc.reg_read(UC_ARM_REG_R0))
        def store(uc,access,address,size,value,data):
            if address==0x2003effc and size==4:observed[id(uc)].append(value)
        stock.hook_add(UC_HOOK_CODE,step);candidate.hook_add(UC_HOOK_MEM_WRITE,store)
        for entry,name in entries.items():
            values=[0,1,2,3,5,10,100,1000,0x4000000,0x4000001,0x8000000,0xc000000] if name.endswith('busy') else [0,1,5,0xffffffff]
            for value in values:
                for uc,address in ((stock,entry),(candidate,syms[name])):
                    observed[id(uc)].clear();uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(address|1,0x20000100,count=1000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                a=observed[id(stock)];b=observed[id(candidate)]
                if name.endswith('busy') and value:b=b[1:] # exclude initial volatile counter store
                assert a==b,(hex(entry),value,a,b);work[str(value)]=len(a)
            counts[hex(entry)]=len(values)
    result=dict(application_sha256=sha(app),gpio_report_sha256=sha(BASE/'gpio-report.json'),object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,entry_symbols={hex(k):v for k,v in entries.items()},scope='Two busy-delay wrappers preserve every subtract-three counter result and unsigned termination; two no-op callbacks do no work; includes shift-overflow cases',limitations=['Volatile C loop introduces stack accesses and does not establish instruction or cycle identity.','Physical elapsed time and interrupt effects remain unverified.','Large effective nonzero delays beyond tested work counts are not executed.'],cycle_identity_proven=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} delay work-contract comparisons passed; cycle identity remains unproven')
if __name__=='__main__':main()
