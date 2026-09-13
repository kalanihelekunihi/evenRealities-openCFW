# SPDX-License-Identifier: MIT
"""Helper-boundary shared-context mutation comparison for TWS audio callback."""
import itertools,json,subprocess
from verify_gx8002_tws_audio import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,decode,execute,word,CTX,STATE

def verify():
    evidence=build();out=ROOT/'build/gx8002-board'
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    elf=Elf32((out/'padmux-get-stock.elf').read_bytes(),'stock analysis')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x183f0','--stop-address=0x184e8',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'tws-audio.disassembly.txt').read_text());cases=0
    for index,kws_index,kws_vad,print_vad,print_last in itertools.product((14,15),(14,15,30),(0,1,7),(0,1,7),(0,1,7)):
        def mutate(name,memory):
            if name=='LvpKwsRun':
                word(memory,CTX+8,kws_index);memory[CTX+12]=(memory[CTX+12]&~7)|kws_vad
            elif name=='printf':
                memory[CTX+12]=(memory[CTX+12]&~7)|print_vad
                word(memory,STATE+84,print_last);word(memory,CTX+8,91)
        args=(index,2,1,0,0,2,1,91)
        actual=execute(new,0x100263dc,evidence['bindings'],*args,hook=mutate)
        assert execute(old,0x183f0,evidence['bindings'],*args,hook=mutate)==actual
        logged=kws_index%15==0 or kws_vad!=0
        assert actual[2][-1]==('LvpTriggerAppEvent',91,91 if logged else kws_index)
        assert [e for e in actual[2] if e[0]=='printf']==([('printf',kws_index,kws_vad,3,0)] if logged else [])
        assert word(actual[1],STATE+84)==(print_vad if logged else 0)
        cases+=1
    return {'candidate':evidence,'cases':cases,'source_admitted':False,'limits':['Scripted KWS and printf mutations verify context index/VAD and last-VAD reloads plus emitted event payload. No asynchronous interrupt or concurrent memory-access ordering proof.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-audio-mutation.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
