# SPDX-License-Identifier: MIT
"""Build typed keyword-list accessor bound to existing source-owned state."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';upstream={}
    for rel in ('lvp/vui/kws/max_decoder.c','include/lvp_param.h','include/driver/gx_audio_in.h','include/driver/gx_audio_in/gx_audio_in_v2.h','include/driver/gx_padmux.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();upstream[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    out=ROOT/'build/gx8002-keyword-list-get';out.mkdir(parents=True,exist_ok=True);(out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n');source=ROOT/'components/shared/gx8002/runtime_gx8002_keyword_list_get.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-I'+str(out),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(out/'get.o')],check=True)
    (out/'get.ld').write_text('SECTIONS { .text 0x100264dc : { *(.text*) } }\nopen_cfw_gx8002_max_keyword_list = 0x2002e79c;\n');path=out/'get.elf';subprocess.run([pre+'ld','-T',str(out/'get.ld'),str(out/'get.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'getter');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==1;s=allocated[0];body=elf.contents(s);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert s['address']==0x100264dc and len(body)==8 and body==stock[0x184f0:0x184f8]
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    return {'sdk_commit':SDK_COMMIT,'upstream':upstream,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'compiled_bytes':8,'compiled_sha256':sha(body),'package_offset':0x184f0,'runtime_address':0x100264dc,'state_address':0x2002e79c,'source_admitted':False,'limits':['Byte-exact typed accessor, no duplicate state allocation. Existing list-owner binding and symbolic return qualification pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-keyword-list-get-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Keyword-list accessor compiled:',r['compiled_bytes'])
