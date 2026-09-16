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


def execute(code,entry,helper,table,hcode,source,enabled,record,flash_result,seed,same_frame=False,extra_memory=None,delta=0):
    r={f'r{i}':(seed+i*0x10203)&MASK for i in range(32)};r['r14']=0x20002ffc;initial=r.copy();mem={0x200014c8+i:v for i,v in enumerate(table)};trace=[];pc=entry;condition=False;returns=[]
    def finish():
        assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
        return r['r0'],trace
    mem.update(extra_memory or {})
    ids=[struct.unpack_from('<I',table,i*16)[0] for i in range(26)]
    def store(a,v):
        for i in range(4):mem[a+i]=(v>>(i*8))&255
    def load(a,n):return sum(mem[a+i]<<(8*i) for i in range(n))
    for i,v in enumerate(struct.pack('<8I',28,0,18,1,16,0,0,0)):mem[0x20001668+i]=v
    for a in (0xa001008c,0xa0300088):store(a,source)
    for a in (0xa0010018,0xa0300018):store(a,enabled)
    for a in range(0xa0010000,0xa0010200,4):
        if a not in (0xa001008c,0xa0010018):store(a,source)
    for a in range(0xa0300000,0xa0300200,4):
        if a not in (0xa0300088,0xa0300018):store(a,enabled)
    for a in (0xa0005084,0xa00050c8):store(a,source)
    for _ in range(30000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('push','pop'):
            registers=[]
            for item in args.split(', '):
                m=re.fullmatch(r'r(\d+)(?:-r(\d+))?',item);assert m
                registers += [f'r{i}' for i in range(int(m[1]),int(m[2] or m[1])+1)]
            if op=='push':
                r['r14']-=4*len(registers)
                for i,reg in enumerate(registers):store(r['r14']+i*4,r[reg])
            else:
                for i,reg in enumerate(registers):r[reg]=load(r['r14']+i*4,4)
                r['r14']+=4*len(registers)
                if returns:
                    nxt=returns.pop();assert r['r15']==nxt
                else:return finish()
        elif op=='rts':
            if returns:
                nxt=returns.pop();assert r['r15']==nxt
            else:return finish()
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('subi','addi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+int(p[-1],0)*(1 if op=='addi' else -1))&MASK
        elif op=='bclri':r[p[0]]=r[p[0] if len(p)==2 else p[1]]&~(1<<int(p[-1],0))
        elif op=='jmp':nxt=r[p[0]]-delta
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
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
        elif op=='sextb':r[p[0]]=((r[p[1]]&255)-(256 if r[p[1]]&128 else 0))&MASK
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='cmplti':condition=(r[p[0]] if r[p[0]]<0x80000000 else r[p[0]]-0x100000000)<int(p[1],0)
        elif op in ('cmphs','cmphsi'):condition=r[p[0]]>=(r[p[1]] if p[1].startswith('r') else int(p[1],0))
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('cmpne','cmpnei'):condition=r[p[0]]!=(r[p[1]] if p[1].startswith('r') else int(p[1],0))
        elif op in ('bt','bf','br','bez','bnez','bnezad','blz','bhsz'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&MASK
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:take=(bool(r[p[0]]&0x80000000)==(op=='blz')) if op in ('blz','bhsz') else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op=='bsr':
            if int(args,0)!=helper:
                target=int(args,0)+delta
                if target==0x10000fdc:
                    assert record is not None and (r['r0'],r['r2'])==(0xff000,64) and r['r1']%16==0
                    assert r['r14']<=r['r1'] and r['r1']+64<=initial['r14']
                    trace.append(('flash',r['r0'],64));mem.update({r['r1']+i:v for i,v in enumerate(record)})
                    for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
                    r['r0']=flash_result;pc=nxt;continue
                name={0x100004f4:'trim',0x10000eb8:'trim32',0x10000ea0:'trimall',0x10001310:'board'}[target]
                trace.append((name,r['r0']) if name not in ('board','trim') else (name,))
                if record is not None:
                    returns.append(nxt);r['r15']=nxt;pc=int(args,0);continue
                if name!='board':assert r['r0']==0
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
                pc=nxt;continue
            module=r['r0'];assert module<26;trace.append(('lookup',module))
            if same_frame:
                returns.append(nxt);r['r15']=nxt;pc=helper;continue
            result,_,writes=lookup(hcode,0x10000138,module,0x1000,ids)
            for a,v in writes:store(r['r1']+a-0x1000,v)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        elif op=='ldr.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (0|2|3)\)',args);assert m
            dest,base,index,shift=m.groups();r[dest]=load((r[base]+(r[index]<<int(shift)))&MASK,4)
        elif op in ('ld.w','ld.b','ld.bs','ldbi.b','ld.h','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m
            reg,base,off=m.groups();a=r[base]+(int(off,0) if off else 0)
            if op=='st.w':
                assert a>=0xa0000000 or initial['r14']-320<=a<initial['r14'];store(a,r[reg])
                if a>=0xa0000000:trace.append(('write',a,r[reg]))
            else:
                v=load(a,4 if op=='ld.w' else 2 if op=='ld.h' else 1);r[reg]=(v-256 if op=='ld.bs' and v&128 else v)&MASK
                if op=='ldbi.b':r[base]+=1
                if a>=0xa0000000:trace.append(('read',a,r[reg]))
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')


def verify(composed=False):
    from build_gx8002_stage1_clock_cluster import build as combined
    from analyze_gx8002_upstream_objects import IMAGE
    evidence=combined();out=ROOT/'build/gx8002-stage1-clock-cluster';elf=Elf32((out/'cluster.elf').read_bytes(),'clock');table=elf.contents(next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table'))
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3912c','--stop-address=0x39678',str(wrapper)],text=True));new=decode((out/'cluster.disassembly.txt').read_text())
    hcode=decode((ROOT/'build/gx8002-stage1-clock-tables/lookup.disassembly.txt').read_text())
    stock=IMAGE.read_bytes();oldmem={0x10000000+i:v for i,v in enumerate(stock[0x38954:0x3b938])};oldmem.update({0x20000000+i:v for i,v in enumerate(stock[0x38954:0x3b938])})
    newmem={}
    for s in elf.sections:
        if s['flags']&2:
            newmem.update({s['address']+i:v for i,v in enumerate(elf.contents(s))})
    if composed:
        old=decode(subprocess.check_output([pre,'-D','--start-address=0x38a8c','--stop-address=0x39c78',str(wrapper)],text=True))
    cases=0
    record=bytearray(64);struct.pack_into('<5I',record,0,0x47525553,1,1,2,3);record[63]=reduce(xor,record[:63])
    for source,enabled,seed,record_kind,flash_status in product((0,MASK,0xaaaaaaaa,0x55555555),(0,MASK),(0x12345678,0x87654321),(0,1,2) if composed else (0,),(0,MASK) if composed else (0,)):
        supplied=record.copy()
        if record_kind==1:supplied[0]^=1
        if record_kind==2:supplied[63]^=1
        a=execute(old,0x3912c,0x38a8c,table,hcode,source,enabled,supplied if composed else None,flash_status,seed,same_frame=composed,extra_memory=oldmem,delta=0x10000000-0x38954)
        b=execute(new,0x100007d8,0x10000138,table,hcode,source,enabled,supplied if composed else None,flash_status,seed,same_frame=composed,extra_memory=newmem)
        assert a[1]==b[1],(source,enabled,a,b)
        assert [e for e in b[1] if e[0] in ('trim32','trimall')][:2]==[('trim32',0),('trimall',0)]
        assert sum(e[0]=='board' for e in b[1])==1
        if composed:
            assert [e for e in b[1] if e[0] in ('trim32','trimall')]==[('trim32',0),('trimall',0)]+([('trimall',1)] if record_kind==0 else [])
            assert sum(e[0]=='flash' for e in b[1])==1
        cases+=1
    report={'composed':composed,'cases':cases,'build':evidence,'limits':[('Initialization, trim setters, board hook, trim and lookup execute in one frame.' if composed else 'Outer initialization with modeled trim/board and separate lookup.')+'  Finite register-memory model; flash always supplies64 bytes even on modeled error. Hardware timing and partial transfers unqualified. Void return unconstrained; ABI checked.']}
    (ROOT/('docs/research/gx8002-stage1-clock-initialize-full'+('-composed' if composed else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'outer initialization cases passed')
