# SPDX-License-Identifier: MIT
"""Execute the recovered information API through the source-owned table callback."""
import json,struct,subprocess
from itertools import product
from verify_gx8002_flash_info_api import verify as qualify
from analyze_gx8002_upstream_objects import ROOT,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute
from compare_gx8002_flash_info import execute as query, oracle


def verify():
    prerequisite=qualify();owners={}
    for name,artifact in (('flash-interface-table','flash-interface-table.elf'),('flash-info','info.elf')):
        p=ROOT/f'docs/research/gx8002-{name}-verification.json';report=json.loads(p.read_text())
        path=ROOT/'build/gx8002-board'/artifact;elf=Elf32(path.read_bytes(),name)
        for row in report.get('functions',[report]):
            section=next(s for s in elf.sections if s['name']==row['section_name'])
            assert sha(elf.contents(section))==row['compiled_sha256'] and not elf.relocations(section['index'])
        owners[name]={'elf_sha256':sha(path.read_bytes()),'report_sha256':sha(p.read_bytes())}
        if name=='flash-interface-table':
            section=next(s for s in elf.sections if s['name']=='.data.flash_interface')
            assert section['address']==0x20026504
            target=struct.unpack_from('<I',elf.contents(section),52)[0]
    assert target==0x10023858
    code=decode((ROOT/'build/gx8002-board/flash-info-api-candidate.disassembly.txt').read_text())
    callback_code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(ROOT/'build/gx8002-board/info.elf')],text=True))
    info_elf=Elf32((ROOT/'build/gx8002-board/info.elf').read_bytes(),'info')
    table=struct.unpack('<14I',info_elf.contents(next(s for s in info_elf.sections if s['name']=='.rodata.flash_info')))
    cases=0
    for selector,pointer,size in product((*range(16),0x7fffffff,0x80000000,0xffffffff),(0,1,0x1020be54,0x80000000,0xffffffff),(0,4095,4096,4097,0xffffffff)):
        memory={};word(memory,0x20026538,target);calls=[]
        expected,effects=oracle(selector,pointer,pointer,size)
        def callback(destination,args,state,events):
            assert destination==target and args[0]==selector
            calls.append(destination)
            return query(callback_code,target,0,table,selector,effects)
        result,after,writes=execute(code,0x100247e0,[0x20026504,selector,23,31],memory,callback)
        assert result[:2]==('return',expected) and after==memory and not writes and calls==[target]
        cases+=1
    return {'prerequisite':prerequisite,'owners':owners,'composed_cases':cases,'source_admitted':False,'limits':['Decoded API and source-owned getinfo callback qualified; selected-device and size reads scripted. Device storage remains separately owned. No physical hardware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-info-api-callback-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
