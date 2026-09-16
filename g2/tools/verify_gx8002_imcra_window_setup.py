# SPDX-License-Identifier: MIT
"""Compare decoded scalar/angle expressions before the window loops."""
import json,re,subprocess
from build_gx8002_backup_imcra_state import ROOT
from verify_gx8002_memcpy_source import decode

def run(code,start,end,source):
    r={'r4':('state',),'r8':('scalar_address',),'r14':('stack',)};f={};writes=[];calls=[];step=None
    fields={12:('length',),0xac:('scalar_address',),0x30:('window_address',),0x34:('normalization_address',)}
    for pc in sorted(p for p in code if start<=p<end):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op in ('lrw','movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fsitos':f[p[0]]=(op,f[p[1]])
        elif op in ('fadds','fdivs'):f[p[0]]=(op,f[p[1]],f[p[2]])
        elif op=='fnmacs':f[p[0]]=(op,f[p[0]],f[p[1]],f[p[2]])
        elif op=='bsr':
            assert int(args,0)==(0x1000ee64 if source else 0x477a4)
            calls.append(f['fr0']);f['fr0']=('cosine',f['fr0'])
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,base,offset=m.groups();assert r[base]==('state',);r[reg]=fields[int(offset,0)]
        elif op=='fsts':
            m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*0x0\)',args);assert m,args
            reg,base=m.groups()
            if r[base]==('stack',):step=f[reg]
            else:writes.append((r[base],f[reg]))
        else:raise AssertionError((hex(pc),op,args))
    if not source:step=f['fr8']
    return {'cosine_arguments':calls,'scalar_writes':writes,'angle_step':step}

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=subprocess.check_output([pre,'-D','--start-address=0x46eb8','--stop-address=0x46efc',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    a=run(decode(raw),0x46eb8,0x46efc,False)
    b=run(decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text()),0x1000e586,0x1000e5d0,True)
    assert a==b,(a,b)
    assert a['angle_step']==('fdivs',0x40c90fdb,('fsitos',('length',)))
    report={'matching_setup':a,'source_admitted':False,'limits':['Stable header/pointer bindings assumed. Compares cosine argument, scalar output expression and angle step only; ignores changed header read timing. Symbolic cosine result; no concrete FPU, concurrent mutation or whole-function proof.']}
    (ROOT/'docs/research/gx8002-imcra-window-setup.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify())
