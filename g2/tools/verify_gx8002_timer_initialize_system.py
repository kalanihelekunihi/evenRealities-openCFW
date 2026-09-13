# SPDX-License-Identifier: MIT
"""System startup invokes the decoded reconstructed timer initializer."""
import json,subprocess
from verify_gx8002_timer_initialize_shared import verify as qualify
from verify_gx8002_timer_initialize import execute as timer,expected as timer_expected,ROOT,decode,Elf32,sha
from execute_gx8002_system_timer import execute as system,SYMBOLS
from gx8002_lvp_system_oracle import expected

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-system-initialize/buffers.elf'
    report_path=ROOT/'docs/research/gx8002-lvp-system-initialize-source-verification.json';report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),'system')
    for row in report['functions']:
        sec=next(s for s in elf.sections if s['name']==row['section_name'])
        assert sha(elf.contents(sec))==row['compiled_sha256'] and not elf.relocations(sec['index'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    timer_code=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-initialize-candidate.elf')],text=True));cases=0;total=0
    for mode in (0,1,2,0xffffffff):
      for seed in (0,1,91):
        for hz in (0,1024000,24576000,0xffffffff):
            calls=[]
            def run():
                trace=timer(timer_code,0x100257e8,hz,seed)
                assert trace==timer_expected(hz);calls.append(trace)
            result=system(code,0x102078a4,mode,0x854012,2,3,seed,timer_runner=run)
            wanted=expected(SYMBOLS,mode,0x854012,2,3,seed)
            assert result==wanted
            assert len(calls)==sum(event==('gx_timer_init',) for event in wanted[0])
            total+=len(calls);cases+=1
    assert total>0
    return {'evidence':evidence,'system_elf_sha256':sha(path.read_bytes()),'system_report_sha256':sha(report_path.read_bytes()),'system_cases':cases,'decoded_timer_calls':total,'source_admitted':False,'limits':['Actual decoded system startup timer call executes reconstructed initializer; system outputs/order match independent oracle. Timer helpers modeled in this caller check, separately composed in prerequisite checks. Whole-system shared peripheral state and physical startup unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-initialize-system.json').write_text(json.dumps(r,indent=2)+'\n');print(r['system_cases'],r['decoded_timer_calls'])
