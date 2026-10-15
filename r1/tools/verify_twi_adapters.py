#!/usr/bin/env python3
"""Execute compiled software-TWI primitives against authenticated stock Thumb."""
import hashlib,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ_UNMAPPED,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROWS=[('r1_stock_i2c'+str(i+2)+'_'+role,[address]) for role,addresses in [('read',[0x5547c,0x554b0,0x554e4,0x55518]),('write',[0x55dbc,0x55e40,0x55ec4,0x55f5c])] for i,address in enumerate(addresses)]
def main():
    null_buffers='--null-buffers' in sys.argv
    rows=ROWS;output=BASE/'software-twi';receipt=output/('null-buffer-verification.json' if null_buffers else 'adapter-verification.json');receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'i2c5/report.json').read_text());obj=BASE/'i2c5/st25-i2c5-registry.o';assert sha(obj)==report['relocatable_sha256']
    for row in report['units']:assert sha(ROOT/row['source'])==row['source_sha256']
    for path,digest in report['headers'].items():assert sha(ROOT/path)==digest
    fault_comparisons=0
    counts={};extents={};engine=0x20002000;stop=0x20000100
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'test.elf';binary=tmp/'test.bin'
        ld=tmp/'layout.ld';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.twi.records 0x20007400 (NOLOAD) : { *(.r1.twi.records) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+rows[0][0],*['--undefined='+r[0] for r in rows],str(obj),'-o',str(elf)],check=True,capture_output=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
        events={id(stock):[],id(candidate):[]};samples={id(stock):[],id(candidate):[]}
        opnames=['low','high','output','input','delay','read'];ops={0x100e000+i*16:n for i,n in enumerate(opnames)}
        for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
        candidate.mem_write(0x1000000,binary.read_bytes())
        def hook(uc,address,size,data):
            if address in ops:
                name=ops[address];args=(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)) if name=='input' else (uc.reg_read(UC_ARM_REG_R0),)
                events[id(uc)].append((name,*args));value=samples[id(uc)].pop(0) if name=='read' else 0
                uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        faults={id(stock):[],id(candidate):[]}
        def fault(uc,access,address,size,value,data):faults[id(uc)].append((access,address,size));return False
        for uc in (stock,candidate):
            uc.hook_add(UC_HOOK_CODE,hook)
            uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED|UC_HOOK_MEM_WRITE_UNMAPPED,fault)
        def run(uc,entry,args,sequence,config):
            delay,scl,sda,pull=config
            block=struct.pack('<7I',delay,scl,sda,0x100e001,0x100e011,0x100e021,0x100e031)+bytes([pull,0,0,0])+struct.pack('<2I',0x100e041,0x100e051)
            uc.mem_write(engine,block);uc.mem_write(engine-4,bytes([current_opened]));uc.mem_write(0x20002500,struct.pack('<BBHIHHIHH',0xa6,0,0x12ab,0 if null_buffers else 0x20003000,current_length,0,0 if null_buffers else 0x20003000,current_length,0));events[id(uc)].clear();samples[id(uc)]=list(sequence)
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,stop|1)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(reg,value)
            if len(args)>4:uc.mem_write(0x2003f000,struct.pack('<I',args[4]))
            uc.mem_write(0x20003000,bytes((i*37+5)&255 for i in range(512)))
            faults[id(uc)].clear()
            try:uc.emu_start(entry|1,stop,count=2000000)
            except UcError:assert null_buffers and faults[id(uc)]
            else:assert uc.reg_read(UC_ARM_REG_PC)==stop and not samples[id(uc)]
            return (None if faults[id(uc)] else uc.reg_read(UC_ARM_REG_R0)),list(faults[id(uc)]),list(events[id(uc)]),bytes(uc.mem_read(engine,40)),bytes(uc.mem_read(0x20003000,512))
        for name,entries in rows:
            for entry in entries:
                count=0
                cases=[]
                index=int(name[12])-2;engine=0x20007408+index*112
                read=name.endswith('_read')
                for opened in (0,1,255):
                    for null in (True,False):
                        for length in (0,1,2,257):
                            actual_count=length if index==2 else length&255
                            ack_count=(3 if index<2 else 4) if read else ((1 if index==2 else 2 if index<2 else 3)+actual_count)
                            for nack in (-1,0,1):
                                if nack>=ack_count:continue
                                sample=[]
                                if opened and not null:
                                    sample=[0]*ack_count if nack<0 else [0]*nack+[1]
                                    if nack<0 and read:
                                        for i in range(max(1,actual_count)):sample += [((i*53+0xa5)>>bit)&1 for bit in range(7,-1,-1)]
                                cases.append(([0xdeadbeef,0x87654321,0 if null else 0x20002500],sample,(1,43,46,3),(opened,length,nack,null)))
                for args,sequence,config,label in cases:
                    current_opened,current_length,_,_=label
                    a=run(stock,entry,args,sequence,config);b=run(candidate,syms[name],args,sequence,config)
                    if name.endswith(('start','stop','write_byte')):a=a[1:];b=b[1:]
                    assert a==b,(name,hex(entry),label,a,b)
                    if a[1]:fault_comparisons+=1
                    count+=1
                counts[hex(entry)]=count;extents[hex(entry)]=name
    result=dict(application_sha256=sha(app),integration_report_sha256=sha(BASE/'i2c5/report.json'),relocatable_sha256=sha(obj),comparisons=sum(counts.values()),fault_comparisons=fault_comparisons,comparisons_by_entry=counts,entry_symbols=extents,scope=('Null payload buffer oracle: exact unmapped read/write address, width, access type, preceding callback order and normal returns compared against stock' if null_buffers else 'Eight native request adapters executing actual compiled transactions/primitives; null requests, closed/nonzero flags, NACK exits and 8/16-bit count behavior'),limitations=['GPIO/delay callbacks are intercepted; electrical behavior remains unverified.','Null payloads are tested separately with --null-buffers. Invalid callback states remain a separate gate.','Native initial-table installation and complete application link remain open.'],instruction_identity_proven=False,application_linked=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} stock comparisons passed across {len(counts)} software-TWI bodies')
if __name__=='__main__':main()
