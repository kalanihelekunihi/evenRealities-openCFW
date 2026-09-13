# SPDX-License-Identifier: MIT
"""Check SADC setup call ordering, input normalization and fresh state reads."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_sadc import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,pga,word,state,status,mutate,bindings):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=pga,r14=0x20070000)
    initial=r.copy();pc=entry;saved=None;condition=False;trace=[];memory={0xa0a00000:word,0x20027330:state}
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if saved is not None or args not in ('r4, r15','r4-r5, r15'):raise ValueError('SADC frame')
            frame=args;regs=['r4','r15'] if args=='r4, r15' else ['r4','r5','r15'];saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if saved is None or args!=frame:raise ValueError('SADC restore')
            for name,value in zip(regs,saved):r[name]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('SADC ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','lrw','movih'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op in ('or','ori'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);r[p[0]]=a|b
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op=='bez':
            if not r[p[0]]:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('SADC memory operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&0xffffffff
            if address not in memory:raise ValueError('SADC memory address')
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xd3a4 else 0))&0xffffffff
            if target not in bindings:raise ValueError('SADC helper target')
            name=bindings[target];trace.append((name,r['r0'],r['r1']) if name=='gate' else (name,r['r0']))
            if mutate:memory[0xa0a00000]^=0x40000000;memory[0x20027330]^=0x10000000
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=status
        else:raise ValueError('SADC instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('SADC bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('SADC stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd3a4','--stop-address=0xd408',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-input-sadc/sadc.disassembly.txt').read_text())
    bindings={address:('gate' if name=='open_cfw_gx8002_platform_gate' else name.removeprefix('gx_analog_set_')) for name,address in candidate['bindings'].items() if name!='open_cfw_gx8002_audio_input_state'}
    cases=0
    for pga,word,state,status,mutate in product((0,1,2,63,64,255,0x80000000,0xffffffff),(0,64,0xffffffff),(0,1,0xffffffff),(0,7,0xffffffff),(False,True)):
        w=word^(0x40000000 if mutate else 0);s=state^(0x10000000 if mutate else 0)
        trace=[('gate',7,1),('adc_rstn',0),('pga_bypass',int(not pga)),('pga_enable',pga),('adc_sample_clk_sel',1),('adc_out_at_clk',0),('adc_in_sel',int(not pga)),('pga_itrim',0),('adc_rstn',1),('read',0xa0a00000,w),('write',0xa0a00000,w|64),('read',0x20027330,s),('write',0x20027330,s|1)]
        wanted=(0,trace,{0xa0a00000:w|64,0x20027330:s|1})
        if execute(old,0xd3a4,pga,word,state,status,mutate,bindings)!=wanted or execute(new,0x10203e18,pga,word,state,status,mutate,bindings)!=wanted:raise ValueError('SADC independent ordering oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Helper calls modeled with clobbers and optional peripheral/global-state mutation. PGA input is preserved; only bypass/input-select are normalized. No physical analog behavior or concurrency qualification.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-input-sadc-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('SADC cases:',r['decoded_cases'])
