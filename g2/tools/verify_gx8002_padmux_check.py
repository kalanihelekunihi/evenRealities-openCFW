#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded padmux-check contract with hostile caller-register clobbers."""
import hashlib,json,shutil,subprocess
from verify_gx8002_logging import check_paths
from itertools import product
from build_gx8002_padmux_check_candidate import ROOT,build
from verify_gx8002_padmux_get import programs as getter_programs
from build_gx8002_padmux_get_candidate import build as build_getter
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0x102065b8


def expected(pin,function,result):
    if pin&0x80000000 or function&0x80000000: return [],MASK
    return [('get',pin)],0 if (result&255)==function else MASK


def execute(code,entry,pin,function,result,getter_hook=None):
    r={f'r{i}':(0x97235618+i*0x1020304)&MASK for i in range(32)}
    r.update(r0=pin,r1=function,r14=0x2002f7fc)
    initial=r.copy();saved=None;condition=False;trace=[];pc=entry
    def finish():
        if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
            raise ValueError('Padmux check ABI')
        return trace,r['r0']
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4, r15' or saved is not None: raise ValueError('Check frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None: raise ValueError('Check restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            return finish()
        elif op=='rts': return finish()
        elif op=='or': r[p[0]]=r[p[1]]|r[p[2]]
        elif op=='blz':
            if r[p[0]]&0x80000000: nxt=int(p[1],0)
        elif op=='br': nxt=int(args,0)
        elif op=='mov': r[p[0]]=r[p[1]]
        elif op=='movi': r[p[0]]=int(p[1],0)
        elif op=='subi': r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='subu': r[p[0]]=(r[p[0]]-r[p[1]])&MASK
        elif op=='zextb': r[p[0]]=r[p[1]]&255
        elif op=='cmpne': condition=r[p[0]]!=r[p[1]]
        elif op=='mvc': r[p[0]]=int(condition)
        elif op=='bsr':
            if int(args,0)!=(0xfb18 if entry==0xfb44 else 0x1020658c): raise ValueError('Check getter target')
            trace.append(('get',r['r0']))
            if getter_hook is not None: result=getter_hook(r['r0'])
            for i in (0,1,2,3,12,13,15,*range(18,32)): r[f'r{i}']=(0xa5721368+i*0x113)&MASK
            r['r0']=result
        else: raise ValueError('Unhandled check instruction '+op)
        pc=nxt
    raise ValueError('Check execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate=build();build_getter();getter_programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    stock=decode(subprocess.check_output([pre,'-D','--start-address=0xfb44','--stop-address=0xfb68',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    source=decode((ROOT/'build/gx8002-board/padmux-check-candidate.disassembly.txt').read_text())
    count=0
    for pin,function,result in product((0,32,33,0x7fffffff,0x80000000,MASK),(*range(257),0x80000000,MASK),(0,1,15,255,256,MASK)):
        want=expected(pin,function,result)
        if execute(stock,0xfb44,pin,function,result)!=want or execute(source,ADDRESS,pin,function,result)!=want:
            raise ValueError('Padmux check mismatch')
        count+=1
    from verify_gx8002_padmux_check_composition import verify as compose
    composition=compose()
    if composition['candidate']!=candidate or not candidate['fits']:
        raise ValueError('Padmux checker candidate changed or exceeds slot')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfb44,'bytes':36,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    names=('verify_gx8002_padmux_check.py','verify_gx8002_padmux_check_composition.py',
           'build_gx8002_padmux_check_candidate.py','verify_gx8002_padmux_get.py',
           'build_gx8002_padmux_get_candidate.py')
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest() for name in names}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/padmux-check-candidate.elf',output/'padmux-check.elf')
    return {'functions':[row],'candidate':candidate,'decoded_cases':count,'composition':composition,
            'evidence_sha256':hashes,'source_admitted':True,'hardware_qualified':False,
            'limits':['Finite argument/result cases and decoded getter call-boundary composition with caller clobbers. No physical pad effects or concurrency proof.']}


if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-padmux-check-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded check cases:',report['decoded_cases'])
