#!/usr/bin/env python3
"""Compare stock/source mutex wrappers with real context/state query instructions."""
import argparse
import importlib.util
import itertools
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(mutex_acquire=0x4166aa,mutex_release=0x416710)
class Machine(v.Machine):
    def __init__(self,*args,**kw):
        super().__init__(*args,**kw);self.kernel_result=1
    def code(self,uc,pc,size,user):
        if pc in [0x419e22,0x41a24e,0x419de2,0x419ec0]:
            r0,r1,r2,r3=self.args()
            if pc in [0x419e22,0x41a24e]:event=['take',hex(pc),r0,r1]
            elif pc==0x419de2:event=['give_tagged',r0]
            else:event=['give_plain',r0,r1,r2,r3]
            self.events.append(event);self.ret(self.kernel_result);return
        super().code(uc,pc,size,user)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert v.sha(v.BLOB)==v.SHA
    _,segments,symbols=v.elf.elf_info(args.elf);cases=[];trace={}
    contexts=[(0,0,0),(0,1,0),(0,0,32),(1,1,32),(2,0,0),(2,1,32)]
    for name in ['mutex_acquire','mutex_release']:
        timeouts=[0,1000,0xffffffff] if name=='mutex_acquire' else [0]
        for handle,timeout,result,context in itertools.product([0,1,0x50,0x51],timeouts,[0,1,2],contexts):
            mode,primask,basepri=context
            machines=[Machine(),Machine(True,segments,symbols)];outputs=[]
            for m in machines:
                m.kernel_result=result;m.w(0x20027150,0 if mode==1 else 1);m.w(0x2002716c,0 if mode==2 else 1)
                m.cpu.reg_write(v.a.UC_ARM_REG_PRIMASK,primask);m.cpu.reg_write(v.a.UC_ARM_REG_BASEPRI,basepri)
                d=m.run(name,[handle,timeout]);outputs.append({'return':d['return'],'events':d['events'],'primask':m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),'basepri':m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)})
            assert outputs[0]==outputs[1],(name,handle,timeout,result,context,outputs)
            nonblocking=mode!=1 and (primask!=0 or basepri!=0)
            expected=-6 if nonblocking else -4 if (handle&~1)==0 else 0 if result==1 else -2 if name=='mutex_acquire' and timeout else -3
            assert outputs[0]['return']==(expected&0xffffffff)
            trace.update(machines[0].trace);cases.append(dict(function=name,handle=handle,timeout=timeout,kernel_result=result,context=context,observed=outputs[0]))
    used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
    d=dict(status='PASS',cases=len(cases),distinct_original_trace_bytes=len(used),original_trace=trace,original_sha256=v.SHA,elf_sha256=v.sha(args.elf),source_sha256={str(p.relative_to(ROOT)):v.sha(p) for p in HERE.iterdir() if p.suffix in ['.c','.h','.ld','.py'] or p.name=='Makefile'},comparisons=cases,
           limits=['Stock/source mutex wrappers, context predicate and runtime-state query execute; tagged/plain kernel operations are synthetic.',
                   'Bit0 dispatch and scalar statuses proved in tested thread-mode fixtures; nonzero IPSR remains statically recovered, not injected.',
                   'Raw timeout forwarded unchanged; no scheduler, mutex priority inheritance, recursive ownership, blocking time or real kernel storage claim.',
                   'Synthetic kernel results include2 to prove exact success==1, not any nonzero; no malformed real kernel pointer safety claim.'])
    args.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:d[k] for k in ['status','cases','distinct_original_trace_bytes']}))
if __name__=='__main__':main()
