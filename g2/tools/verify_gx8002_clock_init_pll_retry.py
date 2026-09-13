# SPDX-License-Identifier: MIT
"""Full init retry sequence through decoded PLL wait, configure and timer."""
import json,subprocess
from verify_gx8002_clock_init_paths import verify as paths
from execute_gx8002_clock_pll_wait import execute
from verify_gx8002_clock_pll_wait import expected
from verify_gx8002_clock_pll import execute as configure,oracle,OFFSETS
from verify_gx8002_clock_time_us_candidate import execute as timer
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha
from verify_gx8002_memcpy_source import decode


def verify():
    codes={};hashes={};pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    for name in ('clock-pll-wait','clock-pll','clock-time-us'):
        path=ROOT/f'build/gx8002-board/{name}-candidate.elf';elf=Elf32(path.read_bytes(),name);r=json.loads((ROOT/f'docs/research/gx8002-{name}-source-verification.json').read_text())
        for row in r['functions']:
            section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
        codes[name]=decode(subprocess.check_output([pre,'-d',str(path)],text=True));hashes[name]=sha(path.read_bytes())
    calls=[]
    def retry(fields,timeout,want_return):
        assert fields[0]==1 and timeout==40
        registers={off:((len(calls)+off)*0x12345)&0xffffffff for off in OFFSETS};want_config=oracle(True,fields,registers,0)
        def config(enable):
            assert enable==1;result=configure(codes['clock-pll'],0x10024b04,True,fields,registers,0);assert result==want_config;return result[0]
        def convert(ticks):return timer(codes['clock-time-us'],ticks&0xffffffff,ticks>>32)
        locks=[0,8] if want_return==0 else [0];ticks=[0,40960] if want_return==0 else [0,41984]
        result=execute(codes['clock-pll-wait'],0x1002500c,1,timeout,1,locks,ticks,convert,config)
        want=expected(False,1,timeout,locks,[0,40000] if want_return==0 else [0,41000]);want=(want[0],want[1],want[2][:1]+want_config[0]+want[2][1:])
        assert result==want and result[1]==want_return;calls.append(fields[5]);return result[1]
    evidence=paths(pll_retry_runner=retry);assert len(calls)==40
    return {'evidence':evidence,'decoded_retry_calls':len(calls),'dependency_elf_sha256':hashes,'source_admitted':False,'limits':['Outer retries use decoded configure/wait/timer with actual changing feedback fields. Lock samples scripted; private configuration MMIO snapshots marshalled rather than propagated to outer state. Full shared-state integration and hardware timing remain pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-init-pll-retry.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_retry_calls'])
