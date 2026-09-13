# SPDX-License-Identifier: MIT
"""Independent notification setup helper/configuration oracle."""
import json,subprocess
from itertools import product
from build_gx8002_notification_setup import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_notification_setup import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12c88','--stop-address=0x12ce8',str(path)],text=True));new=decode((ROOT/'build/gx8002-notification-setup/candidate.disassembly.txt').read_text());cases=0
    for result,change in product((0,1,0xffffffff),(False,True)):
        config=(0,115200,0x58585542,1);m={0x1020b688+i:0 for i in range(16)}
        for i,v in enumerate(config):word(m,0x1020b688+4*i,v)
        wanted=[('print',0x1020b8bc,2),('value',2,1),('direction',2,1),('print',0x1020b8d7,0),('print',0x1020b460,0x1020b678,464),('done',),('copy',0x1020b688,16),('init',*config),('commands',)]
        def helper(t,a,mem,events,sp):
            if t==0x10206c24:events.append(('print',*(a[:3] if a[0]==0x1020b460 else a[:2])))
            elif t==0x10025738:
                events.append(('copy',a[1],a[2]));mem.update({a[0]+i:mem[a[1]+i] for i in range(a[2])})
            elif t==0x10208458:
                events.append(('init',*[word(mem,a[0]+4*i) for i in range(4)]))
                if change:word(mem,a[0],99)
            else:
                name={0x10205f88:'value',0x10205f24:'direction',0x1020854c:'done',0x10209258:'commands'}[t];events.append((name,*a[:2]) if name in ('value','direction') else (name,))
            return result
        for code,entry in ((old,0x12c88),(new,0x102096fc)):
            ret,actual,events=execute(code,entry,[],m,helper)
            if (ret,actual,events)!=(('return',0),m,wanted):raise ValueError('Setup mismatch')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Helper returns and local config mutation modeled; integer ABI and independent call/configuration oracle checked; nested behavior unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-notification-setup-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
