# SPDX-License-Identifier: MIT
"""Shared-memory decoded processing executor; finite FPU and explicit helper models."""
import re,struct,math
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def execute(code,entry,memory,arguments,helpers,fused=False,limit=500000,float_arguments=()):
    arithmetic=fused_operation if fused else operation
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r14=0x8000,r15=0xfffffff0)
    for i,v in enumerate(arguments):r[f'r{i}']=v&M
    initial=r.copy();f={f'fr{i}':0x60000000+i for i in range(16)};initial_f=f.copy()
    for i,v in enumerate(float_arguments):f[f'fr{i}']=v&M
    mem=dict(memory);trace=[];pc=entry;condition=False;base=0x20000000
    def finish():
        assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
        assert all(f[f'fr{i}']==initial_f[f'fr{i}'] for i in range(8,16))
        return {'result':r['r0'],'trace':trace,'memory':{a:v for a,v in mem.items() if a>=base}}
    def signed(v):return v if v<0x80000000 else v-0x100000000
    def read(a,n):return sum(mem[a+i]<<(8*i) for i in range(n))
    def write(a,v,n):
        for i in range(n):mem[a+i]=(v>>(8*i))&255
        if a>=base:trace.append(('write',a,v&((1<<(8*n))-1),n))
    def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
    def value(v):return struct.unpack('<f',struct.pack('<I',v))[0]
    for _ in range(limit):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('push','pop'):
            regs=[]
            for part in p:
                if '-' in part:
                    a,b=part.split('-');regs.extend('r'+str(i) for i in range(int(a[1:]),int(b[1:])+1))
                else:regs.append(part)
            if op=='push':
                r['r14']-=len(regs)*4
                for i,reg in enumerate(regs):write(r['r14']+i*4,r[reg],4)
            else:
                for i,reg in enumerate(regs):r[reg]=read(r['r14']+i*4,4)
                r['r14']+=len(regs)*4
                if 'r15' in regs:
                    if r['r15']==0xfffffff0:return finish()
                    nxt=r['r15']
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='fnegs':f[p[0]]=f[p[1]]^0x80000000
        elif op=='fuitos':f[p[0]]=bits(float(f[p[1]]))
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='abs':r[p[0]]=abs(signed(r[p[1]]))&M
        elif op=='max.u32':r[p[0]]=max(r[p[1]],r[p[2]])
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='zext':
            high,low=int(p[2],0),int(p[3],0)
            r[p[0]]=(r[p[1]]>>low)&((1<<(high-low+1))-1)
        elif op=='sextb':
            v=r[p[1]]&255;r[p[0]]=v|0xffffff00 if v&128 else v
        elif op=='lsr':
            amount=r[p[-1]];assert amount<=31
            r[p[0]]=r[p[0] if len(p)==2 else p[1]]>>amount
        elif op=='and':r[p[0]]=r[p[0] if len(p)==2 else p[1]]&r[p[-1]]
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('addu','subu','addi','subi','lsli','lsri','asri'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=((a+b) if op in ('addu','addi') else a-b if op in ('subu','subi') else a<<b if op=='lsli' else a>>b if op=='lsri' else signed(a)>>b)&M
        elif op=='rts':
            if r['r15']==0xfffffff0:return finish()
            nxt=r['r15']
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&M
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op in ('blsz','bhz','blz','bhsz','bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            v=signed(r[p[0]])
            if {'bhsz':v>=0,'blsz':v<=0,'bhz':v>0,'blz':v<0,'bez':v==0,'bnez':v!=0,'bnezad':v!=0}[op]:nxt=int(p[1],0)
        elif op in ('ld.w','st.w','fsts','flds','ld.h','ld.hs','st.h','ld.b','st.b'):
            m=re.fullmatch(r'((?:fr|r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,addr,off=m.groups();a=r[addr]+int(off,0);n=2 if op in ('ld.h','ld.hs','st.h') else 1 if op in ('ld.b','st.b') else 4
            if op in ('st.w','st.h','st.b','fsts'):write(a,(f if op=='fsts' else r)[reg],n)
            else:
                v=read(a,n)
                if op=='ld.hs' and v&0x8000:v|=0xffff0000
                (f if op=='flds' else r)[reg]=v
        elif op in ('str.h','ldr.h'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(r\d+) << (\d+)\)',args);assert m,args
            reg,addr,index,shift=m.groups();a=r[addr]+(r[index]<<int(shift))
            if op=='str.h':write(a,r[reg],2)
            else:r[reg]=read(a,2)
        elif op in ('ldbi.hs','ldbi.h','ldbi.w','stbi.h'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)\)',args);assert m,args
            reg,addr=m.groups();a=r[addr]
            if op=='stbi.h':write(a,r[reg],2)
            else:
                v=read(a,4 if op=='ldbi.w' else 2);r[reg]=v|0xffff0000 if op=='ldbi.hs' and v&0x8000 else v
            r[addr]+=4 if op=='ldbi.w' else 2
        elif op=='sexth':r[p[0]]=r[p[1]]|0xffff0000 if r[p[1]]&0x8000 else r[p[1]]&0xffff
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op in ('fsitos','fstosi.rz','frecips'):f[p[0]]=arithmetic(op,f[p[1]])
        elif op in ('fmuls','fadds','fsubs','fdivs'):f[p[0]]=arithmetic(op,f[p[1]],f[p[2]])
        elif op in ('fmacs','fnmacs'):f[p[0]]=arithmetic(op,f[p[1]],f[p[2]],f[p[0]])
        elif op=='mulsh':
            def s16(v):return (v&0x7fff)-(v&0x8000)
            r[p[0]]=(s16(r[p[1] if len(p)==3 else p[0]])*s16(r[p[-1]]))&M
        elif op=='sext':
            high,low=int(p[2],0),int(p[3],0);bits=high-low+1;v=(r[p[1]]>>low)&((1<<bits)-1)
            r[p[0]]=(v-(1<<bits) if v&(1<<(bits-1)) else v)&M
        elif op=='max.s32':r[p[0]]=max(signed(r[p[1]]),signed(r[p[2]]))&M
        elif op=='nor':r[p[0]]=~(r[p[-1]]|r[p[-2]])&M
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmplti':condition=signed(r[p[0]])<int(p[1],0)
        elif op=='mult':r[p[0]]=(r[p[1] if len(p)==3 else p[0]]*r[p[-1]])&M
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&M
        elif op=='divs':
            a,b=signed(r[p[1]]),signed(r[p[2]]);assert b
            r[p[0]]=(abs(a)//abs(b)*(-1 if (a<0)!=(b<0) else 1))&M
        elif op in ('lsl','asr'):
            a=r[p[1] if len(p)==3 else p[0]];b=r[p[-1]];assert b<=31
            r[p[0]]=((a<<b) if op=='lsl' else signed(a)>>b)&M
        elif op in ('fldrs','fstrs','str.w'):
            m=re.fullmatch(r'((?:fr|r)\d+),\s*\((r\d+),\s*(r\d+) << (\d+)\)',args);assert m,args
            reg,addr,index,shift=m.groups();a=r[addr]+(r[index]<<int(shift))
            if op=='fldrs':f[reg]=read(a,4)
            else:write(a,(r if op=='str.w' else f)[reg],4)
        elif op in ('fcmplts','fcmphss'):condition=arithmetic(op,f[p[0]],f[p[1]])
        elif op=='fcmpznes':condition=bool(f[p[0]]&0x7fffffff)
        elif op=='fstoui.rz':
            v=value(f[p[1]]);assert 0<=v<4294967296;f[p[0]]=int(v)
        elif op=='bsr':
            target=int(args,0);r['r15']=nxt
            if target in helpers:
                helpers[target](r,f,mem,trace,read,write)
            else:
                assert target in code,hex(target)
                nxt=target
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')
