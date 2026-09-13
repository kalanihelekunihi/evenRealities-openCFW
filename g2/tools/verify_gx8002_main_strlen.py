# SPDX-License-Identifier: MIT
"""Qualify the main-image strlen using the reviewed source libc leaf."""
import json,subprocess,shutil
from pathlib import Path
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_gx8002_stage2_libc_candidate import build
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_stage2_libc import execute,base_registers,load_buffer
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build(prefix=prefix)
    symbol='open_cfw_gx8002_stage2_strlen'
    obj=Path(candidate['object']);elf=Elf32(obj.read_bytes(),str(obj))
    section=next(s for s in elf.sections if s['name']=='.text.'+symbol)
    payload=elf.contents(section)
    if len(payload)>16 or elf.relocations(section['index']):raise ValueError('Main strlen placement')
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';wrapped=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(wrapped.contents(next(s for s in wrapped.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x1022c','--stop-address=0x1023c',str(wrapper)],text=True))
    new=decode(subprocess.check_output([pre,'-d','--section='+section['name'],str(obj)],text=True));cases=0
    for length in (*range(256),511,1023):
        data=bytes((i%255)+1 for i in range(length))+b'\0'
        for alignment in range(4):
            base=0x20030000+alignment;memory={};load_buffer(memory,base,data)
            for code,entry in ((old,0x1022c),(new,0)):
                registers=base_registers();registers['r0']=base
                if execute(code,entry,registers,memory)!=length:raise ValueError('Main strlen effects')
            cases+=1
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(obj,output/'main-strlen.o')
    row={'symbol':symbol,'section_name':section['name'],'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_occurrences':[{'symbol':symbol,'package_offset':0x1022c,'bytes':16,'sha256':sha(stock[0x1022c:0x1023c]),'region':'image_a_xip_text'}]}
    return {'functions':[row],'candidate':candidate,'decoded_cases':cases,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_main_strlen.py','verify_gx8002_stage2_libc.py','build_gx8002_stage2_libc_candidate.py')},'source_admitted':True,'hardware_qualified':False,'limits':['Valid terminated readable buffers; strict unmapped reads and preserved registers checked. Timing and address wrap not qualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-main-strlen-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
