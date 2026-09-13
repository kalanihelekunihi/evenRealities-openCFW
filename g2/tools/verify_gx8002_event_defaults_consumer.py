# SPDX-License-Identifier: MIT
"""Execute first and repeated VAD events with compiled initialized state."""
import json,re,subprocess
from build_gx8002_event_defaults import build,ROOT,sha,Elf32
from execute_gx8002_sample_event import execute
from verify_gx8002_sample_event import EVENT,CONTEXT,STATE,APP
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode


def verify():
    candidate=build();p=ROOT/'build/gx8002-event-defaults/defaults.elf';elf=Elf32(p.read_bytes(),'defaults');data=elf.contents(next(s for s in elf.sections if s['name']=='.event_state'))
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    artifact,report_name=re.search(r"\('sample-event',\s*\w+,\s*'([^']+)',\s*'([^']+)'\)",registry).groups()
    p=ROOT/'build/gx8002-source-candidate/sample-event'/artifact;elf=Elf32(p.read_bytes(),'event');report=json.loads((ROOT/'docs/research'/report_name).read_text())
    for s in elf.sections:
        if s['flags']&2 and s['size']:assert any(r.get('compiled_sha256')==sha(elf.contents(s)) for r in report['functions'])
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(p)],text=True));cases=0
    for vad in range(256):
        memory={a+i:0 for a,n in ((EVENT,8),(CONTEXT,32),(STATE,8),(APP,28)) for i in range(n)}
        memory.update({STATE+i:v for i,v in enumerate(data)});word(memory,EVENT+4,17);memory[CONTEXT+12]=vad
        for repeat in (False,True):
            expected=dict(memory);word(expected,STATE,vad&7)
            def helper(target,args,mem,trace,sp):
                if target==0x10206ec8:
                    assert args[0]==17;word(mem,args[1],CONTEXT);word(mem,args[2],99);trace.append(('lookup',17))
                elif target==0x1020979c:trace.append(('vad',args[0]))
                else:raise AssertionError(hex(target))
                return 0
            ret,after,trace=execute(code,0x10208f04,[EVENT],memory,helper)
            trace=[e for e in trace if e[0]!='write_byte']
            assert ret==('return',0) and after==expected and trace==[('lookup',17)]+([] if repeat else [('vad',vad&7)])
            assert bytes(after[STATE+i] for i in range(4,8))==data[4:]
            memory=after;cases+=1
    pending_cases=0
    for enabled in (0,1):
        for outputs in (False,True):
            for helper_result in (0,0xffffffff):
                memory={a+i:0 for a,n in ((EVENT,8),(CONTEXT,32),(STATE,8),(APP,28)) for i in range(n)}
                memory.update({STATE+i:v for i,v in enumerate(data)})
                for address,value in ((EVENT,91),(EVENT+4,17),(CONTEXT,0x20042000),(APP+4,7),(APP+20,enabled),(APP+24,0x20050000)):
                    word(memory,address,value)
                for repeat in (False,True):
                    expected=dict(memory);word(expected,STATE,0)
                    wanted=[('lookup',17)]+([] if repeat else [('vad',0)])
                    if enabled and not repeat:
                        start=320 if outputs else (-0x20050000)&0xffffffff
                        end=(start+(320 if outputs else 0)-1)&0xffffffff
                        wanted.extend([('print',0x1020b4ea,17,1),('mic',0x20042000,0,17),('mic',0x20042000,1,17),('print',0x1020b50a,start,end),('frame',7,start,end)])
                        expected[STATE+4]=0
                    def pending_helper(target,args,mem,trace,sp):
                        if target==0x10206ec8:
                            trace.append(('lookup',args[0]));word(mem,args[1],CONTEXT);word(mem,args[2],99)
                        elif target==0x1020979c:trace.append(('vad',args[0]))
                        elif target==0x10206c24:trace.append(('print',*args[:3]))
                        elif target==0x10208e80:
                            trace.append(('mic',*args[:3]))
                            if outputs:
                                word(mem,args[3],0x20050140+args[1]*4096);word(mem,word(mem,sp),320)
                        elif target==0x10205488:trace.append(('frame',args[0],word(mem,args[1]),word(mem,args[1]+4)))
                        else:raise AssertionError(hex(target))
                        return helper_result
                    ret,after,trace=execute(code,0x10208f04,[EVENT],memory,pending_helper)
                    trace=[e for e in trace if e[0]!='write_byte']
                    assert ret==('return',0) and after==expected and trace==wanted,(enabled,repeat,trace,wanted)
                    assert bytes(after[STATE+i] for i in range(5,8))==data[5:]
                    memory=after;pending_cases+=1
    return {'candidate':candidate,'consumer_elf_sha256':sha(p.read_bytes()),'cases':cases,'pending_cases':pending_cases,'source_admitted':False,
            'limits':['All 256 input VAD bytes execute initial and repeated events on compiled defaults. First notification follows the sentinel; repeat suppresses notification. Pending byte and padding preserved.',
                      'Sixteen sequential event-91 runs check initially pending consumption, disabled-channel preservation, repeat suppression, helper failures and absent microphone outputs. Helpers remain modeled; I2S start/stop composition remains separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-event-defaults-consumer.json').write_text(json.dumps(r,indent=2)+'\n');print('Event defaults consumer:',r['cases'],'cases')
