#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded padmux getter comparison against a nibble-access contract."""
import json,re,struct,subprocess
import hashlib,shutil
from verify_gx8002_logging import check_paths
from build_gx8002_padmux_get_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0x1020658c


def expected(pin,word):
    if pin>32: return [],MASK
    return [(0xa0010090+4*(pin//8),word)],(word>>(4*(pin%8)))&15


def execute(code,entry,pin,word):
    r={f'r{i}':(0x97123456+i*0x1020304)&MASK for i in range(32)}
    r['r0']=pin;initial=r.copy();trace=[];condition=False;pc=entry
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('movi','lrw'): r[p[0]]=int(p[1],0)
        elif op=='cmphsi': condition=r[p[0]]>=int(p[1],0)
        elif op in ('bt','br'):
            if op=='br' or condition: nxt=int(args,0)
        elif op in ('lsli','lsri','asri','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0)
            if op=='asri' and a&0x80000000: a-=1<<32
            r[p[0]]=(a<<n if op=='lsli' else a-n if op=='subi' else a>>n)&MASK
        elif op=='andi': r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('addu','and','lsl','lsr'):
            a,b=r[p[0]],r[p[1]]
            if op in ('lsl','lsr') and b>=32: raise ValueError('Unqualified shift')
            r[p[0]]=(a+b if op=='addu' else a&b if op=='and' else a<<b if op=='lsl' else a>>b)&MASK
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m: raise ValueError('Padmux load operand')
            reg,base,offset=m.groups();a=(r[base]+int(offset,0))&MASK
            if pin>32 or a!=0xa0010090+4*(pin//8): raise ValueError('Padmux read address')
            trace.append((a,word));r[reg]=word
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
                raise ValueError('Padmux leaf ABI')
            return trace,r['r0']
        else: raise ValueError('Unhandled padmux instruction '+op)
        pc=nxt
    raise ValueError('Padmux execution bound')


def programs():
    out=ROOT/'build/gx8002-board';prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    path=out/'padmux-get-stock.elf'
    subprocess.run([prefix+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(path)],check=True)
    data=bytearray(path.read_bytes());struct.pack_into('<I',data,36,0x21006009);path.write_bytes(data)
    stock=decode(subprocess.check_output([prefix+'objdump','-D','--start-address=0xfb18','--stop-address=0xfb44',str(path)],text=True))
    return stock,decode((out/'padmux-get-candidate.disassembly.txt').read_text())


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    candidate=build();stock,source=programs();count=0
    words=[0,MASK,*[i*0x11111111 for i in range(16)],*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for pin in (*range(34),0x7fffffff,0x80000000,MASK):
        for word in words:
            want=expected(pin,word)
            if execute(stock,0xfb18,pin,word)!=want or execute(source,ADDRESS,pin,word)!=want:
                raise ValueError('Padmux getter mismatch')
            count+=1
    if not candidate['fits']: raise ValueError('Padmux getter exceeds slot')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfb18,'bytes':44,
                              'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest()
            for name in ('verify_gx8002_padmux_get.py','build_gx8002_padmux_get_candidate.py')}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/padmux-get-candidate.elf',output/'padmux-get.elf')
    return {'functions':[row],'candidate':candidate,'decoded_cases':count,'evidence_sha256':hashes,
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Finite word patterns and all valid pin IDs, boundary/negative invalid IDs; exact single-read contract and leaf ABI. No physical pad behavior proved.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-padmux-get-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded padmux cases:',report['decoded_cases'])
