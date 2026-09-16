# SPDX-License-Identifier: MIT
"""Finite numeric execution of decoded C-SKY cosine, with explicit FPU model."""
import re
from gx8002_binary32_rational import operation,fused_operation

def execute(code,entry,input_bits,table,fused=False):
    r={};f={'fr0':input_bits};pc=entry;condition=False;opfloat=fused_operation if fused else operation
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('lrw','movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op in ('fsitos','fstosi.rz'):f[p[0]]=opfloat(op,f[p[1]])
        elif op=='fstoui.rz':
            v=opfloat('fstosi.rz',f[p[1]]);assert v<0x80000000;f[p[0]]=v
        elif op=='fuitos':assert f[p[1]]<0x80000000;f[p[0]]=opfloat('fsitos',f[p[1]])
        elif op in ('fmuls','fsubs'):f[p[0]]=opfloat(op,f[p[1]],f[p[2]])
        elif op=='fmacs':f[p[0]]=opfloat(op,f[p[1]],f[p[2]],f[p[0]])
        elif op=='fcmpzhss':condition=opfloat('fcmphss',f[p[0]],0)
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='fldrs':
            m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(r\d+) << 2\)',args);assert m,args
            reg,base,index=m.groups();assert r[base]==0x100148d4;offset=r[index]*4;assert offset+4<=len(table);f[reg]=int.from_bytes(table[offset:offset+4],'little')
        elif op=='rts':return f['fr0']
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('bound')
