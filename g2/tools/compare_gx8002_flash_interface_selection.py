#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded full-interface JEDEC dispatch, isolated from setup and XIP."""
import contextlib,io,json,struct,subprocess
from build_gx8002_flash_interface_candidate import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode

def execute(code,pc,stop,identifier,delta):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r4']=identifier;carry=None;trace=[]
    for _ in range(100):
        if pc==stop:return trace
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)&0xffffffff
        elif op in ('cmpne','cmplt','cmphsi'):
            a=r[p[0]];b=int(p[1],0) if op=='cmphsi' else r[p[1]]
            if op=='cmplt':a=a-(1<<32) if a>>31 else a;b=b-(1<<32) if b>>31 else b
            carry=a!=b if op=='cmpne' else a<b if op=='cmplt' else a>=b
        elif op in ('br','bt','bf'):
            if op!='br' and carry is None:raise ValueError('undefined condition')
            if op=='br' or carry==(op=='bt'):n=int(args,0)
        elif op=='bsr':
            target=int(args,0)+delta
            if target not in (0x100242b4,0x10024330,0x100242ec,0x10023734):raise ValueError('unexpected dispatch call')
            trace.append(target)
            if target==0x10023734:return trace # Special status transaction qualified separately.
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xa5a50000+i
        else:raise ValueError('unknown dispatch opcode '+op)
        pc=n
    raise ValueError('dispatch bound')

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    wrapper=out/'interface-selection-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x164bc','--stop-address=0x165aa',str(wrapper)],text=True))
    new=decode((out/'flash-interface.disassembly.txt').read_text())
    pair={0xb4014,0xb4016,0xb4017,0x854012,0x856013,0x856014,0xb36014,0xba6015,0xc84015,0xc84215,0xc86015,0xc86016,0xcd7015,0xef4015}
    skip={0x1c3812,0x1c3813,0x1c7017}
    ids={0,0xffffffff,0x7fffffff,0x80000000}
    for v in pair|skip|{0x204016,0x684015,0xc22017}:
        ids.update((v-1,v,v+1))
    ids.update((i*0x9e3779b9)&0xffffffff for i in range(4096))
    for v in sorted(ids):
        if v==0xc22017:expected=[0x10023734]
        elif v==0x684015:expected=[0x100242b4,0x10024330]
        elif v in pair:expected=[0x10024330]
        elif v in skip:expected=[]
        else:expected=[0x100242b4]+([0x100242ec] if v==0x204016 else [])
        if execute(old,0x164bc,0x16550,v,0x1000dfec)!=expected or execute(new,0x100244a8,0x100244d0,v,0)!=expected:raise ValueError(f'JEDEC dispatch {v:#x}')
    report={'build':evidence,'cases':len(ids),'source_admitted':False,'limits':['Isolated dispatch only; C22017 path stops at first status read.', 'Full setup, MMIO, special status transaction, frame, callback stores and XIP argument verification remain.']}
    (ROOT/'docs/research/gx8002-flash-interface-selection-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(len(ids));return report
if __name__=='__main__':verify()
