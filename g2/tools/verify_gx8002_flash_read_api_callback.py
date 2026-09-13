# SPDX-License-Identifier: MIT
"""Read API dispatch through source-owned table to decoded chunking callback."""
import json,struct,subprocess
from verify_gx8002_flash_read_api import verify as qualify,ROOT
from compare_gx8002_flash_read import execute as read,oracle
from execute_gx8002_clock_source_select import execute
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence=qualify();directory=ROOT/'build/gx8002-board';artifacts={}
    for kind,filename in (('flash-interface-table','flash-interface-table.elf'),('flash-read','read.elf')):
        path=directory/filename;elf=Elf32(path.read_bytes(),kind);report=json.loads((ROOT/f'docs/research/gx8002-{kind}-verification.json').read_text())
        for row in report.get('functions',[report]):
            section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
        artifacts[kind]=elf
    table=artifacts['flash-interface-table'];data=table.contents(next(s for s in table.sections if s['name']=='.data.flash_interface'));target=struct.unpack_from('<I',data,4)[0];assert target==0x1002381c
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(directory/'read.elf')],text=True));wrapper=decode((directory/'flash-read-api-candidate.disassembly.txt').read_text());calls=[]
    for address in (0,0xfffffff0):
        for length in (0,1,65535,65536,65537,131072,0x80000000,0xffffffff):
            memory={};word(memory,0x20026508,target);args=[0x20026504,address,0x20040000,length]
            def callback(destination,parameters,state,events):
                assert destination==target and parameters[:3]==args[1:]
                result=read(code,target,0,*parameters[:3],0xffffffff)
                assert result==oracle(*parameters[:3]);calls.append(result[1]);return result[0]
            result,after,events=execute(wrapper,0x100247b8,args,memory,callback)
            assert result[:2]==('return',0) and after==memory and not events
    assert len(calls)==16
    return {'evidence':evidence,'decoded_read_callbacks':len(calls),'source_table_target':target,'source_admitted':False,
            'limits':['Source-generated callback slot authenticated; actual decoded read chunking drives wrapper return.',
                       'Lower-level wait/read_words callback and buffer transfer effects remain modeled as in admitted read qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-read-api-callback.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_read_callbacks'])
