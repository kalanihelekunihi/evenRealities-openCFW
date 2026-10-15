#!/usr/bin/env python3
"""Read native TWI configuration by executing authenticated stock scatter load.
Analysis only: never emits executable firmware or retained-code build inputs.
"""
import hashlib,json,struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2]
def main():
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();digest=hashlib.sha256(image).hexdigest()
    assert digest=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x20000,0xc0000);uc.mem_write(0x27000,image);uc.mem_map(0x20000000,0x40000);uc.reg_write(UC_ARM_REG_SP,0x2003f000)
    uc.emu_start(0x283a1,0x27208,count=2000000);assert uc.reg_read(UC_ARM_REG_PC)==0x27208
    def string(address):return bytes(uc.mem_read(address,64)).split(b'\0')[0].decode()
    records=[]
    for i in range(4):
        address=0x20007400+112*i;data=bytes(uc.mem_read(address,112));words=struct.unpack('<28I',data)
        records.append(dict(address=hex(address),name=string(words[0]),opened=data[4],delay_context=words[2],scl_pin=words[3],sda_pin=words[4],callbacks={name:hex(words[index]) for name,index in [('drive_low',5),('release_high',6),('set_output',7),('set_input',8),('udelay',10),('read_pin',11),('pin_release',12)]},input_pull=data[36],ops=[hex(x) for x in words[19:28]],record_sha256=hashlib.sha256(data).hexdigest()))
    output=ROOT/'r1/research/source-build/software-twi/stock-initialization.json'
    output.write_text(json.dumps(dict(application_sha256=digest,scatter_entry='0x283a0',stop_before_runtime_entry='0x27208',scatter_table_image_bytes=image[0xc43ec-0x27000:0xc440c-0x27000].hex(),records=records,scope='Stock scatter execution only, before product initialization; callback addresses are references, not source closure'),indent=2)+'\n')
    print(json.dumps(records,indent=2))
if __name__=='__main__':main()
