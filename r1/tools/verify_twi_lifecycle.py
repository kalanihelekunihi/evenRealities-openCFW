#!/usr/bin/env python3
"""Native TWI lifecycle with actual compiled Nordic GPIO provider bodies."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'software-twi/lifecycle-verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'i2c5/report.json').read_text());obj=BASE/'i2c5/st25-i2c5-registry.o';assert sha(obj)==report['relocatable_sha256']
    for row in report['units']:assert sha(ROOT/row['source'])==row['source_sha256']
    for path,digest in report['headers'].items():assert sha(ROOT/path)==digest
    initial=json.loads((BASE/'software-twi/stock-initialization.json').read_text());assert initial['application_sha256']==sha(app)
    roots={**{'r1_stock_i2c'+str(i+2)+'_open':a for i,a in enumerate((0x55330,0x55360,0x55390,0x553e4))},**{'r1_stock_i2c'+str(i+2)+'_close':a for i,a in enumerate((0x551e8,0x5520c,0x55230,0x55254))}}
    counts={name:0 for name in roots}
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';binary=tmp/'test.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.twi.records 0x20007400 (NOLOAD) : { *(.r1.twi.records) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+next(iter(roots)),*['--undefined='+n for n in roots],*['--undefined='+n for n in ('r1_twi_gpio_output','r1_twi_gpio_high','r1_twi_gpio_release')],str(obj),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_stock_twi_records']==0x20007400
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):
            uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
            uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,a,p,s,v,d:events[id(u)].append((p,s,v)),begin=0x50000000,end=0x50000fff)
        candidate.mem_write(0x1000000,binary.read_bytes())
        def prepare(uc,index,opened,pins):
            data=bytearray((i*29+17)&255 for i in range(448));offset=index*112;data[offset+4]=opened
            struct.pack_into('<2I',data,offset+12,*pins)
            for off,role,name in ((24,'release_high','r1_twi_gpio_high'),(28,'set_output','r1_twi_gpio_output'),(48,'pin_release','r1_twi_gpio_release')):
                address=int(initial['records'][index]['callbacks'][role],16) if uc is stock else syms[name]|1
                struct.pack_into('<I',data,offset+off,address)
            uc.mem_write(0x20007400,bytes(data));uc.mem_write(0x50000000,bytes([0xa5])*4096)
        def run(uc,entry,index,check_return):
            events[id(uc)].clear();uc.reg_write(UC_ARM_REG_R0,0xaabbccdd);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.emu_start(entry|1,0x20000100,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
            data=bytearray(uc.mem_read(0x20007400,448))
            for off in (24,28,48):data[index*112+off:index*112+off+4]=bytes(4)
            return (uc.reg_read(UC_ARM_REG_R0) if check_return else None,list(events[id(uc)]),bytes(data),bytes(uc.mem_read(0x50000000,4096)))
        for index in range(4):
            for opened in (0,1,2,255):
                for pins in ((initial['records'][index]['scl_pin'],initial['records'][index]['sda_pin']),(0,31),(32,47),(47,0)):
                    for order in (('open','open','close','close'),('close','close','open','open')):
                        for uc in (stock,candidate):prepare(uc,index,opened,pins)
                        for role in order:
                            name='r1_stock_i2c'+str(index+2)+'_'+role
                            # Stock already-closed returns its zero flag; both lifecycle statuses are zero.
                            a=run(stock,roots[name],index,True);b=run(candidate,syms[name],index,True);assert a==b,(name,opened,pins,a,b);counts[name]+=1
    result=dict(application_sha256=sha(app),integration_report_sha256=sha(BASE/'i2c5/report.json'),relocatable_sha256=sha(obj),stock_initialization_sha256=sha(BASE/'software-twi/stock-initialization.json'),comparisons=sum(counts.values()),comparisons_by_entry=counts,scope='Eight native lifecycle bodies with actual stock/compiled Nordic GPIO callbacks; statuses, complete record bytes after relocation normalization, ordered MMIO writes and peripheral snapshots match',limitations=['Only valid non-NULL lifecycle callbacks and valid pins are tested.','Delay and transfer operation installation remain open.','Peripheral writes are emulated; electrical effects and physical timing are unverified.'],instruction_identity_proven=False,application_linked=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} native TWI lifecycle comparisons passed')
if __name__=='__main__':main()
