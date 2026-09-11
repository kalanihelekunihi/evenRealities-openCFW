# SPDX-License-Identifier: MIT
"""Decoded unsigned conversion wrapper; compare/subtract/signed fix modeled."""
import json,struct,subprocess,math
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from execute_gx8002_double_fix_tail import execute as signed_fix
from execute_gx8002_double_ge import execute as ge
from execute_gx8002_double_subtract_prepare import execute as subtract

def execute(code,entry,value,helpers,fix_hook=None,compare_hook=None,subtract_hook=None):
    r={f'r{i}':0x70000000+i for i in range(32)};r['r0'],r['r1']=struct.unpack('<II',struct.pack('<d',value))
    initial=r.copy();saved=None;trace=[];pc=entry
    def number(a):return struct.unpack('<d',struct.pack('<II',r[f'r{a}'],r[f'r{a+1}']))[0]
    for _ in range(40):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];following=pc+width
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('Conversion frame')
            saved={x:r[x] for x in ('r4','r5','r15')}
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('Conversion restore')
            r.update(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Conversion ABI')
            return r['r0'],trace
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addu','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addu' else a<<b)&0xffffffff
        elif op=='bhsz':
            if r[p[0]]<0x80000000:following=int(p[1],0)
        elif op=='bsr':
            target=int(args,0);kind=helpers[target];a=number(0);b=number(2) if kind!='fix' else None
            trace.append((kind,a) if b is None else (kind,a,b))
            if kind=='compare':result=((compare_hook(a,b)&0xffffffff) if compare_hook else (0xffffffff if a<b else 0 if a==b else 1),0)
            elif kind=='subtract':result=struct.unpack('<II',struct.pack('<Q',subtract_hook(a,b))) if subtract_hook else struct.unpack('<II',struct.pack('<d',a-b))
            else:
                if not -2147483648<=a<2147483648:raise ValueError('Signed conversion domain')
                result=(fix_hook(a) if fix_hook else int(a)&0xffffffff,0)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0'],r['r1']=result
        else:raise ValueError('Conversion instruction '+op)
        pc=following
    raise ValueError('Conversion bound')

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(path.read_bytes(),str(path))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12ff8','--stop-address=0x13e36',str(path)],text=True))
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';e=Elf32(path.read_bytes(),str(path));symbols={s['name']:s['value'] for s in e.symbols() if s['name']}
    new=decode((path.parent/'runtime.disassembly.txt').read_text());old_helpers={0x139ac:'compare',0x13658:'subtract',0x139ec:'fix'};new_helpers={symbols[n]:k for n,k in (('__gedf2','compare'),('__subdf3','subtract'),('__fixdfsi','fix'))}
    values={i/256 for i in range(4353)}
    for n in (0,1,16,17,2147483647,2147483648,2147483649,4294967295):
        values.update(x for x in (float(n),math.nextafter(float(n),0),math.nextafter(float(n),math.inf)) if 0<=x<4294967296)
    def fix(program,entry,unpack_entry,value):
        bits=struct.unpack('<Q',struct.pack('<d',value))[0]
        return signed_fix(program,entry,{},bits=bits,unpack_entry=unpack_entry)
    for value in values:
        a=execute(old,0x12ff8,value,old_helpers,lambda v:fix(old,0x139ec,0x13c90,v),lambda a,b:ge(old,0x139ac,a,b,0x13c90,0x13d74),lambda a,b:subtract(old,0x13658,a,b,0x13c90,0x13364,0x13b00));b=execute(new,symbols['__fixunsdfsi'],value,new_helpers,lambda v:fix(new,symbols['__fixdfsi'],symbols['__unpack_d'],v),lambda a,b:ge(new,symbols['__gedf2'],a,b,symbols['__unpack_d'],symbols['__fpcmp_parts_d']),lambda a,b:subtract(new,symbols['__subdf3'],a,b,symbols['__unpack_d'],symbols['_fpadd_parts'],symbols['__pack_d']))
        if a!=b or a[0]!=int(value):raise ValueError(('Unsigned fix wrapper',value,a,b))
        expected=[('compare',value,2147483648.0)]
        if value>=2147483648:expected.append(('subtract',value,2147483648.0))
        expected.append(('fix',value if value<2147483648 else value-2147483648))
        if a[1]!=expected:raise ValueError('Conversion helper order')
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Signed conversion and unpack execute in decoded nested frames. Comparison wrapper/unpack/core also execute; subtraction wrapper/core/pack now execute as well. Separate helper frames; no arithmetic result model supplies this tested chain. Wrapper control flow, helper arguments, integer adjustment and sampled valid domain only; no NaN/overflow semantics claim.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-double-uint-wrapper.json').write_text(json.dumps(result,indent=2)+'\n');print('Unsigned fix wrapper cases:',result['cases'])
