#!/usr/bin/env python3
"""Execute compiled software-TWI primitives against authenticated stock Thumb."""
import hashlib,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROWS=[('software_twi_start',[0x55a18,0x55a56,0x55a94,0x55ad2]),('software_twi_stop',[0x55b10,0x55b3c,0x55b68,0x55b94]),('software_twi_wait_ack',[0x55bc0,0x55c08,0x55c50,0x55c98]),('software_twi_read_byte',[0x55548,0x555f4,0x556a0,0x5574c]),('software_twi_write_byte',[0x55fa4,0x55ff2,0x56040,0x5608e])]
TRANSACTIONS=[('software_twi_read_transaction_reg8',[0x557f8,0x55878]),('software_twi_read_transaction_reg16',[0x558f8,0x55988]),('software_twi_write_transaction_reg16_byte',[0x560dc]),('software_twi_write_transaction_reg8',[0x5613e,0x561a0]),('software_twi_write_transaction_reg16',[0x56202])]
def main():
    transactions='--transactions' in sys.argv
    rows=TRANSACTIONS if transactions else ROWS
    output=BASE/'software-twi';output.mkdir(exist_ok=True);receipt=output/('transaction-verification.json' if transactions else 'primitive-verification.json');receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'report.json').read_text());row=next(x for x in report['units'] if x['source'].endswith('software_twi.c'));obj=Path(row['command'][-1]);assert sha(obj)==row['object_sha256'] and sha(ROOT/row['source'])==row['source_sha256']
    header=ROOT/'r1/reconstructed/software_twi/software_twi.h';assert sha(header)==report['evidence_inputs'][str(header.relative_to(ROOT))]
    counts={};extents={};engine=0x20002000;stop=0x20000100
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'test.elf';binary=tmp/'test.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--gc-sections','--entry='+rows[0][0],*['--undefined='+r[0] for r in rows],str(obj),'-o',str(elf)],check=True,capture_output=True)
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
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_CODE,hook)
        def run(uc,entry,args,sequence,config):
            delay,scl,sda,pull=config
            block=struct.pack('<7I',delay,scl,sda,0x100e001,0x100e011,0x100e021,0x100e031)+bytes([pull,0,0,0])+struct.pack('<2I',0x100e041,0x100e051)
            uc.mem_write(engine,block);events[id(uc)].clear();samples[id(uc)]=list(sequence)
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,stop|1)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(reg,value)
            if len(args)>4:uc.mem_write(0x2003f000,struct.pack('<I',args[4]))
            uc.mem_write(0x20003000,bytes((i*37+5)&255 for i in range(512)))
            uc.emu_start(entry|1,stop,count=2000000);assert uc.reg_read(UC_ARM_REG_PC)==stop and not samples[id(uc)]
            return uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),bytes(uc.mem_read(engine,40)),bytes(uc.mem_read(0x20003000,512))
        for name,entries in rows:
            for entry in entries:
                count=0
                cases=[]
                if transactions:
                    read='read_transaction' in name;single=name.endswith('_byte');wide='reg16' in name
                    for address in (0,0xa6,0xff):
                        for reg in (0,0x34,0x12ab if wide else 0xab):
                            for length in ((1,) if single else (0,1,2,7,255)):
                                ack_count=(4 if wide else 3) if read else ((3 if wide else 2)+(1 if single else length))
                                for nack in (-1,*range(ack_count if length<8 else 3)):
                                    sample=[0]*ack_count
                                    if nack>=0:sample=[0]*nack+[1]
                                    elif read:
                                        for i in range(max(1,length)):
                                            sample += [((i*53+0xa5)>>bit)&1 for bit in range(7,-1,-1)]
                                    args=[address,reg,0x5a,engine] if single else [address,reg,0x20003000,length,engine]
                                    cases.append((args,sample,(1,43,46,0),(address,reg,length,nack)))
                else:
                    for value in (range(256) if name.endswith(('read_byte','write_byte')) else range(2)):
                        for variant in (0,1):
                            config=(1,43,46,0) if variant==0 else (5,11,12,3)
                            if name.endswith('read_byte'):args=[variant,engine];sequence=[(value>>bit)&1 for bit in range(7,-1,-1)]
                            elif name.endswith('write_byte'):args=[value,engine];sequence=[]
                            else:args=[engine];sequence=[value] if name.endswith('wait_ack') else []
                            cases.append((args,sequence,config,(value,variant)))
                for args,sequence,config,label in cases:
                    a=run(stock,entry,args,sequence,config);b=run(candidate,syms[name],args,sequence,config)
                    if name.endswith(('start','stop','write_byte')):a=a[1:];b=b[1:]
                    assert a==b,(name,hex(entry),label,a,b)
                    count+=1
                counts[hex(entry)]=count;extents[hex(entry)]=name
    result=dict(application_sha256=sha(app),source_report_sha256=sha(BASE/'report.json'),source=row['source'],source_sha256=row['source_sha256'],header_sha256=sha(header),object=str(obj.relative_to(ROOT)),object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,entry_symbols=extents,scope=('Eight original transaction bodies versus compiled C; register order, status, NACK exits, lengths 0/1/2/7/255 and full ordered callback traces' if transactions else 'All twenty original primitive bodies versus compiled C; exhaustive write/read byte values, both read ACK choices, ACK/NACK sampling and full ordered callback traces'),limitations=['Only valid fully bound engine states are compared; reconstruction adds invalid-state guards.','GPIO callbacks and delay callback are intercepted. Electrical behavior and physical timing are not proven.','Folded source bodies do not establish original instruction placement or instruction identity.','Provider upstream identity remains unresolved; this is owner-authorized reconstructed source.'],instruction_identity_proven=False,application_linked=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} stock comparisons passed across {len(counts)} software-TWI bodies')
if __name__=='__main__':main()
