# SPDX-License-Identifier: MIT
"""Recovered digital LDO query driving decoded system startup branches."""
import json,subprocess
from verify_gx8002_digital_control import verify as qualify,ROOT
from execute_gx8002_system_control_query import execute,SYMBOLS
from execute_gx8002_clock_source_select import execute as leaf
from gx8002_lvp_system_oracle import expected
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence=qualify();path=ROOT/'build/gx8002-system-initialize/buffers.elf';elf=Elf32(path.read_bytes(),'system')
    report=json.loads((ROOT/'docs/research/gx8002-lvp-system-initialize-source-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    query=decode((ROOT/'build/gx8002-board/digital-control-candidate.disassembly.txt').read_text());calls=[];cases=0
    for value in range(256):
        control=(0,0,1,2)[(value>>1)&3]
        def run():
            memory={};word(memory,0xa0005058,value|0xa5a50000)
            result,after,events=leaf(query,0x10024710,[],memory,lambda *a:None)
            assert result[:2]==('return',control) and after==memory and not events
            calls.append(control);return result[1]
        for mode in (0,1,2,0xffffffff):
            result=execute(code,0x102078a4,mode,0x854012,control,3,7,run)
            assert result==expected(SYMBOLS,mode,0x854012,control,3,7)
            cases+=1
    assert len(calls)==512 and set(calls)=={0,1,2}
    return {'evidence':evidence,'system_cases':cases,'decoded_query_calls':len(calls),'system_elf_sha256':sha(path.read_bytes()),'source_admitted':False,
            'limits':['Decoded control query drives actual startup branch; other startup services remain modeled. Physical boot unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-digital-control-system.json').write_text(json.dumps(report,indent=2)+'\n');print(report['system_cases'],report['decoded_query_calls'])
