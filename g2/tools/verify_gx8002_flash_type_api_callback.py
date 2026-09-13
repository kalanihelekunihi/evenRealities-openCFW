# SPDX-License-Identifier: MIT
"""Execute the recovered type API through the source-owned table callback."""
import json,struct
from verify_gx8002_flash_type_api import verify as qualify
from analyze_gx8002_upstream_objects import ROOT,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_clock_source_select import execute
from compare_gx8002_flash_info import execute as query


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
            target=struct.unpack_from('<I',elf.contents(section),48)[0]
    assert target==0x10024244
    code=decode((ROOT/'build/gx8002-board/flash-type-api-candidate.disassembly.txt').read_text())
    callback_code=decode((ROOT/'build/gx8002-board/info-linked.disassembly.txt').read_text())
    cases=0
    for pointer in (0,1,0x1020be54,0x80000000,0xffffffff):
        memory={};word(memory,0x20026534,target);calls=[]
        def callback(destination,args,state,events):
            assert destination==target
            calls.append(destination)
            return query(callback_code,target,0,(),0,[['read32',0x200264f0,0x20029000],['read32',0x20029000,pointer]])
        result,after,writes=execute(code,0x100247d4,[0x20026504,17,23,31],memory,callback)
        assert result[:2]==('return',pointer) and after==memory and not writes and calls==[target]
        cases+=1
    return {'prerequisite':prerequisite,'owners':owners,'composed_cases':cases,'source_admitted':False,'limits':['Decoded API and source-owned gettype callback qualified; selected-device state reads scripted. Returned string storage remains separately owned. No physical hardware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-type-api-callback-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['composed_cases'])
