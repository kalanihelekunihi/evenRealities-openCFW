#!/usr/bin/env python3
"""Wrap authenticated stock bytes for analysis only; never a C-build input."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[2]


def main():
    source=Path('r1/blobs/official/r1-2.2.6.0009/application.bin')
    payload=(ROOT/source).read_bytes();digest=hashlib.sha256(payload).hexdigest()
    assert digest=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    output=ROOT/'r1/research/source-build/i2c5';output.mkdir(parents=True,exist_ok=True)
    target=output/'stock-r1-native-analysis.elf';commands=[]
    with tempfile.TemporaryDirectory(prefix='r1-stock-analysis-') as temporary:
        temp=Path(temporary);unbased=temp/'unbased.elf';relocatable=temp/'stock-analysis.elf';roundtrip=temp/'roundtrip.bin'
        commands.append(['arm-none-eabi-objcopy','-I','binary','-O','elf32-littlearm','-B','arm',
                         '--rename-section','.data=.text,alloc,load,readonly,code,contents',str(source),str(unbased)])
        commands.append(['arm-none-eabi-objcopy','--change-section-address','.text=0x27000','--set-start','0x504d9',
                         '--add-symbol','$t=.text:0,local',
                         '--add-symbol','r1_stock_gpio_pin_set=.text:0x52435,global,function',
                         '--add-symbol','r1_stock_i2c5_acquire=.text:0x294d9,global,function',
                         '--add-symbol','r1_stock_i2c5_release=.text:0x294c1,global,function',str(unbased),str(relocatable)])
        commands.append(['arm-none-eabi-ld','-Ttext=0x27000','--entry=r1_stock_i2c5_acquire',str(relocatable),'-o',str(target)])
        commands.append(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(target),str(roundtrip)])
        for command in commands:subprocess.run(command,cwd=ROOT,check=True)
        assert roundtrip.read_bytes()==payload
    data=target.read_bytes();assert struct.unpack_from('<H',data,16)[0]==2
    records=dict(application_sha256=digest,analysis_elf_sha256=hashlib.sha256(data).hexdigest(),
                 elf_type='ET_EXEC',text_load_address='0x27000',text_roundtrip_exact=True,
                 labels={'r1_stock_gpio_pin_set':'0x79434','r1_stock_i2c5_acquire':'0x504d8','r1_stock_i2c5_release':'0x504c0'},
                 commands=commands,scope='Analysis wrapper only. Retained executable bytes are never source-build or source-completeness inputs.',
                 loader_requirements='Import the ELF using automatic format detection. Explicit language invokes Ghidra-MCP raw import; ET_REL also causes a default rebase. Neither is suitable for these absolute stock addresses.')
    (output/'stock-analysis-wrapper.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Stock ET_EXEC analysis wrapper prepared; .text matches all 646408 original bytes at 0x27000')


if __name__=='__main__':main()
