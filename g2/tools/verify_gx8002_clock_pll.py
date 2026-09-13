# SPDX-License-Identifier: MIT
"""Decoded PLL register sequence against independent ordered register model."""
import json,re,random,subprocess
from build_gx8002_clock_pll_candidate import build,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
BASE=0xa0005000
PARAM=0x20031000
OFFSETS=(0x1c,0x20,0x24,0x28,0x2c,0x30,0x3c)
def execute(code,entry,present,fields,registers,perturb):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r0']=PARAM if present else 0;initial=r.copy();m=dict(registers);events=[];pc=entry
    for _ in range(200):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.b','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if a>=BASE:
                assert a-BASE in OFFSETS
                if op=='st.w':m[a-BASE]=r[reg];events.append(('write',a,r[reg]))
                else:
                    assert op=='ld.w';r[reg]=(m[a-BASE]+perturb*len(events))&MASK;events.append(('read',a,r[reg]))
            else:
                assert op!='st.w' and present and PARAM<=a<PARAM+56
                value=fields[(a-PARAM)//4];r[reg]=value if op=='ld.w' else (value>>(8*((a-PARAM)%4)))&255
        elif op=='bez':
            if not r[p[0]]:nxt=int(p[1],0)
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='and':r[p[0]]&=r[p[1]]
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return events,m
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')
def oracle(present,f,registers,perturb):
    m=dict(registers);events=[]
    def update(off,mask,value=0):
        read=(m[off]+perturb*len(events))&MASK;events.append(('read',BASE+off,read));m[off]=(read&~mask)|value;m[off]&=MASK;events.append(('write',BASE+off,m[off]))
    if present:
        update(0x3c,2);update(0x3c,1)
        if f[0]:
            update(0x1c,63);update(0x1c,0,f[4]);update(0x20,255);update(0x24,31)
            update(0x20,0,f[5]&255);update(0x24,0,(f[5]>>8)&31)
            update(0x28,7);update(0x28,0,f[9]);update(0x2c,127);update(0x2c,0,f[6])
            update(0x30,7);update(0x30,0,f[11]&7);update(0x30,48);update(0x30,0,(f[8]<<4)&MASK)
            update(0x3c,4);update(0x3c,0,(f[7]&1)<<2);update(0x3c,0,2);update(0x3c,0,1)
    return events,m

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x16b18','--stop-address=0x16be0',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-pll-candidate.disassembly.txt').read_text());rng=random.Random(805)
    for i in range(512):
        fields=[rng.getrandbits(32) for _ in range(14)];fields[0]=0 if i%3==0 else fields[0];present=i%7!=0;registers={o:rng.getrandbits(32) for o in OFFSETS};perturb=(0,1,0xffffffff,0x81234567)[i%4]
        expected=oracle(present,fields,registers,perturb)
        assert execute(old,0x16b18,present,fields,registers,perturb)==expected
        assert execute(new,0x10024b04,present,fields,registers,perturb)==expected
    return {'candidate':candidate,'cases':512,'limits':['Ordered MMIO reads/writes with changing read values, null/disabled branches and integer ABI; analog lock and physical timing remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-pll-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
