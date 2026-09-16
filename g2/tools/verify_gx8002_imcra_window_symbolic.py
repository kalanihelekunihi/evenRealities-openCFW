# SPDX-License-Identifier: MIT
"""Compare decoded window iteration, including cosine argument and Q15 store."""
import json,re,subprocess
from build_gx8002_backup_imcra_state import ROOT
from verify_gx8002_memcpy_source import decode

def run(code,start,stop,source,length=None):
    r={'r8' if source else 'r5':('index',),'r6' if source else 'r7':('window',),'r14':('stack',)}
    f={'fr8':('angle_step',),'fr10':0x3f0a3d71,'fr11':0x3eeb851f,'fr9':0x46fffe00};mem={};calls=[];stores=[]
    if length is not None:r.update({'r8' if source else 'r5':0,'r9':length})
    pc=start;condition=False
    for _ in range(30000):
        if pc==stop:break
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='ld.w':assert source;r[p[0]]=('angle_step',)
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op in ('fsitos','fstosi.rz'):f[p[0]]=(op,f[p[1]])
        elif op=='fmuls':f[p[0]]=(op,f[p[1]],f[p[2]])
        elif op=='fnmacs':f[p[0]]=(op,f[p[0]],f[p[1]],f[p[2]])
        elif op=='bsr':
            assert int(args,0)==(0x1000ee64 if source else 0x477a4)
            calls.append(f['fr0']);f['fr0']=('cosine',f['fr0'])
        elif op=='fsts':mem['temporary']=f[p[0]]
        elif op=='ld.h':r[p[0]]=mem['temporary']
        elif op=='str.h':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(r\d+) << 1\)',args);assert m,args
            reg,base,index=m.groups();stores.append((r[base],r[index],('low16',r[reg])))
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmplt':condition=r[p[0]]<r[p[1]]
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='addi':r[p[0]]=r[p[0] if len(p)==2 else p[1]]+int(p[-1],0)
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    else:raise AssertionError('iteration bound')
    return {'cosine_arguments':calls,'stores':stores}

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=subprocess.check_output([pre,'-D','--start-address=0x46f14','--stop-address=0x46f46',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    stock=run(decode(raw),0x46f14,0x46f40,False)
    code=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text());source=run(code,0x1000e6d6,0x1000e712,True)
    assert stock==source,(stock,source)
    loops=[]
    for length in (1,2,255,256,511,512,513):
        a=run(decode(raw),0x46f14,0x46f46,False,length)
        b=run(code,0x1000e5d4,0x1000e5d8,True,length)
        assert a==b and len(a['stores'])==length
        assert [row[1] for row in a['stores']]==list(range(length))
        loops.append({'length':length,'matching_stores':len(a['stores'])})
    report={'matching_iteration':stock,'loops':loops,'source_admitted':False,'limits':['Symbolic integer index and angle-step inputs; compares cosine input, arithmetic operation order, truncating conversion and low-halfword store. Positive loop lengths compared with modeled cosine result. Initial setup, zero/negative lengths and helper execution are not qualified here.']}
    (ROOT/'docs/research/gx8002-imcra-window-symbolic.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify())
