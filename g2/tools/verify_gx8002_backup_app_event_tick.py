# SPDX-License-Identifier: MIT
"""Decoded event tick callback ordering and mutable application selection."""
import itertools,json,re,subprocess
from build_gx8002_backup_app_event_tick import build,ROOT,Elf32,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode


def execute(code,pc,delta,available,app,response,loop,mutation,event):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;before=r.copy()
    memory={0x20016f74:app,0x20040008:response,0x2004000c:loop,0x20041008:0x10020000,0x2004100c:0x10020010};trace=[];saved=None
    for _ in range(120):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4, r15';saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            assert args=='r4, r15';r['r4'],r['r15']=saved;r['r14']+=8
            assert all(r[f'r{i}']==before[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],trace
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=a+(1 if op=='addi' else -1)*int(p[-1],0)
        elif op=='bez':
            if not r[p[0]]:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(offset,0)
            if op=='ld.w':r[reg]=memory[address]
            else:memory[address]=r[reg]
        elif op in ('bsr','jsr'):
            target=int(args,0)+delta if op=='bsr' else r[args]
            result=0xdeadbeef
            if target==0x10009fbc:
                assert r['r0']==0x2002d784 and r['r1']==r['r14']
                assert memory[r['r1']]==memory[r['r1']+4]==0
                trace.append(('queue',))
                if available:memory[r['r1']],memory[r['r1']+4]=event
                result=available
            elif target==0x1000b4c8:trace.append(('async',))
            elif target in (0x10020000,0x10020020):
                assert r['r0']==r['r14'];trace.append(('response',target,memory[r['r0']],memory[r['r0']+4]))
                if mutation!= -1:memory[0x20016f74]=mutation
            elif target in (0x10020010,0x10020030):trace.append(('loop',target))
            else:raise AssertionError(hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xbad00000+i
            r['r0']=result
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('execution bound')


def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4479c','--stop-address=0x447e8',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-app-event-tick/tick.disassembly.txt').read_text());count=0
    for args in itertools.product((0,1,0xffffffff),(0,0x20040000),(0,0x10020020),(0,0x10020030),(-1,0,0x20041000),((0,0),(92,7),(0xffffffff,0x80000000))):
        available,app,response,loop,mutation,event=args;expected=[('queue',)]
        if available and app and response:
            expected.append(('response',response,*event))
            if mutation!=-1:app=mutation
        current_loop=0x10020010 if app==0x20041000 else loop if app else 0
        if current_loop:expected.append(('loop',current_loop))
        expected.append(('async',))
        assert execute(old,0x4479c,0x10000000-0x38940,*args)==execute(new,0x1000be5c,0,*args)==(0,expected),args
        count+=1
    result={'build':evidence,'cases':count,'source_admitted':False,'limits':['Queue and callbacks modeled; initialized event, callback ordering, application pointer mutation, unconditional async tick and ABI checked against stock plus independent expected traces.', 'Separate queue-reader tests do not constitute nested whole-program execution; concurrent mutation and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-app-event-tick-execution.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['cases'])
