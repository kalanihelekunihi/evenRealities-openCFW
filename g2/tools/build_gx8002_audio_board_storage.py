# SPDX-License-Identifier: MIT
"""Compile typed audio board defaults; binary used only as a verification oracle."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'; upstream={}
    for rel in ('include/lvp_param.h','include/driver/gx_audio_in.h','include/driver/gx_audio_in/gx_audio_in_v2.h','include/driver/gx_padmux.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        upstream[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    out=ROOT/'build/gx8002-audio-board-storage';out.mkdir(parents=True,exist_ok=True)
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_board_storage.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(out),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(out/'storage.o')],check=True)
    (out/'storage.ld').write_text('SECTIONS { .board 0x200269a4 : { *(.data.open_cfw_audio_board_state) } }\n')
    path=out/'storage.elf'
    subprocess.run([pre+'ld','-T',str(out/'storage.ld'),str(out/'storage.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'audio board');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1
    section=sections[0];data=elf.contents(section)
    assert (section['address'],section['size'],section['flags'])==(0x200269a4,240,3)
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert data==stock[0x189b8:0x18aa8], 'Typed audio defaults differ from stock'
    return {'sdk_commit':SDK_COMMIT,'upstream':upstream,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'compiled_sha256':sha(data),'compiled_bytes':240,'package_offset':0x189b8,'runtime_address':0x200269a4,'source_admitted':False,'hardware_qualified':False,'findings':['All 240 bytes reconstructed through named SDK fields and enums, with no binary input to compilation or linking.','PDM input, stereo PDM track, 12dB rough gain, DC removal, PCM1 and logfbank outputs; remaining defaults explicitly typed or zero initialized.'],'limits':['Exact data and ABI agreement; startup, consumer composition and source registry admission remain to be qualified.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-board-storage-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Typed audio board defaults:',r['compiled_bytes'])
