# SPDX-License-Identifier: MIT
"""Build distance-noise register query without retained machine-code input."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_in/v2.0/audio_in.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();obj=Elf32(authenticated_blob(sdk/rel,blob),rel)
    s=next(s for s in obj.sections if s['name']=='.text.gx_audio_in_get_distance_noise_smooth');upstream=obj.contents(s)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert upstream==stock[0xdd38:0xdd38+len(upstream)] and not obj.relocations(s['index'])
    out=ROOT/'build/gx8002-distance-noise';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_distance_noise.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'noise.o')],check=True)
    (out/'noise.ld').write_text('SECTIONS { .text 0x102047ac : { *(.text*) } }\n')
    subprocess.run([pre+'ld','-T',str(out/'noise.ld'),str(out/'noise.o'),'-o',str(out/'noise.elf')],check=True)
    e=Elf32((out/'noise.elf').read_bytes(),'noise');s=next(s for s in e.sections if s['name']=='.text');body=e.contents(s)
    assert len(body)<=12 and not e.relocations(s['index'])
    assert len([s for s in e.sections if s['flags']&2 and s['size']])==1
    return {'sdk_commit':SDK_COMMIT,'upstream_blob':blob,'upstream_bytes':len(upstream),'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(body),'compiled_sha256':sha(body),'package_offset':0xdd38,'runtime_address':0x102047ac,'source_admitted':False,'hardware_qualified':False,'limits':['Pinned SDK leaf matches deployed function. Compiler emits a different address-materialization sequence within 12 bytes; decoded MMIO equivalence and source admission pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-distance-noise-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'])
