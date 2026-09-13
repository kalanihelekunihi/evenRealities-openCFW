# SPDX-License-Identifier: MIT
"""Run decoded audio read-index update inside actual record callback calls."""
import json,subprocess,itertools
from verify_gx8002_audio_record import verify as qualify,execute,ROOT,Elf32,sha,decode,word,CTRL
from verify_gx8002_audio_input_state import execute as update

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-source-candidate/audio-input-state/state.elf'
    elf=Elf32(path.read_bytes(),'state');report=json.loads((ROOT/'docs/research/gx8002-audio-input-state-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');state=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    out=ROOT/'build/gx8002-board';old=decode(subprocess.check_output([pre,'-D','--start-address=0x18228','--stop-address=0x18328',str(out/'padmux-get-stock.elf')],text=True));new=decode((out/'audio-record.disassembly.txt').read_text());cases=0;calls=0
    for offset,index,flags,vad,seed in itertools.product((0,1,2,0xffffffff),(0,3,12),(0,16),(0,1),(0,91)):
        results=[]
        for code,entry in ((old,0x18228),(new,0x10026214)):
            seen=[]
            def callback(memory,frame,private):
                words={a:word(memory,a) for a in range(CTRL,CTRL+20,4)};before=words.copy();next_index=(words[CTRL]+offset)&0xffffffff;accepted=next_index<=words[CTRL+4]
                result,events=update(state,0x102073a0,words,offset)
                expected=before.copy()
                if accepted:expected[CTRL]=next_index
                assert words==expected and result==(0 if accepted else 0xffffffff)
                for event in events:
                    if event[0]=='write':word(memory,event[1],event[2])
                seen.append((result,events));return result
            result=execute(code,entry,evidence['candidate']['bindings'],4,14,14,flags,vad,24,index,seed,record_hook=callback)
            results.append((result,seen))
        assert results[0]==results[1];calls+=len(results[1][1]);cases+=1
    assert calls
    return {'evidence':evidence,'cases':cases,'decoded_update_calls':calls,'state_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Decoded read-index update runs inside modeled application callback with shared state writes. Both stock/source callback execution agree. Application callback body, other helpers and physical concurrency remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-record-read-update.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],r['decoded_update_calls'])
