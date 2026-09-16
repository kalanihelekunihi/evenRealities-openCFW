# SPDX-License-Identifier: MIT
"""Execute stock and C workspace arithmetic with ordered field reads."""
import json,re,subprocess,random
from build_gx8002_backup_imcra_workspace import build,ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,pc,fields,mode):
    r={f'r{i}':0x70000000+i for i in range(32)};r['r0']=0x20010000;r['r1']=mode;initial=r.copy();reads=[]
    for _ in range(100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='ld.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            dst,base,off=m.groups();addr=r[base]+int(off,0);r[dst]=fields[addr-0x20010000];reads.append((addr,r[dst]))
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addu','subu','mult','lsli','addi'):
            dst=p[0];left=r[p[0]] if len(p)==2 else r[p[1]];right=p[-1];right=int(right,0) if op in ('addi','lsli') else r[right]
            r[dst]={'addu':lambda:left+right,'subu':lambda:left-right,'mult':lambda:left*right,'lsli':lambda:left<<right,'addi':lambda:left+right}[op]()&M
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&M
        elif op=='bez':
            if not r[p[0]]:nxt=int(p[1],0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],reads
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-imcra-workspace';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    raw=subprocess.check_output([pre+'objdump','-D','--start-address=0x46c54','--stop-address=0x46cc2',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    (out/'stock.disassembly.txt').write_text(raw);stock=decode(raw);source=decode((out/'index.disassembly.txt').read_text());rng=random.Random(0x46c54)
    base=[512,256,512,257,8,0];vectors=[base]
    for i in range(6):
        for v in (0,1,2,255,256,257,511,512,0x7fffffff,0x80000000,M):
            f=base.copy();f[i]=v;vectors.append(f)
    vectors += [[rng.getrandbits(32) for _ in range(6)] for _ in range(1000)]
    cases=0
    for values in vectors:
        fields=dict(zip((12,20,16,28,104,116),values));frame,hop,transform,bins,history,extra=values
        for mode in (0,1,2,M):
            a=execute(stock,0x46c54,fields,mode);b=execute(source,0x1000e314,fields,mode);assert a==b,(values,mode,a,b)
            expected=0 if not mode else (bins*72+bins*history*8+frame*10+transform*4+extra*8+4)&M
            assert a==(expected,[(0x20010000+k,v) for k,v in fields.items()]);cases+=1
    report={'build':evidence,'cases':cases,'default_workspace_bytes':execute(stock,0x46c54,dict(zip((12,20,16,28,104,116),base)),2)[0],'source_admitted':False,'limits':['Stable readable state fields required, even for zero mode. No algorithm execution or physical allocation qualification.']}
    (ROOT/'docs/research/gx8002-backup-imcra-workspace-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify())
