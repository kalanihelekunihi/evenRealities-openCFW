# SPDX-License-Identifier: MIT
"""Flash probe timeout, argument and state transition differential qualification."""
import json,subprocess
from itertools import product
from build_gx8002_flash_probe_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_flash_probe import execute

def oracle(args,states,times,results,pointers=None):
    trace=[('time',times[0])];start=times[0];ti=1;ri=0
    for state in states:
        trace.append(('state',state))
        if state<2:
            trace.extend([('callback_pointer',pointers[ri] if pointers is not None else 0x10212340),('probe',*args)]);value=results[ri];ri+=1
            if value:trace.append(('write_state',1));return value,trace
        now=times[ti];ti+=1;trace.append(('time',now))
        if (now-start)&((1<<64)-1)>=5000000:return 0,trace
    raise AssertionError('Incomplete scenario')

def verify():
    candidate=build();assert candidate['fits'] and sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x16770','--stop-address=0x167cc',str(path)],text=True));new=decode((ROOT/'build/gx8002-board/flash-probe-candidate.disassembly.txt').read_text());cases=0
    for start,states,success,args in product((0,0xffffffff,(1<<64)-3),((0,0,0),(1,1,1),(2,2,2),(255,0,1),(0,2,1)),(0,1,2,3),((0,0,8000000,0),(0xffffffff,2,0x80000000,3))):
        times=[(start+x)&((1<<64)-1) for x in (0,4999998,4999999,5000000)];results=[0 if i!=success else 0x20012340 for i in range(3)]
        want=oracle(args,states,times,results)
        assert execute(old,0x16770,args,states,times,results)==execute(new,0x1002475c,args,states,times,results)==want
        cases+=1
    changing=0
    for state,start,elapsed in product(range(256),(0,0xffffffff,(1<<64)-3),(5000000,1<<32,(1<<64)-1)):
        args=(1,2,8000000,3);states=(state,0,1);times=[start,(start+1)&((1<<64)-1),(start+2)&((1<<64)-1),(start+elapsed)&((1<<64)-1)]
        pointers=(0x1002443c,0x10212340,0x10212344);results=(0,0,0)
        want=oracle(args,states,times,results,pointers)
        assert execute(old,0x16770,args,states,times,results,pointers)==execute(new,0x1002475c,args,states,times,results,pointers)==want
        changing+=1
    return {'changing_pointer_cases':changing,'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Callback and timer scripted; decoded wrapper state/argument/timeout behavior and ABI checked. Callback target ownership and timer integration pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-probe-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
