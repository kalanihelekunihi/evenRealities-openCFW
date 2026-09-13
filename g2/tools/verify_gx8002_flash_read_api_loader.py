# SPDX-License-Identifier: MIT
"""KWS model loader read calls through decoded flash read API."""
import json,subprocess
from itertools import product
from verify_gx8002_flash_read_api_callback import verify as qualify,ROOT
from execute_gx8002_kws_read_api import execute as loader
from execute_gx8002_clock_source_select import execute as api
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence=qualify();path=ROOT/'build/gx8002-kws-flash-load/loader.elf';elf=Elf32(path.read_bytes(),'loader');report=json.loads((ROOT/'docs/research/gx8002-kws-flash-load-source-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));wrapper=decode((ROOT/'build/gx8002-board/flash-read-api-candidate.disassembly.txt').read_text());calls=[];cases=0
    for commands,weights,first,second in product((0,3,9164),(0,1,120800),(0,0xffffffff),(0,0x80000000)):
        params=(commands,weights,0,13056,4);command=0x20003304;aligned=(commands+3)&0xfffffffc;weight=command+aligned;weight_size=(weights+3)&0xfffffffc
        def read(args,status):
            memory={};word(memory,args[0]+4,0x1002381c)
            def callback(target,parameters,state,events):
                assert target==0x1002381c and parameters[:3]==list(args[1:]);return status
            result,after,events=api(wrapper,0x100247b8,list(args),memory,callback)
            assert result[:2]==('return',status) and after==memory and not events
            calls.append(args);return result[1]
        actual=loader(code,0x10206cb0,params,True,0x20040000,(first,second),read)
        expected=[('probe',0x20040000),('read',0x20040000,0xf804,command,aligned),('read',0x20040000,0xf804+aligned,weight,weight_size),('print',0x1020adde,48)]
        if first|second:expected.append(('print',0x1020adf7,None))
        else:expected.append(('publish',(0,0x20000000,0x20000000,0,0,command,0x20003300,weight)))
        assert actual==expected;cases+=1
    assert len(calls)==72
    return {'evidence':evidence,'loader_cases':cases,'decoded_api_calls':len(calls),'source_admitted':False,
            'limits':['Decoded loader arguments/status branches flow through decoded read API; lower callback statuses scripted to exercise error propagation. Buffer transfer semantics remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-read-api-loader.json').write_text(json.dumps(r,indent=2)+'\n');print(r['loader_cases'],r['decoded_api_calls'])
