# SPDX-License-Identifier: MIT
"""Decoded wrapper call order and ABI with poisoned helper return registers."""
import json,subprocess
from build_gx8002_backup_audio_suspend_resume import build,ROOT,ROWS,Elf32,sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode

def execute(code,entry,target,seed):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};initial=r.copy();saved=None;trace=[]
    for _ in range(30):
        op,args,width=code[entry];p=[v.strip() for v in args.split(',')]
        if op=='push':assert args=='r15' and saved is None;saved=r['r15'];r['r14']-=4
        elif op=='pop':
            assert args=='r15';r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&0xffffffff
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='ixw':r[p[0]]=(r[p[1]]+4*r[p[2]])&0xffffffff
        elif op=='bsr':
            assert int(args,0)==target;trace.append((r['r0'],r['r1']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xdead0000)+i
        else:raise AssertionError((op,args))
        entry+=width
    raise AssertionError('bound')
def verify():
    evidence=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x43054','--stop-address=0x43084',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-audio-suspend-resume/wrappers.disassembly.txt').read_text());cases=0
    for name,offset,size in ROWS:
        for seed in (0,1,0x12345678,0x80000000,0xffffffff):
            wanted=[(0x20007,0),(0x10000,1)] if name=='suspend' else [(0x30007,1)]
            assert execute(old,offset,0x3e5fc,seed)==execute(new,offset-0x38940+0x10000000,0x10005cbc,seed)==wanted;cases+=1
    result={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Ordered calls and saved ABI verified with caller-register clobbers. Helper execution and hardware delivery qualified separately.']}
    (ROOT/'docs/research/gx8002-backup-audio-suspend-resume-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['cases'])
