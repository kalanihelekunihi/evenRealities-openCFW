#!/usr/bin/env python3
"""Compare integrated ST25/i2c_5/registry paths with authenticated stock code."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, __version__ as unicorn_version
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'r1/research/source-build/i2c5'
STATE=0x20006838; DEVICE=0x20002000; OPS=0x20002100; STOP=0x20000100
OP_OPEN=0x100e000;OP_CLOSE=0x100e010;OP_READ=0x100e020;OP_WRITE=0x100e030;DELAY=0x100f000


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    receipt=BASE/'verification.json';receipt.unlink(missing_ok=True)
    application=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=application.read_bytes()
    assert sha(application)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    assert struct.unpack_from('<I',image,0x50530-0x27000)[0]==STATE+8
    assert struct.unpack_from('<I',image,0x50554-0x27000)[0]==STATE+8
    report=json.loads((BASE/'report.json').read_text())
    for row in report['units']:
        assert sha(ROOT/row['source'])==row['source_sha256']
        assert sha(Path(row['command'][-1]))==row['object_sha256']
    for path,expected in report['headers'].items():assert sha(ROOT/path)==expected
    integrated=BASE/'st25-i2c5-registry.o';assert sha(integrated)==report['relocatable_sha256']
    roots={'r1_st25dvxxkc_bus_read':0x44c84,'r1_st25dvxxkc_bus_write':0x44c8a,
           'r1_i2c5_read_transfer':0x50510,'r1_i2c5_write_transfer':0x50534,
           'r1_i2c5_nfc_resource_acquire':0x504d8,'r1_i2c5_nfc_resource_release':0x504c0}
    records={};comparisons=0
    with tempfile.TemporaryDirectory(prefix='r1-i2c5-integration-') as temporary:
        temp=Path(temporary);script=temp/'layout.ld';elf=temp/'integrated.elf';binary=temp/'integrated.bin'
        script.write_text('''SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .ARM.exidx : { *(.ARM.exidx*) }
 .r1.i2c5.state 0x20006838 (NOLOAD) : { *(.r1.i2c5.state) }
 /DISCARD/ : { *(.comment) *(.note*) }
}''')
        command=['arm-none-eabi-ld','-T',str(script),'--gc-sections','--entry=r1_st25dvxxkc_bus_read',
                 *['--undefined='+name for name in roots], '--defsym=r1_st25_delay_ms='+hex(DELAY|1),str(integrated),'-o',str(elf)]
        linked=subprocess.run(command,check=True,capture_output=True,text=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        lines=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
        symbols={line.split()[-1]:int(line.split()[0],16) for line in lines if len(line.split())==3}
        assert symbols['r1_i2c5_state']==STATE
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,image)
        candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        traces={id(stock):[],id(candidate):[]};status=[0]
        operation_names={OP_OPEN:'open',OP_CLOSE:'close',OP_READ:'read',OP_WRITE:'write'}
        for uc in (stock,candidate):
            uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x30000);uc.mem_map(0x50000000,0x1000);uc.mem_write(STOP,b'\x00\xbe')
        candidate.mem_write(0x1000000,binary.read_bytes())
        def observe(uc,address,size,delay_addresses):
            if address in delay_addresses:
                traces[id(uc)].append(('delay_ms',uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
            elif address in operation_names:
                name=operation_names[address]
                if name in ('read','write'):
                    args=[uc.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
                    traces[id(uc)].append((name,args,bytes(uc.mem_read(args[2],20))))
                else:traces[id(uc)].append((name,uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_R0,status[0]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        def mmio(uc,access,address,size,value,user):
            traces[id(uc)].append(('mmio_write',address,size,value))
        stock.hook_add(UC_HOOK_CODE,observe,{0x784d0,0x784f0})
        candidate.hook_add(UC_HOOK_CODE,observe,{DELAY})
        for uc in (stock,candidate):uc.hook_add(UC_HOOK_MEM_WRITE,mmio,begin=0x50000000,end=0x50000fff)
        def prepare(uc,mode):
            block=bytearray((i*29+17)&255 for i in range(28));struct.pack_into('<I',block,4,0 if mode==0 else DEVICE)
            uc.mem_write(STATE,bytes(block));uc.mem_write(DEVICE,struct.pack('<6I',0,OPS,0,0,0,0))
            operations=[0]*9
            if mode==2:
                for index,address in ((2,OP_OPEN),(3,OP_CLOSE),(4,OP_READ),(5,OP_WRITE)):operations[index]=address|1
            uc.mem_write(OPS,struct.pack('<9I',*operations));uc.mem_write(0x50000000,bytes(4096))
        def call(uc,entry,args,return_value):
            traces[id(uc)].clear();status[0]=return_value
            uc.reg_write(UC_ARM_REG_SP,0x2002f000);uc.reg_write(UC_ARM_REG_LR,STOP|1)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(reg,value)
            uc.emu_start(entry|1,STOP,count=10000);assert uc.reg_read(UC_ARM_REG_PC)==STOP
            return uc.reg_read(UC_ARM_REG_R0),list(traces[id(uc)]),bytes(uc.mem_read(STATE,28))
        for name,entry in roots.items():
            count=0
            if 'resource_' in name:
                for mode in (0,1,2):
                    for value in (0,0x87654321):
                        for uc in (stock,candidate):prepare(uc,mode)
                        a=call(stock,entry,[0,0,0,0],value);b=call(candidate,symbols[name],[0,0,0,0],value)
                        # Resource APIs are void. Compare observable order/state, not an incidental return register.
                        assert a[1:]==b[1:],(name,mode,a,b)
                        count+=1
            else:
                addresses=(0,0xa6,0x1a6,0xffae) if 'st25' in name else (0,0xa6,0xae,0xff)
                for mode in (0,1,2):
                    for address in addresses:
                        for length in (0,1,257,65535):
                            for data in (0,0x20001000):
                                for value in (0,0x87654321):
                                    for uc in (stock,candidate):prepare(uc,mode)
                                    args=[address,0x2034,data,length]
                                    a=call(stock,entry,args,value);b=call(candidate,symbols[name],args,value)
                                    assert a==b,(name,mode,args,a,b)
                                    count+=1
            records[name]=count;comparisons+=count
        # A non-NULL write followed by a NULL write retains the previous data pointer.
        for uc in (stock,candidate):prepare(uc,2)
        for data in (0x20001000,0):
            a=call(stock,0x44c8a,[0x1a6,0x1234,data,7],0)
            b=call(candidate,symbols['r1_st25dvxxkc_bus_write'],[0x1a6,0x1234,data,7],0)
            assert a==b
            assert struct.unpack_from('<I',a[2],12)[0]==0x20001000
            comparisons+=1
    result=dict(application_sha256=sha(application),integration_report_sha256=sha(BASE/'report.json'),
                relocatable_sha256=report['relocatable_sha256'],unicorn_version=unicorn_version,
                comparisons=comparisons,comparisons_by_entry=records,shared_state_address=hex(STATE),
                shared_request_address=hex(STATE+8),linker_test_seam_diagnostics=linked.stderr,
                scope='Actual compiled ST25 veneers, shared transport and registry dispatch compared with stock; only final bus operations and delays are intercepted',
                limitations=['Bus electrical behavior and real elapsed delay remain unverified.','NULL operation-table pointers are covered separately by registry-dispatch-verification.json.',
                             'Resource functions have void contracts; incidental R0 values are not compared.','This receipt does not test boot discovery; see registry-bootstrap-verification.json. Actual board record population and a complete application link remain open.'],
                application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(f'{comparisons} integrated i2c_5 comparisons passed, including request bytes, registry dispatch and ordered GPIO/delay actions')


if __name__=='__main__':main()
