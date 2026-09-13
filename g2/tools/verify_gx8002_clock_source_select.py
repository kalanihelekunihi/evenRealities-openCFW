# SPDX-License-Identifier: MIT
import json,random,subprocess
from build_gx8002_clock_source_select_candidate import build,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA
from execute_gx8002_clock_source_select import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x16a44','--stop-address=0x16bf4',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-source-select-candidate.disassembly.txt').read_text());rng=random.Random(129);reg=0xa001008c;param=0x20031000
    for i in range(512):
        shift=i%32;value=rng.getrandbits(32);mask=rng.getrandbits(32);initial=rng.getrandbits(32);m={};word(m,reg,initial)
        expected=((initial&~((mask<<shift)&0xffffffff))|(value<<shift))&0xffffffff
        for code,entry in ((old,0x16a44),(new,0x10024a30)):
            ret,after,events=execute(code,entry,[reg,shift,value,mask],m,lambda *x:None)
            assert ret[0]=='return' and word(after,reg)==expected and set(after)==set(m)
    for shift in range(32):
        for clk in range(256):
            initial=rng.getrandbits(32);m={param+4:clk};word(m,param,shift);word(m,reg,initial)
            for code,entry,helper_entry in ((old,0x16be0,0x16a44),(new,0x10024bcc,0x10024a30)):
                calls=[]
                def helper(t,a,state,events):
                    assert t==0x10024a30 and a==[reg,shift,clk,1];calls.append(tuple(a))
                    ret,after,ev=execute(code,helper_entry,a,state,lambda *x:None);state.clear();state.update(after);return 0
                ret,after,events=execute(code,entry,[param],m,helper)
                expected=(initial&~(1<<shift))|((clk<<shift)&0xffffffff)
                assert ret[0]=='return' and len(calls)==1 and word(after,reg)==expected
                assert all(after[k]==v for k,v in m.items() if not reg<=k<reg+4)
    return {'candidate':candidate,'register_cases':512,'nested_selector_cases':8192,'limits':['Bit-offset ABI 0..31; all byte-valued selector inputs, arbitrary register bits and helper mask/value inputs. Physical clock transitions/timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-source-select-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['nested_selector_cases'])
