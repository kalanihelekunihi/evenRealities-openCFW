#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded setter MMIO and call contract; hardware behavior remains unproved."""
import hashlib,json,re,shutil,subprocess
from verify_gx8002_logging import check_paths
from itertools import product
from build_gx8002_padmux_set_candidate import ROOT,build
from verify_gx8002_padmux_get import programs,build as build_getter
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0x102065dc


def expected(pin,function,word,result):
    if pin>32: return [],MASK
    address=0xa0010090+4*(pin//8);shift=4*(pin%8)
    value=(word&~(15<<shift))|((function&15)<<shift)
    return [('read',address,word),('write',address,value),('check',pin,function)],0 if result==0 else MASK


def execute(code,entry,pin,function,word,result,check_hook=None):
    r={f'r{i}':(0x91234567+i*0x1020304)&MASK for i in range(32)}
    r.update(r0=pin,r1=function,r14=0x2002f7fc)
    initial=r.copy();saved=None;condition=False;trace=[];pc=entry
    address=0xa0010090+4*(pin//8)
    def finish():
        if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
            raise ValueError('Setter ABI')
        return trace,r['r0']
    for _ in range(60):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r15' or saved is not None: raise ValueError('Setter frame')
            saved=r['r15'];r['r14']-=4
        elif op=='pop':
            if args!='r15' or saved is None: raise ValueError('Setter restore')
            r['r15']=saved;r['r14']+=4
            return finish()
        elif op=='rts': return finish()
        elif op in ('movi','lrw'): r[p[0]]=int(p[1],0)
        elif op=='cmphsi': condition=r[p[0]]>=int(p[1],0)
        elif op=='cmpnei': condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','br'):
            if op=='br' or condition: nxt=int(args,0)
        elif op in ('lsli','lsri','asri','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0)
            if op=='asri' and a&0x80000000: a-=1<<32
            r[p[0]]=(a<<n if op=='lsli' else a-n if op=='subi' else a>>n)&MASK
        elif op=='andi': r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('addu','and','or','lsl','subu','nor','andn'):
            a,b=(r[p[1]],r[p[2]]) if len(p)==3 else (r[p[0]],r[p[1]])
            if op=='lsl' and b>=32: raise ValueError('Setter shift')
            r[p[0]]=(a+b if op=='addu' else a&b if op=='and' else a|b if op=='or' else a<<b if op=='lsl' else a-b if op=='subu' else ~(a|b) if op=='nor' else a&~b)&MASK
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m: raise ValueError('Setter memory operand')
            reg,base,offset=m.groups();actual=(r[base]+int(offset,0))&MASK
            if pin>32 or actual!=address: raise ValueError('Setter MMIO address')
            if op=='ld.w': trace.append(('read',actual,word));r[reg]=word
            else: word=r[reg];trace.append(('write',actual,word))
        elif op=='mvc': r[p[0]]=int(condition)
        elif op=='bsr':
            if int(args,0)!=(0xfb44 if entry==0xfb68 else 0x102065b8): raise ValueError('Setter checker target')
            trace.append(('check',r['r0'],r['r1']))
            if check_hook is not None: result=check_hook(r['r0'],r['r1'],word)
            for i in (0,1,2,3,12,13,15,*range(18,32)): r[f'r{i}']=(0xa5721368+i*0x113)&MASK
            r['r0']=result
        else: raise ValueError('Unhandled setter instruction '+op)
        pc=nxt
    raise ValueError('Setter execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate=build();build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfb68','--stop-address=0xfbbc',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-board/padmux-set-candidate.disassembly.txt').read_text())
    count=0
    for pin,function,word,result in product((*range(34),0x7fffffff,0x80000000,MASK),(*range(17),255,256,0x80000000,MASK),(0,MASK,0x12345678,0x87654321),(0,1,0x80000000,MASK)):
        want=expected(pin,function,word,result)
        if execute(old,0xfb68,pin,function,word,result)!=want or execute(new,ADDRESS,pin,function,word,result)!=want:
            raise ValueError('Setter decoded contract mismatch')
        count+=1
    from verify_gx8002_padmux_set_composition import verify as compose
    composition=compose()
    if composition['candidate']!=candidate or not candidate['fits']:
        raise ValueError('Setter candidate changed or exceeds slot')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfb68,'bytes':84,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=('verify_gx8002_padmux_set.py','verify_gx8002_padmux_set_composition.py',
           'verify_gx8002_padmux_check.py','verify_gx8002_padmux_get.py',
           'build_gx8002_padmux_set_candidate.py','build_gx8002_padmux_check_candidate.py',
           'build_gx8002_padmux_get_candidate.py')
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in names}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/padmux-set-candidate.elf',output/'padmux-set.elf')
    return {'functions':[row],'candidate':candidate,'decoded_cases':count,'composition':composition,
            'evidence_sha256':hashes,'source_admitted':True,'hardware_qualified':False,
            'limits':['Finite setter contract and decoded checker/getter call-boundary composition. Helpers use separate checked stacks. No hardware effects, shared nested-stack or concurrency proof.']}


if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-padmux-set-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded setter cases:',report['decoded_cases'])
