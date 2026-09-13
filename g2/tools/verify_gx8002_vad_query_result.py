# SPDX-License-Identifier: MIT
"""Check all hardware state indices through decoded query return paths."""
import json,subprocess
from verify_gx8002_vad_query_transitions import verify,execute,ROOT,decode


def check():
    transitions=verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x10990','--stop-address=0x10b54',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-audio-input-query-vad/index.disassembly.txt').read_text());cases=0
    for index in range(65536):
        bit=(index+94)%95;word=bit//32;mask=1<<(bit%32)
        for selected in (0,1):
            words=[0xffffffff,0xffffffff,0xffffffff];words[word]=mask if selected else 0xffffffff^mask
            for code,entry in ((old,0x10990),(new,0x10207404)):
                if execute(code,entry,0,4,0xa5,(*words,index))!=selected:raise ValueError(('VAD result',index,selected))
            cases+=1
    for index in (0,1,31,32,63,64,94,95,65535):
        for code,entry in ((old,0x10990),(new,0x10207404)):
            if execute(code,entry,0xffffffff,1,0,(0,0,0,index))!=1:raise ValueError('Forced VAD')
        cases+=1
    return {'transitions':transitions,'result_cases':cases,'source_admitted':False,'limits':['All16-bit state indices and selected-bit values checked through saved ABI restoration. Stable modeled hardware state; changing-level full paths and helper mutation pending.']}


if __name__=='__main__':
    report=check();(ROOT/'docs/research/gx8002-vad-query-result.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result_cases'])
