# SPDX-License-Identifier: MIT
import re,struct
from execute_gx8002_double_unpack import execute as unpack


def execute(code,entry,left,right,unpack_entry,add_entry,pack_entry=None):
    r={f'r{i}':0x70000000+i for i in range(32)};r['r14']=0x20050000
    r['r0'],r['r1']=struct.unpack('<II',struct.pack('<d',left));r['r2'],r['r3']=struct.unpack('<II',struct.pack('<d',right))
    initial=r.copy();memory={};saved=None;condition=False;pc=entry
    for _ in range(60):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];following=pc+width
        if op=='push':
            if args not in ('r15','r4-r5, r15'):raise ValueError('GE save')
            regs=['r15'] if args=='r15' else ['r4','r5','r15'];saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            r.update(saved);r['r14']+=4*len(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('GE ABI')
            return r['r0']|(r['r1']<<32) if pack_entry is not None else r['r0'] if r['r0']<0x80000000 else r['r0']-0x100000000
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=r[base]+int(off,0)
            if not initial['r14']-88<=address<initial['r14']:raise ValueError('GE stack access')
            if op=='st.w':memory[address]=r[reg]
            else:r[reg]=memory[address]
        elif op=='xori':r[p[0]]=r[p[1]]^int(p[2],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='bt':
            if condition:following=int(args,0)
        elif op=='bsr':
            target=int(args,0);result=0
            if target==unpack_entry:
                bits=memory[r['r0']]|(memory[r['r0']+4]<<32)
                fields=unpack(code,unpack_entry,bits)
                for off,value in fields.items():memory[r['r1']+off]=value
            elif target==add_entry:
                if (r['r0'],r['r1'],r['r2'])!=(r['r14']+16,r['r14']+36,r['r14']+56):raise ValueError('Subtract core pointers')
                fields=[{off:memory[base+off] for off in (0,4,8,12,16) if base+off in memory} for base in (r['r0'],r['r1'])]
                if pack_entry is None:return fields
                from execute_gx8002_fpadd_core import execute as add
                selected,output=add(code,add_entry,*fields)
                result={0x20040000:r['r0'],0x20040100:r['r1'],0x20040200:r['r2']}[selected]
                for off,value in output.items():memory[result+off]=value
            elif target==pack_entry:
                from execute_gx8002_double_pack_integer import execute as pack
                fields={off:memory[r['r0']+off] for off in (0,4,8,12,16) if r['r0']+off in memory}
                packed=pack(code,pack_entry,fields)
                result=packed&0xffffffff

            else:raise ValueError('GE helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result&0xffffffff
            if target==pack_entry:r['r1']=packed>>32
        else:raise ValueError('GE opcode '+op)
        pc=following
    raise ValueError('GE bound')
