# SPDX-License-Identifier: MIT
"""Authenticate public I2S wrapper's three field-to-internal-state copies."""
import json,subprocess
from build_gx8002_audio_output_i2s_config import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('I2S mapping stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0xe1f0','--stop-address=0xe21c',str(wrapper)],text=True))
    expected={0xe1f6:('ld.w','r3, (r0, 0x30)'),0xe1f8:('ld.w','r2, (r1, 0x4)'),0xe1fa:('st.w','r2, (r3, 0x14)'),0xe1fc:('ld.w','r2, (r1, 0x8)'),0xe1fe:('st.w','r2, (r3, 0x18)'),0xe200:('ld.w','r2, (r1, 0x0)'),0xe202:('movih','r0, 41136'),0xe206:('st.w','r2, (r3, 0x20)'),0xe208:('addi','r1, r3, 8'),0xe20a:('bsr','0xe03c')}
    for pc,want in expected.items():
        if code[pc][:2]!=want:raise ValueError('I2S field mapping changed '+hex(pc))
    return {'candidate':candidate,'wrapper_package_offset':0xe1f0,'hardware_base':0xa0b00000,'mapping':[{'public_field':'bclk','public_offset':0,'internal_word':6,'register_offset':4,'bits':[16,16]},{'public_field':'pcm_length','public_offset':4,'internal_word':3,'register_offset':4,'bits':[3,2]},{'public_field':'data_format','public_offset':8,'internal_word':4,'register_offset':4,'bits':[1,0]}],'limits':['Other internal configuration fields retain bit-position names. This authenticates the public-to-internal mapping, not full wrapper execution or hardware timing.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-audio-output-i2s-mapping.json').write_text(json.dumps(r,indent=2)+'\n');print('Three public I2S field mappings authenticated')
