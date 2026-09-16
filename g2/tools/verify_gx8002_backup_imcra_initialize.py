# SPDX-License-Identifier: MIT
"""Decoded wrapper ordering and ABI; DSP calls are modeled, not executed."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_imcra_initialize import build,ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,entry,allocation,rate,state,replacement):
    r={f'r{i}':0x70000000+i for i in range(32)};initial=r.copy();mem={0x2002d2c4:17,0x2002d2c8:19};trace=[];pc=entry;saved=None
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args.replace(' ','')=='r4,r15';saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            r['r4'],r['r15']=saved;r['r14']+=8
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],trace,mem
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&M
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&M
        elif op in ('st.w','ld.w'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,base,offset=m.groups();address=r[base]+int(offset,0)
            if op=='st.w':mem[address]=r[reg];trace.append(('write',address,r[reg]))
            else:r[reg]=mem[address];trace.append(('read',address,r[reg]))
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0);target=target+0x10000000-0x38940 if entry<0x10000000 else target
            if target==0x10009f2c:trace.append(('allocate',r['r0']));result=allocation
            elif target==0x10009f80:
                trace.append(('rate',));result=rate
                # Exercise mandatory buffer reload across a potentially mutating call.
                if replacement is not None:mem[0x2002d2c4]=replacement
            elif target==0x1000e384:trace.append(('initialize',r['r0'],r['r1'],r['r2']));result=state
            elif target==0x10009934:trace.append(('printf',r['r0']));result=123
            else:raise AssertionError(hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-imcra-initialize';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    raw=subprocess.check_output([pre+'objdump','-D','--start-address=0x4425c','--stop-address=0x44298',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)
    stock=decode(raw);source=decode((out/'index.disassembly.txt').read_text());cases=0
    for allocation,rate,state,replacement in product((0,0x20010000,M),(0,16000,48000,M),(0,1,0x20020000,M),(None,0,0x20012340)):
        a=execute(stock,0x4425c,allocation,rate,state,replacement);b=execute(source,0x1000b91c,allocation,rate,state,replacement);assert a==b,(a,b)
        buffer=allocation if replacement is None else replacement
        expected=[('allocate',43008),('write',0x2002d2c4,allocation),('rate',),('read',0x2002d2c4,buffer),('initialize',rate,buffer,43008),('write',0x2002d2c8,state)]
        if not state:expected.append(('printf',0x1001378c))
        assert a==(0 if state else M,expected,{0x2002d2c4:buffer,0x2002d2c8:state});cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Helpers are modeled with caller-register clobbers. DSP functionality, allocation validity and hardware behavior are not qualified.']}
    (ROOT/'docs/research/gx8002-backup-imcra-initialize-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
