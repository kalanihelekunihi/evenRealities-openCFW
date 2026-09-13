# SPDX-License-Identifier: MIT
"""Actual decoded lock-mask query governs tick suspend decision."""
import json,subprocess
from verify_gx8002_tws_tick import verify as qualify,execute,ROOT,Elf32,sha,decode
from verify_gx8002_power_locks import execute as query,word,BASE

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-source-candidate/power-locks/buffers.elf';elf=Elf32(path.read_bytes(),'locks');report=json.loads((ROOT/'docs/research/gx8002-power-locks-source-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');locks=decode(subprocess.check_output([pre,'-d',str(path)],text=True));code=decode(subprocess.check_output([pre,'-D','--start-address=0x1836c','--stop-address=0x183c8',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));cases=0;calls=0
    for mask in (0,0xffffffff,*(1<<i for i in range(32))):
      for standby in (2,4):
        observed=[]
        def hook(name,memory):
            if name!='LvpPmuSuspendIsLocked':return None
            state={};word(state,BASE,mask);result,after,events=query(locks,0x102077f8,state,0)
            assert result==int(bool(mask)) and after==state and events==[('read',BASE,mask)];observed.append(result);return result
        actual=execute(code,evidence['candidate']['bindings'],0,0,0,0,standby,0,91,helper_hook=hook);wanted=[('LvpQueueGet',)]
        if standby==4:
            wanted.append(('LvpPmuSuspendIsLocked',))
            if not mask:wanted.append(('LvpPmuSuspend',13))
        assert actual==wanted and len(observed)==int(standby==4);cases+=1;calls+=len(observed)
    return {'evidence':evidence,'cases':cases,'decoded_lock_calls':calls,'lock_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Actual decoded lock query reads every single lock bit plus zero/full mask. Suspend and other helpers remain modeled; no physical execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-tick-lock.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_lock_calls'])
