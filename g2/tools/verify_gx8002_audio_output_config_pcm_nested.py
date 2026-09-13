# SPDX-License-Identifier: MIT
"""Compose decoded PCM, I2S, DAC and latch against independent effects oracles."""
import json,subprocess
from itertools import product
from verify_gx8002_audio_output_config_pcm import execute as pcm_execute,oracle as pcm_oracle
from build_gx8002_audio_output_config_pcm import build as pcm_build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_audio_output_i2s_config import execute as i2s_execute,oracle as i2s_oracle,BASE,CONFIG
from build_gx8002_audio_output_i2s_config import build as i2s_build
from verify_gx8002_audio_output_dac import execute as dac_execute,oracle as dac_oracle
from build_gx8002_audio_output_dac import build as dac_build
from verify_gx8002_audio_output_lodac import execute as lodac_execute,oracle as lodac_oracle
from build_gx8002_audio_output_lodac import build as lodac_build
from verify_gx8002_memcpy_source import decode
HW=0xa0b00000

def verify():
    candidates=[f() for f in (pcm_build,i2s_build,dac_build,lodac_build)];wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('PCM nested stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xdf74','--stop-address=0xe3f8',str(wrapper)],text=True))
    new=[decode((ROOT/('build/gx8002-audio-output-'+stem)/'bits.disassembly.txt').read_text()) for stem in ('config-pcm','i2s-config','dac','lodac')];cases=0
    for bits,ratio,seed,level in product((16,32),(128,192,256,384,512,768,1024,1536),(0,0xffffffff,0xa5a5a5a5),(0,1,0xffffffff)):
        config=(16000).to_bytes(4,'little')+bytes((2,bits,1,1))+(16000*ratio).to_bytes(4,'little')
        def hook_factory(codes,entries):
            shared={}
            def hook(target,base,address,settings):
                if target in (0x10204ab0,0x102049e8):
                    index=0 if target==0x10204ab0 else 1;size=40 if index==0 else 36;expected=0x20030008 if index==0 else 0x20030030
                    if (base,address)!=(HW,expected):raise ValueError('Nested PCM helper address')
                    blob=settings[address-0x20030000:address-0x20030000+size]
                    if len(blob)!=size:raise ValueError('Nested PCM config extent')
                    events,state=(i2s_execute if index==0 else dac_execute)(codes[index],entries[index],blob,seed,base=base,config_address=address)
                else:
                    if target!=0x10204b5c or HW+4 not in shared:raise ValueError('Nested PCM latch order')
                    events,state=lodac_execute(codes[2],entries[2],shared[HW+4],level,seed,candidates[3]['stock_switch_targets'])
                shared.update(state)
                return events+[('helper_final',tuple(sorted(shared.items())))]
            return hook
        result,trace,word,state,settings=pcm_oracle(config,seed,False);expanded=[];shared={}
        for event in trace:
            expanded.append(event)
            if event[0]!='helper':continue
            target=event[1]
            if target in (0x10204ab0,0x102049e8):
                offset,size,oracle=(8,40,i2s_oracle) if target==0x10204ab0 else (48,36,dac_oracle)
                effects,registers=oracle(settings[offset:offset+size],seed)
                effects=[(e[0],e[1]+(0x20030000+offset-CONFIG if e[0]=='config' else HW-BASE),*e[2:]) for e in effects]
                registers={a+HW-BASE:v for a,v in registers.items()}
            else:effects,registers=lodac_oracle(shared[HW+4],level,seed)
            shared.update(registers);expanded.extend(effects);expanded.append(('helper_final',tuple(sorted(shared.items()))))
        wanted=(result,expanded,word,state,settings)
        for code,entry,codes,entries in ((old,0xe2c4,(old,old,old),(0xe03c,0xdf74,0xe0e8)),(new[0],0x10204d38,new[1:],(0x10204ab0,0x102049e8,0x10204b5c))):
            if pcm_execute(code,entry,config,seed,False,hook_factory(codes,entries))!=wanted:raise ValueError(('Nested PCM effects',entry,bits,ratio,seed,level))
        cases+=1
    return {'candidates':candidates,'nested_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual decoded PCM/I2S/DAC/latch paths; uniform initial helper MMIO and fixed valid settings memory. Settings-pointer mutation is tested separately with modeled helper bodies. Hardware semantics and asynchronous mutation remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-config-pcm-nested-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['nested_cases'])
