#!/usr/bin/env python3
"""Capture named ADC descriptors from authenticated startup execution."""
import hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2]
def main():
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();digest=hashlib.sha256(image).hexdigest();assert digest=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x20000,0xc0000);uc.mem_write(0x27000,image);uc.mem_map(0x20000000,0x40000);uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.emu_start(0x283a1,0x27208,count=2000000);assert uc.reg_read(UC_ARM_REG_PC)==0x27208
    records=[]
    for i in range(3):
        address=0x20006ef8+40*i;data=bytes(uc.mem_read(address,40));words=struct.unpack('<10I',data)
        records.append(dict(address=hex(address),name=bytes(uc.mem_read(words[0],64)).split(b'\0')[0].decode(),words=[hex(x) for x in words],bytes=data.hex()))
    result=dict(application_sha256=digest,records=records,shared_ops_address='0x20006f70',shared_ops=[hex(x) for x in struct.unpack('<9I',bytes(uc.mem_read(0x20006f70,36)))],scope='Stock scatter-initialized data before runtime entry; no product init or physical ADC execution')
    output=ROOT/'r1/research/source-build/adc';output.mkdir(exist_ok=True);(output/'stock-initialization.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
