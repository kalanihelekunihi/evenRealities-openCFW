# SPDX-License-Identifier: MIT
"""Compare unpacked unsigned-to-double values at the pack helper boundary."""
import json,re,subprocess,struct
from execute_gx8002_double_pack_integer import execute as pack_execute
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,value,pack,full=False,seed=0):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=value,r14=0x2002f000)
    initial=r.copy();saved=None
    memory={};pc=entry;condition=False
    for _ in range(60):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];following=pc+width
        if op=='push':
            if p not in (['r15'],['r4','r15']):raise ValueError('Conversion save registers')
            saved={reg:r[reg] for reg in p};r['r14']-=4*len(p)
        elif op=='pop':
            if saved is None or p!=list(saved):raise ValueError('Conversion restore registers')
            r.update(saved);r['r14']+=4*len(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Conversion ABI')
            return r['r0']|(r['r1']<<32)
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ff1':r[p[0]]=32-r[p[1]].bit_length()
        elif op=='btsti':condition=bool(r[p[0]]&(1<<int(p[1],0)))
        elif op=='incf':
            if not condition:r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op in ('addi','subi','subu','lsl','lsr','lsri'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op in ('subi','subu') else 0 if b>=32 else a<<b if op=='lsl' else a>>b)&0xffffffff
        elif op=='bez':
            if not r[p[0]]:following=int(p[1],0)
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=r[base]+int(off,0)
            if not initial['r14']-28<=address<initial['r14']:raise ValueError('Conversion stack bounds')
            memory[address]=r[reg]
        elif op=='bsr':
            if int(args,0)!=pack or r['r0']!=r['r14']:raise ValueError('Conversion pack boundary')
            fields={offset:memory[r['r14']+offset] for offset in (0,4,8,12,16) if r['r14']+offset in memory}
            if not full:return fields
            result=pack_execute(code,pack,fields,seed)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result&0xffffffff;r['r1']=result>>32
        else:raise ValueError('Conversion opcode '+op)
        pc=following
    raise ValueError('Conversion bound')

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),str(p))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x13a5c','--stop-address=0x13d00',str(p)],text=True))
    linked=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(linked.read_bytes(),str(linked));symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    new=decode((linked.parent/'runtime.disassembly.txt').read_text())
    values=set(range(4096))|{0xffffffff}|{i<<20 for i in range(4096)}
    values|={(1<<bit)+delta for bit in range(32) for delta in (-1,0,1) if 0<=(1<<bit)+delta<=0xffffffff}
    for value in sorted(values):
        a=execute(old,0x13a5c,value,0x13b00);b=execute(new,symbols['__floatunsidf'],value,symbols['__pack_d'])
        if a!=b:raise ValueError(('Conversion preparation mismatch',value,a,b))
        if value==0:wanted={0:2,4:0}
        else:
            exponent=value.bit_length()-1;fraction=value<<(60-exponent)
            wanted={0:3,4:0,8:exponent,12:fraction&0xffffffff,16:fraction>>32}
        if a!=wanted:raise ValueError(('Conversion independent fraction',value,a,wanted))
        bits=struct.unpack('<Q',struct.pack('<d',float(value)))[0]
        for seed in (0,0xffffffff):
            if execute(old,0x13a5c,value,0x13b00,True,seed)!=bits or execute(new,symbols['__floatunsidf'],value,symbols['__pack_d'],True,seed)!=bits:raise ValueError(('Full integer conversion',value,seed))
            if pack_execute(old,0x13b00,a,seed)!=bits or pack_execute(new,symbols['__pack_d'],b,seed)!=bits:raise ValueError(('Integer IEEE packing',value,seed))
    return {'candidate':candidate,'cases':len(values),'full_function_executions':4*len(values),'source_admitted':False,'limits':['Unpacked conversion output is passed to decoded stock/source pack helpers; final IEEE bits checked against exact host uint32 conversion. Zero unused fields varied with two seeds. Full conversion frame returns checked with decoded pack in a separate frame; only unsigned integer domain qualified. Out-of-range shift intermediates modeled zero before conditional replacement. No full float-runtime equivalence claim.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uint-double-prepare.json').write_text(json.dumps(result,indent=2)+'\n');print('Conversion preparation cases:',result['cases'])
