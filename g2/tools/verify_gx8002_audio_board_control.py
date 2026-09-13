# SPDX-License-Identifier: MIT
import json,random,subprocess
from build_gx8002_audio_board_control import build,ROOT
from execute_gx8002_audio_board_control import execute
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha

def verify():
    r=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(path.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xc590','--stop-address=0xc5dc',str(path)],text=True));new=decode((ROOT/'build/gx8002-audio-board-control/candidate.disassembly.txt').read_text())
    memory={0x1020a8aa+i:6*(i+1) for i in range(9)};rng=random.Random(523);gains=list(range(256))+[rng.getrandbits(32) for _ in range(1000)]
    assert bytes(memory[0x1020a8aa+i] for i in range(9))==e.contents(next(s for s in e.sections if s['name']=='.data'))[0x13e36:0x13e3f]
    for code,base in ((old,0xc590),(new,0x10203004)):
        def reject(*args):raise AssertionError('Unexpected helper')
        ret,after,events=execute(code,base,[],memory,reject);assert ret[1]==0x200269a4 and after==memory and not events
        for gain in gains:
            ret,after,events=execute(code,base+8,[gain],memory,reject);assert ret[1]==(gain*6 if gain<=9 else 0) and after==memory and not events
    configs=[i<<6 for i in range(16)]+[rng.randrange(65536) for _ in range(256)]
    for config in configs:
        for code,base in ((old,0xc590),(new,0x10203004)):
            seen=[];m={**memory,0x200269c4:0,0x200269c5:0}
            def helper(t,a,state,events):
                if t==0x1020300c:
                    ret,after,ev=execute(code,base+8,a,state,lambda *args:None);assert after==state and not ev;return ret[1]
                assert t==0x10206c24;seen.append(tuple(a[:2]))
                if len(seen)==1:
                    # First printf may change state; initialization must read afterward.
                    state[0x200269c4]=config&255;state[0x200269c5]=config>>8
                return 0xfedcba98
            ret,after,events=execute(code,base+32,[],m,helper)
            gain=(config>>6)&15
            assert seen==[(0x1020a8b3,2),(0x1020a8d3,gain*6 if gain<=9 else 0)]
            assert after=={**m,0x200269c4:config&255,0x200269c5:config>>8}
    r.update(gain_cases=len(gains),initialization_cases=len(configs),limits=['Decoded board state pointer, gain conversion, init call ordering and integer ABI; printf internals and physical timing remain separate.'])
    return r
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-board-control-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['gain_cases'],r['initialization_cases'])
