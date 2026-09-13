# SPDX-License-Identifier: MIT
"""Callback mutation checks for decoded audio initialization."""
import json,subprocess
from itertools import product
from build_gx8002_audio_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_audio_initialize import execute,STATE
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Callback stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdd70','--stop-address=0xdf10',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-initialize/gain.disassembly.txt').read_text());cases=0
    for record,mask,output,left,right in product((0,0x10300000),range(8),range(8),(0,2,8),(1,7,15)):
        callbacks=(record,0x10300004,0x10300008,0x1030000c,0x10300010)
        def hook(memory):
            expected={8:callbacks[1],12:callbacks[0],16:callbacks[2],20:callbacks[3],24:callbacks[4]}
            if any(memory[STATE+off]!=value for off,value in expected.items()):raise ValueError('Callback publication order/state')
            # Callback clears registered callbacks. Initializer must continue
            # using original arguments for record-presence and direct callback.
            changes={STATE+off:0 for off in (8,12,16,20,24)}
            changes.update({STATE:mask,STATE+4:output,0xa0a00028:left,0xa0a0002c:right,0xa0a00048:right,0xa0a0004c:left})
            return [('callback_mutation',mask,output,left,right)],changes
        args=(callbacks,0,0,0,0)
        a=execute(old,0xdd70,*args,config_hook=hook);b=execute(new,0x102047e4,*args,config_hook=hook)
        if a!=b:raise ValueError('Callback mutation differential')
        memory=a[2]
        if memory[0xa0a00100]!=(output&7 if record else 0):raise ValueError('Original record callback presence lost')
        for off,original,enabled in ((0x28,left,mask&2 and left<2),(0x2c,right,mask&2 and right<2),(0x48,right,mask&4 and right<8),(0x4c,left,mask&4 and left<8)):
            if memory[0xa0a00000+off]!=(original|(512 if enabled else 0)):raise ValueError('Callback selector not reloaded')
        cases+=1
    return {'candidate':candidate,'callback_mutation_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Config callback modeled, mutates published callbacks, both masks and asymmetric selectors. Original argument presence preserved while live state changes honored. Actual callback source composition pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-initialize-callback-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['callback_mutation_cases'])
