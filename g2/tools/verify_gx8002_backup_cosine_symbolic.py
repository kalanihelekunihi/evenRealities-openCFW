# SPDX-License-Identifier: MIT
"""Compare ordered floating-operation expression trees on both cosine paths.

No floating algebra reassociation or host rounding is used: each target opcode
is retained in the expression tree. This is not hardware FPU qualification.
"""
import json,re,subprocess
from build_gx8002_backup_cosine import build,ROOT
from verify_gx8002_memcpy_source import decode

def execute(code,pc,nonnegative):
    r={f'r{i}':('initial',i) for i in range(32)};f={f'fr{i}':('initial_float',i) for i in range(32)};f['fr0']=('input',);initial=r.copy();initial_f=f.copy();reads=[];comparison=None
    for _ in range(100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op in ('lrw','movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op in ('fstosi.rz','fstoui.rz','fsitos','fuitos'):f[p[0]]=(op,f[p[1]])
        elif op in ('fmuls','fsubs'):f[p[0]]=(op,f[p[1]],f[p[2]])
        elif op=='fmacs':f[p[0]]=(op,f[p[0]],f[p[1]],f[p[2]])
        elif op=='fcmpzhss':comparison=('ge_zero',f[p[0]])
        elif op=='bt':
            assert comparison is not None
            if nonnegative:nxt=int(args,0)
        elif op=='subi':r[p[0]]=('sub_u32',r[p[0]],int(p[1],0))
        elif op=='addi':r[p[0]]=('add_u32',r[p[0]],int(p[1],0))
        elif op=='andi':r[p[0]]=('and',r[p[1]],int(p[2],0))
        elif op=='fldrs':
            m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(r\d+) << 2\)',args);assert m,args
            dst,base,index=m.groups();assert r[base]==0x100148d4
            address=('table_index',r[index]);reads.append(address);f[dst]=('load_f32',address)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert all(f[f'fr{i}']==initial_f[f'fr{i}'] for i in range(8,16))
            return {'comparison':comparison,'reads':reads,'result':f['fr0']}
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();assert evidence['fits'] and evidence['exact_table'];out=ROOT/'build/gx8002-backup-cosine';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    raw=subprocess.check_output([pre+'objdump','-D','--start-address=0x477a4','--stop-address=0x4781c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    (out/'stock.disassembly.txt').write_text(raw);stock=decode(raw);source=decode((out/'cosine.disassembly.txt').read_text());paths=[]
    for nonnegative in (False,True):
        a=execute(stock,0x477a4,nonnegative);b=execute(source,0x1000ee64,nonnegative);assert a==b,(a,b)
        paths.append({'nonnegative':nonnegative,'tree':a})
    report={'build':evidence,'matching_paths':2,'paths':paths,'source_admitted':False,'limits':['Exact opcode-expression ordering, comparison, table access and saved registers agree on both branch paths. Assumes instruction semantics and valid finite float-to-integer conversion range; does not establish hardware exception, rounding-mode or NaN behavior. No numeric approximation accuracy claim.']}
    (ROOT/'docs/research/gx8002-backup-cosine-symbolic.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['matching_paths'])
