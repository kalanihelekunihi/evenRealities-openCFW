# SPDX-License-Identifier: MIT
"""Admit typed playback settings and a selector with input-independent behavior."""
import json,shutil,subprocess
from pathlib import Path
from build_gx8002_audio_output_hw_config import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';stock=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(stock.contents(next(s for s in stock.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Selector stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe900','--stop-address=0xe908',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-hw-config/bits.disassembly.txt').read_text())
    for code,entry in ((old,0xe900),(new,0x10205374)):
        op,args,width=code[entry]
        if (op,args,width)!=('lrw','r0, 0x20026c1c',2):raise ValueError('Selector constant return')
        op,args,width=code[entry+2]
        if (op,args,width)!=('rts','',2):raise ValueError('Selector immediate return')
    # These two instructions have no input-register or RAM dependency, writes,
    # branches, or calls. The literal is authenticated by the build comparison.
    rows=[]
    for item in candidate['functions']:
        row={key:item[key] for key in ('symbol','section_name','compiled_bytes','compiled_sha256','ownership_kind')}
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_dram_data' if item['ownership_kind']=='generated_source_data' else 'image_a_xip_text'}];rows.append(row)
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-output-hw-config/bits.elf',output/'bits.elf')
    evidence=('build_gx8002_audio_output_hw_config.py','verify_gx8002_audio_output_hw_config_source.py','verify_gx8002_memcpy_source.py')
    return {'functions':rows,'candidate':candidate,'selector_proof':{'decoded_instructions':2,'returns':0x20026c1c,'input_independent':True,'ram_writes':0,'calls':0},'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in evidence},'source_admitted':True,'hardware_qualified':False,'limits':['Typed mutable initializer matches stock and authenticated pinned SDK. Layout assertions cover consumer offsets. Some hardware field semantics and full boot/data-copy composition remain unqualified; this does not establish whole-source closure.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-hw-config-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Settings and selector source admission passed')
