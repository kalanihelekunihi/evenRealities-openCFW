# SPDX-License-Identifier: MIT
"""Execute compiled buffer control flow and real decoded scalar helper calls."""
import json,re
from build_gx8002_backup_shift_q15 import build,ROOT
from verify_gx8002_memcpy_source import decode
from verify_gx8002_shift_sample_decoded import execute as sample_execute
from verify_gx8002_backup_shift_q15_host import expected

def execute(code,entry,values,shift,count,delta):
    mem=bytearray(values);r={f'r{i}':0x76540000+i for i in range(32)}
    r.update(r0=64,r1=shift&0xffffffff,r2=64+delta,r3=count,r14=0x10000)
    initial=r.copy();pc=entry;frames=[];trace=[]
    def access(addr,size,value=None):
        assert 0<=addr and addr+size<=len(mem) and addr%size==0
        if value is None:
            value=int.from_bytes(mem[addr:addr+size],'little');trace.append(('read',addr,size,value));return value
        value&=(1<<(size*8))-1;trace.append(('write',addr,size,value));mem[addr:addr+size]=value.to_bytes(size,'little')
    for _ in range(count*50+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            m=re.fullmatch(r'r4-r(\d+), r15',args);assert m,args
            names=[*(f'r{i}' for i in range(4,int(m.group(1))+1)),'r15'];frames.append({k:r[k] for k in names});r['r14']-=4*len(names)
        elif op=='pop':
            saved=frames.pop();r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return mem,trace
        elif op=='bsr':
            r['r15']=nxt;r=sample_execute(code,int(args,0),0,0,registers=r)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('lsri','lsli'):
            a=r[p[1]];b=int(p[2],0);r[p[0]]=(a>>b if op=='lsri' else a<<b)&0xffffffff
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='or':r[p[0]]=r[p[1]]|r[p[2]]
        elif op in ('addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0);r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op=='br':nxt=int(args,0)
        elif op in ('bnez','bez','blz'):
            value=r[p[0]];take=value!=0 if op=='bnez' else value==0 if op=='bez' else bool(value&0x80000000)
            if take:nxt=int(p[1],0)
        elif op=='bloop':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:nxt=int(p[1],0)
        elif op=='neg.s32.s':
            value=r[p[1]];r[p[0]]=0x7fffffff if value==0x80000000 else (-value)&0xffffffff
        elif op in ('plsl.s16.s','pasr.s16'):
            value=r[p[1]];amount=r[p[2]];packed=0
            for lane in range(2):
                v=(value>>(lane*16))&65535;v=v-65536 if v&32768 else v
                if op=='pasr.s16':result=v>>(amount&31)
                else:
                    if amount>=32 and v==0:raise ValueError('Unqualified vendor zero/large-shift semantics')
                    result=(-32768 if v<0 else 32767 if v>0 else 0) if amount>16 else max(-32768,min(32767,v*(1<<amount)))
                packed|=(result&65535)<<(lane*16)
            r[p[0]]=packed
        elif op=='pldbi.d':
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args);assert m,args
            reg,base=m.groups();address=r[base]
            r[reg]=access(address,4);r['r'+str(int(reg[1:])+1)]=access(address+4,4);r[base]+=8
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return mem,trace
        elif op in ('ld.w','st.w','ldbi.h','ldbi.hs','stbi.h','stbi.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m,args
            reg,base,offset=m.groups();address=r[base]+(int(offset,0) if offset else 0);size=2 if op.endswith(('.h','.hs')) else 4
            if op.startswith('ld'):
                value=access(address,size)
                r[reg]=(value-65536)&0xffffffff if op=='ldbi.hs' and value&32768 else value
            else:access(address,size,r[reg])
            if 'bi.' in op:r[base]+=size
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('instruction bound')

def verify():
    evidence=build();code=decode((ROOT/'build/gx8002-backup-shift-q15/shift.disassembly.txt').read_text());cases=0
    shifts=(-0x80000000,-33,-32,-31,-16,-1,0,1,8,15,16,17,31,32,0x7fffffff)
    for count in range(33):
      for shift in shifts:
       for delta in (-16,-8,-4,0,4,8,16,256):
        original=bytes((i*73+19)&255 for i in range(512));wanted=bytearray(original);trace=[];a,b=64,64+delta
        def read(addr,size):
            value=int.from_bytes(wanted[addr:addr+size],'little');trace.append(('read',addr,size,value));return value
        def transform(value):
            value=value-65536 if value&32768 else value;return expected(value,shift)&65535
        def write(addr,size,value):
            trace.append(('write',addr,size,value));wanted[addr:addr+size]=value.to_bytes(size,'little')
        for _ in range(count//4):
            x,y=read(a,4),read(a+4,4)
            write(b,4,transform(x&65535)|(transform(x>>16)<<16));write(b+4,4,transform(y&65535)|(transform(y>>16)<<16));a+=8;b+=8
        for _ in range(count&3):write(b,2,transform(read(a,2)));a+=2;b+=2
        actual,observed=execute(code,evidence['entry'],original,shift,count,delta)
        assert actual==wanted and observed==trace,(count,shift,delta)
        cases+=1
    report={'build':evidence,'decoded_buffer_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual compiled outer loop and decoded helper calls; complete memory and ordered sample read/write trace match block-transfer scalar oracle.','Stock DSP instructions not executed by this check. pldbi.d represented as two word reads in oracle; atomicity, extreme positive-zero hardware semantics and full-domain proof remain pending.']}
    (ROOT/'docs/research/gx8002-shift-buffer-decoded.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['decoded_buffer_cases'],'decoded buffer cases')
