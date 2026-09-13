# SPDX-License-Identifier: MIT
"""Compose decoded public wrapper and internal I2S with an independent oracle."""
import json,subprocess
from verify_gx8002_audio_output_lodac import execute as lodac_execute,oracle as lodac_oracle
from build_gx8002_audio_output_lodac import build as lodac_build
from itertools import product
from verify_gx8002_audio_output_config_i2s import run,oracle as wrapper_oracle,DEST
from verify_gx8002_audio_output_i2s_config import execute,oracle as i2s_oracle,BASE,CONFIG
from build_gx8002_audio_output_config_i2s import build as wrapper_build
from build_gx8002_audio_output_i2s_config import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();wrapper_candidate=wrapper_build();lodac_candidate=lodac_build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Nested I2S stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe03c','--stop-address=0xe21c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-output-config-i2s/bits.disassembly.txt').read_text());i2s_new=decode((ROOT/'build/gx8002-audio-output-i2s-config/bits.disassembly.txt').read_text());lodac_new=decode((ROOT/'build/gx8002-audio-output-lodac/bits.disassembly.txt').read_text());cases=0
    for pointer,seed,mmio,level in product((0,0x20040000,DEST-4,DEST,DEST+4),(0,1,127,255),(0,0xffffffff,0xa5a5a5a5),(0,1,0xffffffff)):
        def hooks(code,entry,lodac_code,lodac_entry):
            shared={}
            def invoke(config):
                trace,state=execute(code,entry,config,mmio,base=0xa0b00000,config_address=DEST)
                shared.update(state)
                return trace+[('i2s_final',tuple(sorted(state.items())))]
            def finish():
                if 0xa0b00004 not in shared:raise ValueError('Lodac before I2S')
                trace,state=lodac_execute(lodac_code,lodac_entry,shared[0xa0b00004],level,mmio,lodac_candidate['stock_switch_targets'])
                shared.update(state)
                return trace+[('path_final',tuple(sorted(shared.items())))]
            return invoke,finish
        result,trace,memory=wrapper_oracle(pointer,seed)
        if pointer:
            if trace.pop()!=('lodac',):raise ValueError('Expected final lodac boundary')
            config=bytes(memory[DEST+i] for i in range(40));effects,state=i2s_oracle(config,mmio)
            effects=[(event[0],event[1]+(DEST-CONFIG if event[0]=='config' else 0xa0b00000-BASE),*event[2:]) for event in effects]
            trace.extend(effects);trace.append(('i2s_final',tuple(sorted((a+0xa0b00000-BASE,v) for a,v in state.items()))))
            trace.append(('lodac',))
            final={a+0xa0b00000-BASE:v for a,v in state.items()}
            effects,lodac_state=lodac_oracle(final[0xa0b00004],level,mmio)
            final.update(lodac_state);trace.extend(effects);trace.append(('path_final',tuple(sorted(final.items()))))
        wanted=(result,trace,memory)
        if run(old,0xe1f0,pointer,seed,*hooks(old,0xe03c,old,0xe0e8))!=wanted or run(new,0x10204c64,pointer,seed,*hooks(i2s_new,0x10204ab0,lodac_new,0x10204b5c))!=wanted:raise ValueError('Nested I2S effects mismatch')
        cases+=1
    return {'candidate':candidate,'wrapper_candidate':wrapper_candidate,'lodac_candidate':lodac_candidate,'nested_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual decoded I2S instructions execute with wrapper-produced40-byte config at observed hardware base. Uniform initial MMIO; finite null/alias cases. Actual decoded lodac follows I2S-produced register state; physical semantics of extension fields remain unresolved.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-i2s-config-nested-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['nested_cases'])
