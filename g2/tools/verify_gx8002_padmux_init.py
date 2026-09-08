#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded initializer read/call contract for valid configuration arrays."""
import hashlib,json,re,shutil,subprocess
from verify_gx8002_logging import check_paths
from build_gx8002_padmux_init_candidate import ROOT,build
from verify_gx8002_padmux_get import build as build_getter,programs
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0x10206630
TABLE=0x20030000
DEFAULTS=0x1020acc4


def expected(entries,pointer=TABLE,size=None):
    size=len(entries) if size is None else size
    if not pointer or size&0x80000000: return [],MASK
    trace=[]
    for pin in range(32):
        trace.append(('read',DEFAULTS+pin*2,pin))
        function=0
        for i,(candidate,value) in enumerate(entries[:size]):
            trace.append(('read',pointer+i*2,candidate))
            if candidate==pin:
                trace.append(('read',pointer+i*2+1,value));function=value;break
        else: trace.append(('read',DEFAULTS+pin*2+1,0))
        trace.append(('set',pin,function))
    return trace,0


def execute(code,entry,entries,pointer=TABLE,size=None,result=0,setter_hook=None):
    size=len(entries) if size is None else size
    memory={DEFAULTS+2*i+j:v for i in range(32) for j,v in enumerate((i,0))}
    memory.update({pointer+2*i+j:v for i,pair in enumerate(entries) for j,v in enumerate(pair)})
    r={f'r{i}':(0x91234567+i*0x1020304)&MASK for i in range(32)}
    r.update(r0=pointer,r1=size,r14=0x2002f7fc);initial=r.copy()
    saved=None;condition=False;trace=[];pc=entry
    def finish():
        if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)): raise ValueError('Initializer ABI')
        return trace,r['r0']
    for _ in range(100000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r7, r15' or saved is not None: raise ValueError('Initializer frame')
            saved=[r[f'r{i}'] for i in (4,5,6,7,15)];r['r14']-=20
        elif op=='pop':
            if args!='r4-r7, r15' or saved is None: raise ValueError('Initializer restore')
            for i,v in zip((4,5,6,7,15),saved):r[f'r{i}']=v
            r['r14']+=20;return finish()
        elif op=='rts':return finish()
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addu','addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]]
            b=r[p[-1]] if op=='addu' else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a+b)&MASK
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('bez','blz'):
            if (r[p[0]]==0 if op=='bez' else r[p[0]]&0x80000000):nxt=int(p[1],0)
        elif op=='ld.b':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Initializer load operand')
            reg,base,offset=m.groups();a=(r[base]+int(offset,0))&MASK
            if a not in memory:raise ValueError('Initializer read outside arrays')
            r[reg]=memory[a];trace.append(('read',a,memory[a]))
        elif op=='bsr':
            if int(args,0)!=(0xfb68 if entry==0xfbbc else 0x102065dc):raise ValueError('Initializer setter target')
            trace.append(('set',r['r0'],r['r1']))
            if setter_hook is not None: result=setter_hook(r['r0'],r['r1'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xa5721368+i*0x113)&MASK
            r['r0']=result
        else:raise ValueError('Unhandled initializer instruction '+op)
        pc=nxt
    raise ValueError('Initializer execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate=build();build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfbbc','--stop-address=0xfc0c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-board/padmux-init-candidate.disassembly.txt').read_text())
    tables=[[],[(i,i%16) for i in range(32)],[(i,255-i) for i in reversed(range(32))],[(255,7),(32,3)],[(3,9),(3,2),(0,255)]]
    tables.extend([[(pin,function)] for pin in range(34) for function in (0,1,15,16,255)])
    count=0
    for entries in tables:
        for result in (0,1,MASK):
            want=expected(entries)
            if execute(old,0xfbbc,entries,result=result)!=want or execute(new,ADDRESS,entries,result=result)!=want:raise ValueError('Initializer contract mismatch')
            count+=1
    for pointer,size in ((0,0),(0,1),(TABLE,0xffffffff),(TABLE,0x80000000)):
        want=expected([],pointer,size)
        if execute(old,0xfbbc,[],pointer,size)!=want or execute(new,ADDRESS,[],pointer,size)!=want:raise ValueError('Initializer invalid-input mismatch')
        count+=1
    from verify_gx8002_padmux_init_composition import verify as compose
    from verify_gx8002_padmux_defaults import verify as defaults
    composition=compose();policy=defaults()
    if composition['candidate']!=candidate or not candidate['fits']:
        raise ValueError('Initializer candidate changed or exceeds slot')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfbbc,'bytes':80,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=['verify_gx8002_padmux_init_composition.py','verify_gx8002_padmux_defaults.py']
    names.extend('verify_gx8002_padmux_'+name+'.py' for name in ('init','set','check','get'))
    names.extend('build_gx8002_padmux_'+name+'_candidate.py' for name in ('init','set','check','get'))
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in names}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/padmux-init-candidate.elf',output/'padmux-init.elf')
    return {'functions':[row],'candidate':candidate,'decoded_cases':count,'composition':composition,
            'default_policy':policy,'evidence_sha256':hashes,'source_admitted':True,'hardware_qualified':False,
            'limits':['Valid readable distinct arrays and recovered default policy. Full decoded call-boundary chain with separate checked helper stacks. No nested-stack sharing, concurrent mutation, malformed/wrapped pointers or physical effects proof.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-padmux-init-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded initializer cases:',report['decoded_cases'])
