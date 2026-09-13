# SPDX-License-Identifier: MIT
"""Decoded tick observes decoder/read-update changes before emitting events."""
import json,itertools,subprocess
from verify_gx8002_tws_tick import verify as qualify,execute,ROOT,decode

def verify():
    evidence=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x1836c','--stop-address=0x183c8',str(path)],text=True));cases=0
    for module,initial_kws,decoded_kws,updated_kws,after_standby,locked in itertools.product((0,256),(0,7),(0,23),(0,91),(2,4),(0,1)):
        calls=[]
        def hook(name,memory):
            calls.append(name)
            if name=='LvpDoMaxDecoder':memory[0x2005000d]=decoded_kws;memory[0x20050008]=123
            elif name=='LvpAudioInUpdateReadIndex':memory[0x2005000d]=updated_kws;memory[0x20050008]=456;memory[0x2002e738]=after_standby
            elif name=='LvpTriggerAppEvent':memory[0x2002e738]=after_standby
        result=execute(code,evidence['candidate']['bindings'],1,module,initial_kws,999,2,locked,91,helper_hook=hook)
        wanted=[('LvpQueueGet',)]
        if module==256:wanted.extend([('LvpDoMaxDecoder',0x20050000),('LvpAudioInUpdateReadIndex',1)])
        keyword=updated_kws if module==256 else initial_kws;index=456 if module==256 else 999
        if keyword:wanted.append(('LvpTriggerAppEvent',keyword,index))
        state=after_standby if module==256 or keyword else 2
        if state==4:
            wanted.append(('LvpPmuSuspendIsLocked',))
            if not locked:wanted.append(('LvpPmuSuspend',13))
        assert result==wanted and calls==[x[0] for x in wanted];cases+=1
    return {'evidence':evidence,'mutation_cases':cases,'source_admitted':False,'limits':['Scripted decoder/read-update/event mutations prove post-call context and standby reads. Helper machine code and physical concurrency remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-tick-mutation.json').write_text(json.dumps(r,indent=2)+'\n');print(r['mutation_cases'])
