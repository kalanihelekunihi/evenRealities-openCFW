# SPDX-License-Identifier: MIT
"""Check compiled event ingress arguments, ignored queue result and saved ABI."""
import json
from itertools import product
from build_gx8002_backup_trigger_app_event import build,ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();assert evidence['exact_stock']
    code=decode((ROOT/'build/gx8002-backup-trigger-app-event/trigger.disassembly.txt').read_text());cases=0
    for pointer,result,seed in product((0,0x20020000,0x2002d31c,0xffffffff),(0,1,0xffffffff),(0,0x12345678)):
        r={f'r{i}':seed+i for i in range(32)};r['r0']=pointer;initial=r.copy();pc=0x1000bde8;saved=None;calls=[]
        for _ in range(15):
            op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
            if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
            elif op=='mov':r[p[0]]=r[p[1]]
            elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
            elif op=='bsr':
                assert int(args,0)==0x10015b64;calls.append((r['r0'],r['r1']))
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
                r['r0']=result
            elif op=='pop':
                assert args=='r15';r['r15']=saved;r['r14']+=4
                assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
                assert calls==[(0x2002d784,pointer)] and r['r0']==0;break
            else:raise AssertionError((op,args))
            pc+=width
        else:raise AssertionError('bound')
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Byte-identical stock wrapper, queue arguments and ignored return verified with caller clobbers. Pointer extremes are forwarding-only cases; actual queue dereference is modeled.']}
    (ROOT/'docs/research/gx8002-backup-trigger-app-event-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
