# SPDX-License-Identifier: MIT
"""Decoded nested trim query, using supplied gate boundary."""
def execute(codes,value,gate_runner=None):
    trace=[]
    def run(name,entry):
        r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;initial=dict(r);pc=entry
        for _ in range(16):
            op,args,width=codes[name][pc];p=[v.strip() for v in args.split(',')]
            if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
            elif op=='pop':
                assert args=='r15';r['r15']=saved;r['r14']+=4;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0']
            elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
            elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
            elif op=='ld.w':assert args=='r0, (r3, 0x30)' and r['r3']==0xa0010000;r['r0']=value;trace.append(('read',0xa0010030,value))
            elif op=='bsr':
                target=int(args,0)
                if target==0x10024a10:run('trim-clock-enable',target)
                else:
                    assert target==0x10025080;trace.append(('gate',r['r0'],r['r1']))
                    if gate_runner:gate_runner(r['r0'],r['r1'],value)
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            else:raise ValueError((op,args))
            pc+=width
        raise AssertionError('Execution bound')
    result=run('trim-state',0x10024a1c)
    return result,trace
