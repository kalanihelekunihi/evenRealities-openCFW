#!/usr/bin/env python3
"""Compare linked upstream-backed ARM crypto policy to authenticated R1 code."""
import hashlib
import json
from pathlib import Path
import random
import struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, __version__ as unicorn_version
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

ROOT=Path(__file__).resolve().parents[2]
APP_HASH='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
BASE=0x20000000; STOP=BASE+0x100; INPUT=BASE+0x1000; OUTPUT=BASE+0x4000; KEY=BASE+0x8000; LENGTH=BASE+0x9000; STACK=BASE+0x20000


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=ROOT/'r1/research/source-build/crypto'
    receipt=output/'verification.json';receipt.unlink(missing_ok=True)
    image=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
    assert hashlib.sha256(image).hexdigest()==APP_HASH
    report=json.loads((output/'report.json').read_text())
    assert digest(output/'two-pass.bin')==report['binary_sha256']
    for row in report['units']:assert digest(ROOT/row['source'])==row['source_sha256']
    for path,expected in report['headers'].items():assert digest(ROOT/path)==expected
    stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,image)
    candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate.mem_map(0x1000000,0x10000);candidate.mem_write(0x1000000,(output/'two-pass.bin').read_bytes())
    for uc in (stock,candidate):uc.mem_map(BASE,0x40000);uc.mem_write(STOP,b'\x00\xbe')

    def call(uc,entry,args):
        uc.reg_write(UC_ARM_REG_SP,STACK)
        uc.reg_write(UC_ARM_REG_LR,STOP|1)
        for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args[:4]):uc.reg_write(reg,value&0xffffffff)
        if len(args)>4:uc.mem_write(STACK,struct.pack('<'+'I'*(len(args)-4),*args[4:]))
        uc.emu_start(entry|1,STOP,count=100000000)
        assert uc.reg_read(UC_ARM_REG_PC)==STOP,'instruction budget exhausted'
        return uc.reg_read(UC_ARM_REG_R0)

    def prepare(uc,payload,key):
        uc.mem_write(INPUT,payload or b'\0');uc.mem_write(OUTPUT-16,bytes([0xa5])*(len(payload)+32))
        uc.mem_write(KEY,key);uc.mem_write(LENGTH,b'\xaa'*4)

    rng=random.Random(0x48b02)
    cases=[(bytes((i*37+length)&255 for i in range(length)),bytes(range(32))) for length in range(66)]
    cases += [(bytes(rng.randrange(256) for _ in range(length)),bytes(rng.randrange(256) for _ in range(32)))
              for length in [128,239,256,512,4096]+[rng.randrange(257) for _ in range(32)]]
    comparisons=0
    for index,(payload,key) in enumerate(cases):
        for uc in (stock,candidate):prepare(uc,payload,key)
        expected_return=call(stock,0x891a4,[INPUT,len(payload),KEY,OUTPUT,LENGTH])
        actual_return=call(candidate,report['symbols']['r1_stock_two_pass_callback'],[INPUT,len(payload),KEY,OUTPUT,LENGTH])
        assert expected_return==actual_return==0,index
        assert bytes(stock.mem_read(OUTPUT-16,len(payload)+32))==bytes(candidate.mem_read(OUTPUT-16,len(payload)+32)),index
        assert stock.mem_read(LENGTH,4)==candidate.mem_read(LENGTH,4)==struct.pack('<I',len(payload)),index
        assert stock.mem_read(INPUT,len(payload) or 1)==candidate.mem_read(INPUT,len(payload) or 1),index
        assert stock.mem_read(KEY,32)==candidate.mem_read(KEY,32)==key,index
        comparisons+=1
        # Direct six-argument entry separately checks key/argument ordering.
        if index%8==0:
            for uc in (stock,candidate):prepare(uc,payload,key)
            args=[INPUT,len(payload),KEY+16,KEY,OUTPUT,LENGTH]
            call(stock,0x48b02,args);call(candidate,report['symbols']['r1_stock_two_pass'],args)
            assert stock.mem_read(OUTPUT-16,len(payload)+32)==candidate.mem_read(OUTPUT-16,len(payload)+32),index
            comparisons+=1
    xor_comparisons=0
    for length in (-3,-1,0,1,15,16,64):
        for delta in (0,1,16,80):
            data=bytes(rng.randrange(256) for _ in range(160))
            for uc in (stock,candidate):uc.mem_write(OUTPUT,data)
            call(stock,0x98e22,[OUTPUT,OUTPUT+delta,length])
            call(candidate,report['symbols']['r1_stock_xor'],[OUTPUT,OUTPUT+delta,length])
            assert stock.mem_read(OUTPUT,160)==candidate.mem_read(OUTPUT,160),(length,delta)
            xor_comparisons+=1
    bodies=[dict(entry=hex(entry),bytes=size,sha256=hashlib.sha256(image[entry-0x27000:entry-0x27000+size]).hexdigest()) for entry,size in ((0x48b02,162),(0x891a4,20),(0x98e22,22))]
    record=dict(application_sha256=APP_HASH,candidate_binary_sha256=report['binary_sha256'],upstream_pin=report['upstream_pin'],unicorn_version=unicorn_version,
                bodies=bodies,payloads=len(cases),transform_comparisons=comparisons,xor_comparisons=xor_comparisons,random_seed='0x48b02',
                scope='Original stock Thumb including its AES core versus linked ARM C and pinned upstream AES; full output, length, buffer/key preservation and guards',
                limitations=['Transform calls use disjoint input/output/key/result buffers and nonnegative lengths.','Malformed pointers, negative transform lengths, overlapping transform buffers and all possible inputs are not proven.','This is component behavior testing, not stock instruction identity or an application firmware link.'],
                instruction_identity=False,application_linked=False)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(f'{comparisons} transform comparisons and {xor_comparisons} XOR comparisons passed; {len(cases)} payloads including partial blocks and 4096 bytes')


if __name__=='__main__':main()
