# SPDX-License-Identifier: MIT
"""Qualify the query's 1/1/0 weights for every unspecified ABI padding byte."""
import json,subprocess
from verify_gx8002_audio_fftvad_w import verify,execute,ROOT,decode


def check():
    evidence=verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdb80','--stop-address=0xdbbc',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-audio-fftvad-w/gain.disassembly.txt').read_text());cases=0
    for padding in range(256):
        for seed in (0,0xffffffff,0xa5a5a5a5,0x80000000):
            word=seed;trace=[]
            for low,value in ((8,1),(12,1),(16,0)):
                trace.append(('read',0xa0a00158,word));word=(word&~(15<<low))|(value<<low);trace.append(('write',0xa0a00158,word))
            for code,entry in ((old,0xdb80),(new,0x102045f4)):
                if execute(code,entry,(padding<<24)|0x101,seed)!=(0,trace,word):raise ValueError('Padding affected weight setter')
            cases+=1
    return {'consumer_evidence':evidence,'cases':cases,'limits':['Specific decoded stock/source weight setter ignores high ABI byte for query weights1/1/0. Does not prove all possible consumers or query control flow.']}


if __name__=='__main__':
    report=check();(ROOT/'docs/research/gx8002-vad-query-weight-padding.json').write_text(json.dumps(report,indent=2)+'\n');print(report['cases'])
