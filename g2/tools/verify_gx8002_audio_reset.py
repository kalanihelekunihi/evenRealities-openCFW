#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode both audio resets; compare ordered MMIO with an independent oracle."""
import json,re,shutil,struct,subprocess
from build_gx8002_audio_reset_candidate import ROOT,IMAGE,ADDRESS,OFFSET,SIZE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
BASE=0xa0a00000
REGS=(0,4,8,12,0x28,0x2c,0x48,0x4c,0x100,0x104,0x108,0x158,0x180)
# Independently transcribed stock register/bit ordering. Each entry is a fresh
# hardware read followed by one write; adjacent entries must not be merged.
BEFORE=[(0,31,0),(0,15,1),(0,14,0),(0,7,1),(0,6,0),(4,31,1),(4,30,0),(8,31,1),(8,30,0),(12,9,0),(0x28,9,0),(0x2c,9,0),(0x48,9,0),(0x4c,9,0)]
AFTER=[(0x108,15,1),(0x108,14,0),(0x108,7,1),(0x108,6,0),(0x108,23,1),(0x108,22,0),(0x158,31,1),(0x158,30,0),(0x180,31,1),(0x180,30,0),(0x180,29,0)]
class PrefixReached(Exception):pass
class MMIO:
    def __init__(self,seed,mode,delay,prefix):
        self.seed=seed;self.mode=mode;self.delay=delay;self.prefix=prefix;self.polls=0;self.reads=0;self.trace=[];self.state={BASE+o:seed for o in REGS}
    def read(self,address):
        if address not in self.state:raise ValueError('audio reset invalid MMIO read')
        if self.mode=='latched':value=self.state[address]
        elif self.mode=='constant':value=self.seed
        elif self.mode=='changing':value=(self.seed^(self.reads*0x9e3779b9)^(address*0x7654321))&MASK
        else:raise ValueError('audio reset response mode')
        self.reads+=1
        if address==BASE+0x104:
            value=(value&~0x100)|(0x100 if self.delay is not None and self.polls>=self.delay else 0);self.polls+=1
        self.trace.append(['read',address,value])
        if self.prefix is not None and self.polls>=self.prefix:raise PrefixReached
        return value
    def write(self,address,value):
        if address not in self.state:raise ValueError('audio reset invalid MMIO write')
        self.state[address]=value&MASK;self.trace.append(['write',address,value&MASK])

def expected(seed,mode,delay,prefix=None):
    m=MMIO(seed,mode,delay,prefix)
    def rmw(rows):
        for offset,bit,value in rows:
            address=BASE+offset;old=m.read(address);m.write(address,(old&~(1<<bit))|(value<<bit))
    try:
        m.write(BASE+0x100,0);m.write(BASE+0x104,MASK^0x700);rmw(BEFORE);m.write(BASE+0x104,0x200)
        while not m.read(BASE+0x104)&0x100:pass
        for value in (0x100,0x400,0x071f003f):m.write(BASE+0x104,value)
        rmw(AFTER)
        return m.trace,m.state,0,'return'
    except PrefixReached:return m.trace,m.state,None,'poll_prefix'

def execute(code,pc,seed,mode,delay,prefix=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();m=MMIO(seed,mode,delay,prefix)
    try:
        for _ in range(10000):
            op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
            if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
            elif op=='movih':r[p[0]]=(int(p[1],0)<<16)&MASK
            elif op=='nor':r[p[0]]=~(r[p[0]]|r[p[1]])&MASK
            elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
            elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
            elif op=='bclri':r[p[0]]&=MASK^(1<<int(p[1],0))
            elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
            elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
            elif op=='andni':r[p[0]]=r[p[1]]&(MASK^int(p[2],0))
            elif op=='ins':
                high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
            elif op=='zext':
                high,low=int(p[2],0),int(p[3],0);r[p[0]]=(r[p[1]]>>low)&((1<<(high-low+1))-1)
            elif op in ('ld.w','st.w'):
                match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
                if not match:raise ValueError('audio reset MMIO operand')
                reg,base,off=match.groups();address=(r[base]+int(off,0))&MASK
                if op=='ld.w':r[reg]=m.read(address)
                else:m.write(address,r[reg])
            elif op=='bez':
                if r[p[0]]==0:nxt=int(p[1],0)
            elif op=='rts':
                if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('audio reset ABI/frame')
                return m.trace,m.state,r['r0'],'return'
            else:raise ValueError('unknown audio reset instruction '+op)
            pc=nxt
    except PrefixReached:
        if r['r14']!=initial['r14']:raise ValueError('audio reset prefix frame')
        return m.trace,m.state,None,'poll_prefix'
    raise ValueError('audio reset execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'audio-reset-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D',f'--start-address={OFFSET}',f'--stop-address={OFFSET+SIZE}',str(w)],text=True));new=decode((out/'audio-reset-candidate.disassembly.txt').read_text());cases=prefixes=0
    seeds=[0,MASK,0x12345678,0xaaaaaaaa,0x55555555,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]]
    for seed in seeds:
        for mode in ('constant','latched','changing'):
            for delay in (0,1,2,3,7,15,31,63,255,1023):
                wanted=expected(seed,mode,delay)
                for code,pc in ((old,OFFSET),(new,ADDRESS)):
                    if execute(code,pc,seed,mode,delay)!=wanted:raise ValueError('audio reset MMIO/state/return mismatch')
                cases+=1
            for limit in (1,2,32):
                wanted=expected(seed,mode,None,limit)
                for code,pc in ((old,OFFSET),(new,ADDRESS)):
                    if execute(code,pc,seed,mode,None,limit)!=wanted:raise ValueError('audio reset polling prefix mismatch')
                prefixes+=1
    if not evidence['fits']:raise ValueError('audio reset envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':SIZE,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'audio-reset-candidate.elf',output/'audio-reset.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'noncompletion_prefix_cases':prefixes,'frame_bytes':0,'source_admitted':True,'hardware_qualified':False,'limits':['Ordered 32-bit MMIO with constant, latched and changing read responses; modeled completion after 0..1023 delayed polls at selected boundaries. Never-ready input checked through 32-read prefixes, not physical timing proof. Original unbounded wait retained. No hardware execution or external register semantics qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-audio-reset-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
