# SPDX-License-Identifier: MIT
"""Decoded FIFO get feeds tick local record at actual addresses."""
import json,itertools,subprocess
from verify_gx8002_tws_tick import verify as qualify,execute,ROOT,decode,Elf32,sha
from execute_gx8002_active_queue import execute as get

def verify():
    evidence=qualify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-board'
    path=ROOT/'build/gx8002-source-candidate/queue_get/queue-size.o';elf=Elf32(path.read_bytes(),'get');report=json.loads((ROOT/'docs/research/gx8002-queue-get-comparison.json').read_text());section=next(s for s in elf.sections if s['name']==report.get('section_name','.text.'+report['symbol']));assert sha(elf.contents(section))==report['compiled_sha256']
    queue=decode(subprocess.check_output([pre,'-dr','--section='+section['name'],str(path)],text=True));code=decode(subprocess.check_output([pre,'-D','--start-address=0x1836c','--stop-address=0x183c8',str(out/'padmux-get-stock.elf')],text=True));cases=0
    for head,tail,module,kws in itertools.product(range(0,56,8),range(0,56,8),(0,256),(0,7)):
        observed=[]
        def hook(name,words):
            if name!='LvpQueueGet':return None
            memory={0x2002e700+i:(i*73+19)&255 for i in range(56)}
            for base,values in ((0x2002e6ec,(tail,head,0x2002e700,56,8)),(0x2006ffec,(0,0)),(0x2002e700+head,(module,0x20050000))):
                for n,value in enumerate(values):
                    for i in range(4):memory[base+4*n+i]=(value>>(8*i))&255
            before=memory.copy();result,trace=get(queue,memory,0,0x2002e6ec,0x2006ffec);wanted=before.copy()
            if tail!=head:
                for i in range(8):wanted[0x2006ffec+i]=before[0x2002e700+(head+i)%56]
                for i in range(4):wanted[0x2002e6f0+i]=(((head+8)%56)>>(8*i))&255
            assert result==int(tail!=head) and memory==wanted
            for a in (0x2006ffec,0x2006fff0):words[a]=sum(memory[a+i]<<(8*i) for i in range(4))
            observed.append(result);return result
        actual=execute(code,evidence['candidate']['bindings'],0,0,kws,123,2,0,91,helper_hook=hook)
        wanted=[('LvpQueueGet',)]
        if head!=tail:
            if module==256:wanted.extend([('LvpDoMaxDecoder',0x20050000),('LvpAudioInUpdateReadIndex',1)])
            if kws:wanted.append(('LvpTriggerAppEvent',kws,123))
        assert actual==wanted and observed==[int(head!=tail)];cases+=1
    return {'evidence':evidence,'queue_cases':cases,'queue_object_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Actual decoded queue reads fill tick stack record; complete byte-memory oracle validates wrap and empty queue. Other helpers and context remain modeled; no physical execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-tick-queue.json').write_text(json.dumps(r,indent=2)+'\n');print(r['queue_cases'])
