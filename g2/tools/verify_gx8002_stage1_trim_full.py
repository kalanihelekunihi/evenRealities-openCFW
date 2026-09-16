# SPDX-License-Identifier: MIT
"""Execute complete stock/source trim with modeled flash and compiled lookup."""
import json,re,struct,subprocess
from functools import reduce
from operator import xor
from itertools import product
from build_gx8002_stage1_clock_trim import build,ROOT,Elf32
from compare_gx8002_stage1_clock_lookup import execute as lookup
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff


def execute(code,entry,helper,table,hcode,source,enabled,record,flash_result,seed,same_frame=False):
    r={f'r{i}':(seed+i*0x10203)&MASK for i in range(32)};r['r14']=0x20002ffc;initial=r.copy();mem={0x200014c8+i:v for i,v in enumerate(table)};trace=[];pc=entry;condition=False;returns=[]
    def finish():
        assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
        return r['r0'],trace
    ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
    def store(a,v):
        for i in range(4):mem[a+i]=(v>>(i*8))&255
    def load(a,n):return sum(mem[a+i]<<(8*i) for i in range(n))
    for i,v in enumerate(struct.pack('<8I',28,0,18,1,16,0,0,0)):mem[0x20001668+i]=v
    for a in (0xa001008c,0xa0300088):store(a,source)
    for a in (0xa0010018,0xa0300018):store(a,enabled)
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('push','pop'):
            assert args=='r4, r15'
            if op=='push':
                r['r14']-=8;store(r['r14'],r['r4']);store(r['r14']+4,r['r15'])
            else:
                r['r4']=load(r['r14'],4);r['r15']=load(r['r14']+4,4);r['r14']+=8;return finish()
        elif op=='rts':
            if returns:
                nxt=returns.pop();assert r['r15']==nxt
            else:return finish()
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('subi','addi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+int(p[-1],0)*(1 if op=='addi' else -1))&MASK
        elif op=='bseti':r[p[0]]=r[p[0] if len(p)==2 else p[1]]|(1<<int(p[-1],0))
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='rotli':
            v=r[p[1]];n=int(p[2],0);r[p[0]]=((v<<n)|(v>>(32-n)))&MASK
        elif op=='addu':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+r[p[-1]])&MASK
        elif op=='xor':r[p[0]]^=r[p[1]]
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op in ('and','andn','or','nor','subu','lsl','lsr'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]]
            if op in ('lsl','lsr'):assert b<32
            r[p[0]]=(a&b if op=='and' else a&~b if op=='andn' else a|b if op=='or' else ~(a|b) if op=='nor' else a-b if op=='subu' else a<<b if op=='lsl' else a>>b)&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('cmphs','cmphsi'):condition=r[p[0]]>=(r[p[1]] if p[1].startswith('r') else int(p[1],0))
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('cmpne','cmpnei'):condition=r[p[0]]!=(r[p[1]] if p[1].startswith('r') else int(p[1],0))
        elif op in ('bt','bf','br','bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&MASK
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:take=(r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op=='bsr':
            if int(args,0)!=helper:
                assert int(args,0)==(0x39930 if entry<0x10000000 else 0x10000fdc)
                assert (r['r0'],r['r2'])==(0xff000,64) and r['r1']%16==0
                assert r['r14']<=r['r1'] and r['r1']+64<=initial['r14']
                trace.append(('flash',r['r0'],64))
                mem.update({r['r1']+i:v for i,v in enumerate(record)})
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
                r['r0']=flash_result;pc=nxt;continue
            module=r['r0'];assert module in (9,10,6,13);trace.append(('lookup',module))
            if same_frame:
                returns.append(nxt);r['r15']=nxt;pc=helper;continue
            result,_,writes=lookup(hcode,0x10000138,module,0x1000,ids)
            for a,v in writes:store(r['r1']+a-0x1000,v)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        elif op=='ldr.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args);assert m
            dest,base,index=m.groups();r[dest]=load((r[base]+r[index])&MASK,4)
        elif op in ('ld.w','ld.b','ld.bs','ldbi.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m
            reg,base,off=m.groups();a=r[base]+(int(off,0) if off else 0)
            if op=='st.w':
                assert a>=0xa0000000 or initial['r14']-160<=a<initial['r14'];store(a,r[reg])
                if a>=0xa0000000:trace.append(('write',a,r[reg]))
            else:
                v=load(a,4 if op=='ld.w' else 1);r[reg]=(v-256 if op=='ld.bs' and v&128 else v)&MASK
                if op=='ldbi.b':r[base]+=1
                if a>=0xa0000000:trace.append(('read',a,r[reg]))
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')


def verify(cluster=False,same_frame=False):
    assert not same_frame or cluster
    if cluster:
        from build_gx8002_stage1_clock_cluster import build as combined
        evidence=combined();out=ROOT/'build/gx8002-stage1-clock-cluster';filename='cluster'
    else:
        evidence=build();out=ROOT/'build/gx8002-stage1-clock-trim';filename='trim'
    elf=Elf32((out/(filename+'.elf')).read_bytes(),'trim');table=elf.contents(next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table'))
    assert b''.join(elf.contents(next(s for s in elf.sections if s['name']==name)) for name in ('.data.low','.data.high'))==struct.pack('<8I',28,0,18,1,16,0,0,0)
    from build_gx8002_stage1_clock_tables import build as tables
    tables();hcode=decode((ROOT/'build/gx8002-stage1-clock-tables/lookup.disassembly.txt').read_text())
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x38e48','--stop-address=0x3912c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((out/(filename+'.disassembly.txt')).read_text());cases=0
    if same_frame:
        old.update(decode(subprocess.check_output([pre,'-D','--start-address=0x38a8c','--stop-address=0x38b4c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True)))
    for source,enabled,valid,flash_result,seed in product((0,MASK,0xaaaaaaaa,0x55555555),(0,MASK),(0,1,2),(0,MASK),(0x12345678,0x87654321)):
        record=bytearray(64);struct.pack_into('<5I',record,0,0x47525553,1,0x1234,0x5678,0x9abc);record[63]=reduce(xor,record[:63])
        if valid==1:record[0]^=1
        if valid==2:record[63]^=1
        a=execute(old,0x38e48,0x38a8c,table,hcode,source,enabled,record,flash_result,seed,same_frame=same_frame)
        b=execute(new,0x100004f4,0x10000138,table,hcode,source,enabled,record,flash_result,seed,same_frame=same_frame)
        assert a==b,(source,enabled,valid,flash_result,a,b)
        assert b[0]==(0 if valid==0 else MASK)
        assert [e for e in b[1] if e[0]=='lookup']==[('lookup',9)]*2+([('lookup',10),('lookup',6),('lookup',13),('lookup',9),('lookup',9)] if valid==0 else [])
        cases+=1
    report={'lookup_same_frame':same_frame,'cluster':cluster,'candidate_sha256':__import__('hashlib').sha256((out/(filename+'.elf')).read_bytes()).hexdigest(),'cases':cases,'build':evidence,'limits':[('Complete trim and lookup execute in one register frame.' if same_frame else 'Complete trim executes with lookup in a separate frame.')+' ABI comparison; Flash always supplies all64 bytes, including modeled error return. MMIO register model is finite; hardware timing, incomplete flash transfers and concurrent mutation unqualified.']}
    (ROOT/('docs/research/gx8002-stage1-trim-full'+('-cluster' if cluster else '')+('-same-frame' if same_frame else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'full trim cases passed')
