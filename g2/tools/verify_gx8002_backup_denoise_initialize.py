# SPDX-License-Identifier: MIT
"""Decoded denoise initializer path comparison with modeled subsystem outcomes."""
import itertools,json,re
from build_gx8002_backup_denoise_initialize import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
BASE=0x2002d2bc


def execute(code,entry,delta,scenario,bindings):
    status,mode,algorithm,drc,audio,seed,allocation=scenario
    r={f'r{i}':(seed+i)&MASK for i in range(32)};r['r14']=0x20070000;initial=r.copy();pc=entry;saved=None;condition=False;trace=[];rates=0
    memory={BASE+16:mode,BASE+24:0xfeedface}
    names={v:k for k,v in bindings.items()}
    for _ in range(200):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r5, r15';saved={k:r[k] for k in ('r4','r5','r15')};r['r14']-=12
        elif op=='pop':
            assert args=='r4-r5, r15';r.update(saved);r['r14']+=12
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],memory[BASE+24],trace
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            value=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(value+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('br','bt','bf','bez','bnez'):
            take=op=='br' or (op=='bt' and condition) or (op=='bf' and not condition) or (op=='bez' and r[p[0]]==0) or (op=='bnez' and r[p[0]]!=0)
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(offset,0)
            if op=='ld.w':assert address==BASE+16;r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:assert address==BASE+24;memory[address]=r[reg];trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=int(args,0)+delta;name=names[target];ret=0
            if name=='printf':
                message=names[r['r0']];arguments=[message]
                if message=='denoise_msg_rate':arguments += [r['r1'],r['r2']]
            elif name=='denoise_status_3c8f8':arguments=[];ret=status
            elif name=='denoise_prepare_428e8':arguments=[r[f'r{i}'] for i in range(4)]
            elif name=='denoise_prepare_42850':arguments=[]
            elif name in ('denoise_beamforming_44140','denoise_imcra_4425c'):arguments=[];ret=algorithm
            elif name=='denoise_rate_428c0':arguments=[];ret=16000+rates;rates+=1
            elif name=='denoise_allocate_4286c':arguments=[r['r0']];ret=allocation
            elif name=='denoise_drc_470c4':arguments=[r[f'r{i}'] for i in range(3)];ret=drc
            elif name=='denoise_audio_42d58':arguments=[r['r0']];ret=audio
            else:raise ValueError(name)
            trace.append(('call',name,arguments))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=ret&MASK
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('Execution bound')


def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-denoise-initialize'
    old=decode((out/'stock.disassembly.txt').read_text());new=decode((out/'initialize.disassembly.txt').read_text());cases=0
    for scenario in itertools.product((0,1,2,0xffffffff),(0,1,2,0xffffffff),(0,1,0xffffffff),(0,0x20023000),(0,1,0xffffffff),(0,0x12345678),(0,0x20022000)):
        result=execute(new,0x1000bc44,0,scenario,evidence['bindings'])
        assert result==execute(old,0x44584,0x10000000-0x38940,scenario,evidence['bindings'])
        status,mode,algorithm,drc,audio,seed,allocation=scenario
        setup=status<2;algorithm_failed=setup and mode in (0,1) and algorithm!=0
        reached_drc=setup and not algorithm_failed
        failed=algorithm_failed or (reached_drc and drc==0) or audio!=0
        assert result[0]==(MASK if failed else 0)
        assert result[1]==(drc if reached_drc else 0xfeedface)
        rate_calls=[x for x in result[2] if x[:2]==('call','denoise_rate_428c0')]
        assert len(rate_calls)==(2 if reached_drc else 0)
        if reached_drc:assert ('call','denoise_drc_470c4',[16001,256,allocation]) in result[2]
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Subsystem calls modeled with poisoned caller-saved registers and independent return/state oracle. Null/nonnull allocation returns included; asynchronous state changes, actual subsystem bodies and hardware unqualified.']}
    (ROOT/'docs/research/gx8002-backup-denoise-initialize-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'])
