# SPDX-License-Identifier: MIT
"""Decoded system startup feeds arguments through reconstructed probe wrapper."""
import json,subprocess
from verify_gx8002_flash_probe_interface import verify as qualify,ROOT
from execute_gx8002_system_probe import execute as system,SYMBOLS
from execute_gx8002_flash_probe import execute as probe
from gx8002_lvp_system_oracle import expected
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence=qualify();path=ROOT/'build/gx8002-system-initialize/buffers.elf';elf=Elf32(path.read_bytes(),'system');report=json.loads((ROOT/'docs/research/gx8002-lvp-system-initialize-source-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(path)],text=True));probe_code=decode((ROOT/'build/gx8002-board/flash-probe-candidate.disassembly.txt').read_text());calls=[];cases=0
    for mode in (0,1,2,0xffffffff):
        for seed in (0,7,91):
            for retry in (False,True):
                def run(args,want):
                    states=(0,0);times=(0,4999999);results=(0,want) if retry else (want,)
                    result,trace=probe(probe_code,0x1002475c,args,states,times,results)
                    assert result==want and trace[-1]==('write_state',1)
                    assert [x[1:] for x in trace if x[0]=='probe']==[args]*(2 if retry else 1)
                    calls.append(trace);return result
                actual=system(code,0x102078a4,mode,0x854012,2,3,seed,probe_runner=run)
                assert actual==expected(SYMBOLS,mode,0x854012,2,3,seed);cases+=1
    assert len(calls)==12
    return {'evidence':evidence,'system_cases':cases,'decoded_probe_calls':len(calls),'source_admitted':False,
            'limits':['Actual system probe arguments and returned device pointer flow through decoded wrapper; retry path checked.',
                       'Probe callback/timer values modeled in this caller test and separately decoded in dependency tests; whole-system peripheral execution unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-probe-system.json').write_text(json.dumps(r,indent=2)+'\n');print(r['system_cases'],r['decoded_probe_calls'])
