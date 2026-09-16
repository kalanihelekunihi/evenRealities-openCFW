# SPDX-License-Identifier: MIT
"""Decode final clear/header/diagnostic effects with symbolic float conversion."""
import json,re,subprocess
from build_gx8002_backup_imcra_state import ROOT
from verify_gx8002_memcpy_source import decode

def run(code,source,frames,size,workspace):
    r={f'r{i}':0 for i in range(32)};r.update(r4=0x20010000,r5=size,r6=size,r2=frames);f={};trace=[];pc=0x1000e5fc if source else 0x46fb2
    for _ in range(150):
        if pc==(0x1000e39c if source else 0x47040):return trace
        op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
        if op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='ld.w':assert args=='r0, (r4, 0x24)';r['r0']=0x200100c4
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,base,off=m.groups();trace.append(('write',r[base]+int(off,0),r[reg]))
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fsitos':f[p[0]]=(op,f[p[1]])
        elif op=='fmuls':f[p[0]]=(op,f[p[1]],f[p[2]])
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0)+(0 if source else 0x10000000-0x38940);result=0;pair=None
            if target==0x100113c4:trace.append(('memset',r['r0'],r['r1'],r['r2']))
            elif target==0x1000e314:
                trace.append(('workspace',r['r0'],r['r1']));result=workspace[r['r1']]
            elif target==0x10011af4:
                trace.append(('extend',f['fr0']));pair=(('low_double',f['fr0']),('high_double',f['fr0']))
            elif target==0x10009934:trace.append(('printf',r['r0'],r['r1'],r['r2']))
            else:raise AssertionError(hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            for i in range(8):f[f'fr{i}']=0xdead1000+i
            r['r0']=result
            if pair:r['r0'],r['r1']=pair
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x46fb2','--stop-address=0x47040',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text());cases=0
    for frames in (0,1,512,0x80000000,0xffffffff):
        for size in (42320,43008,0x7fffffff):
            for workspace in ((0,42124,42124),(1,0x7fffffff,0x80000000)):
                a=run(old,False,frames,size,workspace);b=run(new,True,frames,size,workspace);assert a==b,(a,b)
                assert a[:3]==[('memset',0x200100c4,0,(frames*2)&0xffffffff),('write',0x20010000,0x20010000),('write',0x20010004,size)]
                assert [x[1] for x in a if x[0]=='printf']==[0x10014378,0x1001439c,0x100143c0];cases+=1
    report={'cases':cases,'source_admitted':False,'limits':['Final block only. Memset/workspace/conversion/printf modeled with caller clobbers; checks argument expressions and ordered effects, not helper internals or huge clear validity. Epilogue and whole-function composition remain pending.']}
    (ROOT/'docs/research/gx8002-imcra-finish.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify())
