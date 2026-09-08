#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Continuously decode TWS initialization, including helper ABI and state writes."""
import json,re,struct,subprocess
from build_gx8002_tws_candidate import ROOT,IMAGE,BINDINGS,build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
DELTA=0x101f6a74

def execute(code,pc,delta,previous,wakeup,audio_result,seed):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;r['r0']=previous
    initial=r.copy();saved=None;trace=[];condition=False
    reverse={v:k for k,v in BINDINGS.items()}
    argc={'LvpQueueInit':4,'LvpInitMaxKws':0,'gx_pmu_get_wakeup_source':0,'LvpKwsInit':2,'LvpAudioInInit':1,'LvpAudioInStandbyToStartup':0,'printf':1}
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args!='r4-r5, r15':raise ValueError('TWS frame')
            saved={i:r[f'r{i}'] for i in (4,5,15)};r['r14']-=12
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='subi':r[p[0]]=((r[p[1]]-int(p[2],0)) if len(p)==3 else (r[p[0]]-int(p[1],0)))&MASK
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-12:raise ValueError('TWS call frame')
            target=(int(args,0)+delta)&MASK;name=reverse.get(target)
            if name not in argc:raise ValueError('unknown TWS helper')
            trace.append(['call',name,[r[f'r{i}'] for i in range(argc[name])]])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            if name=='gx_pmu_get_wakeup_source':r['r0']=wakeup
            elif name=='LvpAudioInInit':r['r0']=audio_result
        elif op=='st.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('TWS store operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&MASK
            if address not in (0x2002e738,0x2002e73c):raise ValueError('TWS state address')
            trace.append(['write',address,r[reg]])
        elif op=='pop':
            if saved is None or args!='r4-r5, r15' or r['r14']!=initial['r14']-12:raise ValueError('TWS return frame')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('TWS ABI')
            return {'trace':trace,'result':r['r0']}
        else:raise ValueError('unknown TWS instruction '+op)
        pc=nxt
    raise ValueError('TWS execution bound')

def expected(previous,wakeup,audio_result):
    t=[['call','LvpQueueInit',[0x2002e6ec,0x2002e700,56,8]],['call','LvpInitMaxKws',[]],
       ['call','gx_pmu_get_wakeup_source',[]],['call','LvpKwsInit',[0x10026340,wakeup]]]
    if previous!=65535 or wakeup<2:
        t.append(['call','LvpAudioInInit',[0x100263dc]])
        if audio_result:
            t.append(['call','printf',[0x1020b230]])
            return {'trace':t,'result':MASK}
    else:t.append(['call','LvpAudioInStandbyToStartup',[]])
    t.extend([['write',0x2002e738,2],['write',0x2002e73c,50]])
    return {'trace':t,'result':0}

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'tws-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x11bfc','--stop-address=0x11c68',str(w)],text=True))
    new=decode((out/'tws-candidate.disassembly.txt').read_text());cases=0
    for previous in (0,1,2,0xfffe,0xffff,0x10000,0x7fffffff,0x80000000,0xffffffff):
     for wakeup in (0,1,2,3,4,5,6,0x7fffffff,0xffffffff,*[1<<i for i in range(3,32)]):
      for result in (0,1,2,0x80000000,0xffffffff):
       for seed in (0,0xffffffff,0x12345678):
        want=expected(previous,wakeup,result)
        for code,entry,delta in ((old,0x11bfc,DELTA),(new,0x10208670,0)):
         if execute(code,entry,delta,previous,wakeup,result,seed)!=want:raise ValueError('TWS trace mismatch')
        cases+=1
    report={'build':evidence,'cases':cases,'frame_bytes':12,'source_admitted':False,
      'limits':['Continuous init control flow with modeled returning helpers, caller clobbers and ordered standby writes. Queue and printf already have source; decoder, audio/KWS helpers, callbacks, messages and state require separate ownership. No hardware or whole-TWS qualification.']}
    (ROOT/'docs/research/gx8002-tws-comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(verify(),indent=2))
