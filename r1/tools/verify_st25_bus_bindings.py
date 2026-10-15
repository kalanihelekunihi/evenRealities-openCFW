#!/usr/bin/env python3
"""Check six R1 ST25 veneers against stock with observed provider call seams."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, __version__ as unicorn_version
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

ROOT=Path(__file__).resolve().parents[2]
PAIRS=[('r1_st25dvxxkc_bus_tick_get',0x44c58,6),('r1_st25dvxxkc_bus_deinitialize',0x44c64,10),
       ('r1_st25dvxxkc_bus_initialize',0x44c6e,10),('r1_st25dvxxkc_bus_is_ready',0x44c78,12),
       ('r1_st25dvxxkc_bus_read',0x44c84,6),('r1_st25dvxxkc_bus_write',0x44c8a,6)]
SEAMS=[('r1_i2c5_nfc_resource_release',0x504c0,0x100f000),
       ('r1_i2c5_nfc_resource_acquire',0x504d8,0x100f010),('r1_st25_delay_ms',0x784f0,0x100f020),
       ('r1_i2c5_read_transfer',0x50510,0x100f030),('r1_i2c5_write_transfer',0x50534,0x100f040)]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=ROOT/'r1/research/source-build/sensors';receipt=output/'st25-bus-verification.json';receipt.unlink(missing_ok=True)
    application=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=application.read_bytes()
    assert sha(application)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    table=list(struct.unpack_from('<6I',image,0x44c34-0x27000))
    assert table==[0x44c6f,0x44c65,0x44c79,0x44c85,0x44c8b,0x44c59]
    assert struct.unpack_from('<I',image,0x44c60-0x27000)[0]==0x40011504
    report=json.loads((output/'report.json').read_text());row=report['units'][-1]
    assert sha(ROOT/row['source'])==row['source_sha256']
    assert sha(ROOT/'r1/components/st25/stock_bus_bindings.h')==report['r1_binding_header_sha256']
    obj=Path(row['command'][-1]);assert row['compiled'] and sha(obj)==row['object_sha256']
    with tempfile.TemporaryDirectory(prefix='r1-st25-bus-') as temporary:
        temp=Path(temporary);elf=temp/'bindings.elf';binary=temp/'bindings.bin'
        command=['arm-none-eabi-ld','-Ttext=0x01000000','--gc-sections','--entry='+PAIRS[0][0],
                 *['--undefined='+name for name,_,_ in PAIRS],
                 *['--defsym='+name+'='+hex(candidate|1) for name,_,candidate in SEAMS],str(obj),'-o',str(elf)]
        link_result=subprocess.run(command,check=True,capture_output=True,text=True)
        assert not subprocess.check_output(['arm-none-eabi-nm','-u',str(elf)],text=True).strip()
        subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
        lines=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines()
        symbols={line.split()[-1]:int(line.split()[0],16) for line in lines if len(line.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,image)
        candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate.mem_map(0x1000000,0x10000);candidate.mem_write(0x1000000,binary.read_bytes())
        stop=0x20000100;registers=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
        traces={id(stock):[],id(candidate):[]};return_status=[0]
        def hook(uc,address,size,targets):
            if address not in targets:return
            name=targets[address];args=[uc.reg_read(r) for r in registers]
            # Only semantic arguments are part of the recovered seam contract.
            count=1 if name=='r1_st25_delay_ms' else 4 if 'transfer' in name else 0
            traces[id(uc)].append((name,args[:count]))
            uc.reg_write(UC_ARM_REG_R0,return_status[0]&0xffffffff)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        for uc,index in ((stock,1),(candidate,2)):
            uc.mem_map(0x20000000,0x10000);uc.mem_write(stop,b'\x00\xbe');uc.mem_map(0x40011000,0x1000)
            uc.hook_add(UC_HOOK_CODE,hook,{row[index]:row[0] for row in SEAMS})
        def execute(uc,entry,args,tick,status):
            traces[id(uc)].clear();return_status[0]=status
            uc.mem_write(0x40011504,struct.pack('<I',tick));uc.reg_write(UC_ARM_REG_SP,0x2000f000);uc.reg_write(UC_ARM_REG_LR,stop|1)
            for reg,value in zip(registers,args):uc.reg_write(reg,value)
            uc.emu_start(entry|1,stop,count=1000);assert uc.reg_read(UC_ARM_REG_PC)==stop
            return uc.reg_read(UC_ARM_REG_R0),list(traces[id(uc)])
        comparisons=0
        for name,entry,_ in PAIRS:
            for address in (0,0xa6,0x1a6,0xffae,0xffff):
                for status in (0,-1,0x1234):
                    args=[address,0x2034,0x20001000,0x1234]
                    tick=(address*65537)&0xffffffff
                    a=execute(stock,entry,args,tick,status);b=execute(candidate,symbols[name],args,tick,status)
                    assert a==b,(name,address,status,a,b)
                    if name.endswith('tick_get'):assert a[0]==tick and not a[1]
                    if name.endswith('is_ready'):assert a==(0,[('r1_st25_delay_ms',[10])])
                    if name.endswith(('bus_read','bus_write')):assert a[1][0][1][0]==address&255
                    comparisons+=1
    record=dict(application_sha256=sha(application),source_sha256=row['source_sha256'],object_sha256=row['object_sha256'],
                binding_header_sha256=report['r1_binding_header_sha256'],unicorn_version=unicorn_version,comparisons=comparisons,literal_pool_order=[hex(x) for x in table],
                io_structure_order=['Init','DeInit','IsReady','Write','Read','GetTick'],
                tick_register='0x40011504',readiness_delay_ms=10,
                bodies=[dict(name=name,entry=hex(entry),bytes=size,sha256=hashlib.sha256(image[entry-0x27000:entry-0x27000+size]).hexdigest()) for name,entry,size in PAIRS],
                linker_test_seam_diagnostics=link_result.stderr,scope='Stock and candidate veneer return values, semantic provider call arguments and raw RTC counter reads under emulated call seams',
                limitations=['Resource, bus and delay implementations are intercepted as test seams, not firmware provider implementations.',
                             'Registration root compiles but is not tested by this veneer-only link.',
                             'No actual bus transfer, elapsed timing, device initialization, hardware behavior or complete firmware link is established.'],
                application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(f'{comparisons} ST25 bus veneer comparisons passed; address truncation, call contracts and RTC reads agree')


if __name__=='__main__':main()
