# SPDX-License-Identifier: MIT
"""Invoke decoded, source-authenticated standby loop within audio callback."""
import itertools,json,subprocess
from verify_gx8002_tws_audio import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,decode,execute,word,STATE
from verify_gx8002_tws_standby import execute as standby_execute

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-source-candidate/tws-standby/standby.elf';elf=Elf32(path.read_bytes(),'standby')
    report=json.loads((ROOT/'docs/research/gx8002-tws-standby-source-verification.json').read_text())
    row=next(r for r in report['functions'] if r['section_name']=='.loop');section=next(s for s in elf.sections if s['name']=='.loop')
    assert sha(elf.contents(section))==row['compiled_sha256'] and elf.contents(section)==stock[0x183d8:0x183f0]
    wrapper=out/'padmux-get-stock.elf';analysis=Elf32(wrapper.read_bytes(),'stock');assert analysis.contents(next(s for s in analysis.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x183d8','--stop-address=0x184e8',str(wrapper)],text=True));new=decode((out/'tws-audio.disassembly.txt').read_text());cases=0;calls=0
    def nested(memory):
        nonlocal calls
        values,trace=standby_execute(old,0x183d8,word(memory,STATE+76),word(memory,STATE+80),0)
        for a,v in values.items():word(memory,a,v)
        calls+=1
    for args in itertools.product((-1,0,14,15),(0,2),(0,1),(0,1),(0,1),(0,2,4),(0,1,50,0xffffffff),(91,)):
        actual=execute(new,0x100263dc,evidence['bindings'],*args,standby_hook=nested)
        assert actual==execute(old,0x183f0,evidence['bindings'],*args,standby_hook=nested)
        assert actual==execute(new,0x100263dc,evidence['bindings'],*args)
        cases+=1
    assert calls==2*cases*3//4
    return {'candidate':evidence,'standby_elf_sha256':sha(path.read_bytes()),'cases':cases,'decoded_helper_calls':calls,'source_admitted':False,'limits':['Source-authenticated exact standby instruction body executed at stock analysis addresses with callback state transferred at the call boundary. Other helpers modeled; no hardware or concurrency proof.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-audio-standby.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_helper_calls'])
