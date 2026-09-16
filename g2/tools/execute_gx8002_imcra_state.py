# SPDX-License-Identifier: MIT
"""Bounded full initializer executor with explicit finite FPU/helper models."""
import re,struct,math
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def execute(code,entry,size=43008,fused=False,cosine=None):
    arithmetic=fused_operation if fused else operation
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=48000,r1=0x20010000,r2=size,r14=0x8000);initial=r.copy()
    f={f'fr{i}':0x60000000+i for i in range(16)};initial_f=f.copy();mem={};trace=[];pc=entry;condition=False;base=0x20010000
    def signed(v):return v if v<0x80000000 else v-0x100000000
    def read(a,n):return sum(mem.get(a+i,0xa5)<<(8*i) for i in range(n))
    def write(a,v,n):
        for i in range(n):mem[a+i]=(v>>(8*i))&255
        if a>=base:trace.append(('write',a,v&((1<<(8*n))-1),n))
    def bits(v):return struct.unpack('<I',struct.pack('<f',v))[0]
    def value(v):return struct.unpack('<f',struct.pack('<I',v))[0]
    for _ in range(50000):
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
                assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
                assert all(f[f'fr{i}']==initial_f[f'fr{i}'] for i in range(8,16))
                return {'result':r['r0'],'trace':trace,'memory':{a:v for a,v in mem.items() if a>=base}}
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addu','subu','addi','subi','lsli','lsri','asri'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=r[p[-1]] if op in ('addu','subu') else int(p[-1],0)
            r[p[0]]=((a+b) if op in ('addu','addi') else a-b if op in ('subu','subi') else a<<b if op=='lsli' else a>>b if op=='lsri' else signed(a)>>b)&M
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='blsz':
            if signed(r[p[0]])<=0:nxt=int(p[1],0)
        elif op in ('ld.w','st.w','fsts','flds','ld.h','ld.hs'):
            m=re.fullmatch(r'((?:fr|r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,addr,off=m.groups();a=r[addr]+int(off,0);n=2 if op in ('ld.h','ld.hs') else 4
            if op in ('st.w','fsts'):write(a,(f if op=='fsts' else r)[reg],n)
            else:
                v=read(a,n)
                if op=='ld.hs' and v&0x8000:v|=0xffff0000
                (f if op=='flds' else r)[reg]=v
        elif op in ('str.h','ldr.h'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(r\d+) << (\d+)\)',args);assert m,args
            reg,addr,index,shift=m.groups();a=r[addr]+(r[index]<<int(shift))
            if op=='str.h':write(a,r[reg],2)
            else:r[reg]=read(a,2)
        elif op in ('ldbi.hs','stbi.h'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)\)',args);assert m,args
            reg,addr=m.groups();a=r[addr]
            if op=='stbi.h':write(a,r[reg],2)
            else:
                v=read(a,2);r[reg]=v|0xffff0000 if v&0x8000 else v
            r[addr]+=2
        elif op=='sexth':r[p[0]]=r[p[1]]|0xffff0000 if r[p[1]]&0x8000 else r[p[1]]&0xffff
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op in ('fsitos','fstosi.rz','frecips'):f[p[0]]=arithmetic(op,f[p[1]])
        elif op in ('fmuls','fadds','fsubs','fdivs'):f[p[0]]=arithmetic(op,f[p[1]],f[p[2]])
        elif op in ('fmacs','fnmacs'):f[p[0]]=arithmetic(op,f[p[1]],f[p[2]],f[p[0]])
        elif op=='bsr':
            target=int(args,0)+(0x10000000-0x38940 if entry<0x10000000 else 0);result=0;fp=0;pair=None
            if target==0x100100a4:
                assert (f['fr0'],f['fr1'])==(0x41200000,0xbf19999a);fp=0x3e809bcc;trace.append(('power',f['fr0'],f['fr1']))
            elif target==0x1000ee64:
                trace.append(('cosine',f['fr0']));fp=cosine(f['fr0'],fused) if cosine else bits(math.cos(value(f['fr0'])))
            elif target==0x1000e314:
                s=r['r0'];mode=r['r1'];result=0 if mode==0 else (read(s+28,4)*72+read(s+28,4)*read(s+104,4)*8+read(s+12,4)*10+read(s+16,4)*4+read(s+116,4)*8+4)&M;trace.append(('workspace',s,mode,result))
            elif target==0x100113c4:
                trace.append(('memset',r['r0'],r['r1'],r['r2']));assert r['r2']<=43008
                for i in range(r['r2']):mem[r['r0']+i]=r['r1']&255
            elif target==0x10011af4:pair=struct.unpack('<II',struct.pack('<d',value(f['fr0'])))
            elif target==0x10009934:trace.append(('printf',r['r0'],r['r1'],r['r2']))
            else:raise AssertionError(hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            for i in range(8):f[f'fr{i}']=0xdead1000+i
            r['r0']=result;f['fr0']=fp
            if pair:r['r0'],r['r1']=pair
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')
