# SPDX-License-Identifier: MIT
"""Compose decoded public wrapper and internal DAC with an independent oracle."""
import json,subprocess
from itertools import product
from verify_gx8002_audio_output_config_dac import run,oracle as wrapper_oracle,DEST
from verify_gx8002_audio_output_dac import execute,oracle as dac_oracle,BASE,CONFIG
from build_gx8002_audio_output_config_dac import build as wrapper_build
from build_gx8002_audio_output_dac import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();wrapper_candidate=wrapper_build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Nested DAC stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xdf74','--stop-address=0xe260',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-output-config-dac/bits.disassembly.txt').read_text());dac_new=decode((ROOT/'build/gx8002-audio-output-dac/bits.disassembly.txt').read_text());cases=0
    for pointer,seed,mmio in product((0,0x20040000,DEST-4,DEST,DEST+4),(0,1,127,255),(0,0xffffffff,0xa5a5a5a5)):
        def hook(code,entry):
            def invoke(config):
                trace,state=execute(code,entry,config,mmio,base=0xa0b00000,config_address=DEST)
                return trace+[('dac_final',tuple(sorted(state.items())))]
            return invoke
        result,trace,memory=wrapper_oracle(pointer,seed)
        if pointer:
            config=bytes(memory[DEST+i] for i in range(36));effects,state=dac_oracle(config,mmio)
            effects=[(event[0],event[1]+(DEST-CONFIG if event[0]=='config' else 0xa0b00000-BASE),*event[2:]) for event in effects]
            trace.extend(effects);trace.append(('dac_final',tuple(sorted((a+0xa0b00000-BASE,v) for a,v in state.items()))))
        wanted=(result,trace,memory)
        if run(old,0xe21c,pointer,seed,hook(old,0xdf74))!=wanted or run(new,0x10204c90,pointer,seed,hook(dac_new,0x102049e8))!=wanted:raise ValueError('Nested DAC effects mismatch')
        cases+=1
    return {'candidate':candidate,'wrapper_candidate':wrapper_candidate,'nested_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual decoded DAC instructions execute with wrapper-produced36-byte config at observed hardware base. Uniform initial MMIO; finite null/alias cases. Physical semantics of extension fields remain unresolved.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-dac-nested-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['nested_cases'])
