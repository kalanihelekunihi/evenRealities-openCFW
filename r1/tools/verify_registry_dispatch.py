#!/usr/bin/env python3
"""Stock-Thumb differential oracle for native registry operation dispatch."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ_UNMAPPED
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build/i2c5'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROWS=[('00',0x85d08,0,5,1),('08',0x85d1a,2,5,1),('0c',0x85cba,3,6,1),('10',0x85d2c,4,2,4),('14',0x85da8,5,3,4),('18',0x85ccc,6,7,3),('20',0x85d46,8,9,3)]
def main():
    receipt=BASE/'registry-dispatch-verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    ghidra=json.loads((BASE/'ghidra-mcp-dispatch-bytes.json').read_text())
    assert bytes(ghidra['data'])==app.read_bytes()[0x85cba-0x27000:0x85cde-0x27000]
    report=json.loads((BASE/'report.json').read_text());obj=BASE/'stock_registry.o';row=next(x for x in report['units'] if x['source'].endswith('stock_registry.c'))
    assert sha(obj)==row['object_sha256'] and sha(ROOT/row['source'])==row['source_sha256']
    for path,digest in report['headers'].items():assert sha(ROOT/path)==digest
    counts={};faults=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'test.elf';binary=tmp/'test.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--gc-sections','--entry=r1_stock_dispatch_00',*['--undefined=r1_stock_dispatch_'+r[0] for r in ROWS],str(obj),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        for suffix,entry,index,missing,argc in ROWS:
            count=0
            for mode in ('null_device','null_table','missing','provider'):
                for status in (0,1,0x87654321):
                    results=[]
                    for stock in (True,False):
                        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x20000,0xc0000);uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
                        uc.mem_write(0x27000,app.read_bytes());uc.mem_write(0x1000000,binary.read_bytes());events=[];bad=[]
                        device=0 if mode=='null_device' else 0x20002000;ops=0 if mode=='null_table' else 0x20002100
                        uc.mem_write(0x20002000,struct.pack('<6I',0,ops,0,0,0,0));table=[0]*9;table[index]=0x100f001 if mode=='provider' else 0;uc.mem_write(0x20002100,struct.pack('<9I',*table))
                        regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
                        for reg,value in zip(regs,(device,0x12345678,0x20003000,0xdeadbeef)):uc.reg_write(reg,value)
                        uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                        def hook(u,address,size,data):
                            if address==0x100f000:
                                events.append(tuple(u.reg_read(r) for r in regs[:argc]));u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
                        def fault(u,access,address,size,value,data):bad.append((address,size));return False
                        uc.hook_add(UC_HOOK_CODE,hook);uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED,fault)
                        try:uc.emu_start((entry if stock else syms['r1_stock_dispatch_'+suffix])|1,0x20000100,count=1000)
                        except UcError:
                            assert mode=='null_table' and bad
                        else:assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                        results.append((bad,events,None if bad else uc.reg_read(UC_ARM_REG_R0)))
                    assert results[0]==results[1],(suffix,mode,results)
                    if mode=='null_table':assert results[0][0]==[(index*4,4)];faults+=1
                    else:assert results[0][2]==(1 if mode=='null_device' else missing if mode=='missing' else status)
                    count+=1
            counts['r1_stock_dispatch_'+suffix]=count
    result=dict(application_sha256=sha(app),integration_report_sha256=sha(BASE/'report.json'),object_sha256=sha(obj),comparisons=sum(counts.values()),comparisons_by_entry=counts,null_table_fault_comparisons=faults,scope='Seven native dispatchers: return statuses, declared argument forwarding and null-table unmapped read address/width match stock',limitations=['Unmapped reads in Unicorn do not prove physical Cortex-M exception state.','Unused argument registers are outside each recovered operation ABI.'],instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'{sum(counts.values())} dispatch comparisons passed, including {faults} null-table fault comparisons')
if __name__=='__main__':main()
