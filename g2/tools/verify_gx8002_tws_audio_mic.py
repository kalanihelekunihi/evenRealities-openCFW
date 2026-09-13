# SPDX-License-Identifier: MIT
"""TWS callback invokes authenticated decoded source microphone indexing."""
import itertools,json,subprocess
from verify_gx8002_tws_audio import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,decode,execute,word,CTX,HEADER
from verify_gx8002_mic_frame import execute as mic_execute

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-source-candidate/mic-frame/index.elf';elf=Elf32(path.read_bytes(),'mic')
    report=json.loads((ROOT/'docs/research/gx8002-mic-frame-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256'] and section['address']==0x10206f08
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');mic=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    wrapper=out/'padmux-get-stock.elf';analysis=Elf32(wrapper.read_bytes(),'stock');assert analysis.contents(next(s for s in analysis.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x183f0','--stop-address=0x184e8',str(wrapper)],text=True));new=decode((out/'tws-audio.disassembly.txt').read_text());cases=0;calls=0
    def setup(name,memory):
        if name=='LvpGetContext':
            for off,value in ((28,10),(32,16000),(36,2),(40,6),(60,3),(80,0x20030410)):word(memory,HEADER+off,value)
    def nested(memory,channel,frame):
        nonlocal calls
        result,reads=mic_execute(mic,section['address'],memory,channel,frame,91)
        assert frame==0
        expected=0x20030410+(channel*6+(word(memory,CTX+8)%3)*2)*320
        assert result==expected
        assert sorted(reads)==sorted([CTX,CTX+8,*[HEADER+i for i in (28,32,36,40,60,80)]])
        calls+=1;return result
    for args in itertools.product((-1,0,1,13,14,15,0x7fffffff),(0,1,2),(0,1),(0,1),(0,1),(2,4),(1,50),(91,)):
        actual=execute(new,0x100263dc,evidence['bindings'],*args,hook=setup,mic_hook=nested)
        assert actual==execute(old,0x183f0,evidence['bindings'],*args,hook=setup,mic_hook=nested)
        assert actual==execute(new,0x100263dc,evidence['bindings'],*args,hook=setup)
        cases+=1
    assert calls==1152
    return {'candidate':evidence,'mic_elf_sha256':sha(path.read_bytes()),'cases':cases,'decoded_helper_calls':calls,'source_admitted':False,'limits':['Actual decoded source microphone helper reads callback context/header and checks independent pointer/read-set oracle. Returned microphone pointer intentionally unused by stock callback. Other helpers modeled; physical timing/concurrency not qualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-audio-mic.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_helper_calls'])
