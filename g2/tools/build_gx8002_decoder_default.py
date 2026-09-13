# SPDX-License-Identifier: MIT
"""Build initialized decoder state using the pinned upstream state enum."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from build_transparent_image import Elf32


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-decoder-default';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_decoder_default.c';prefix=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    subprocess.run([prefix+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-Wall','-Wextra','-Werror','-I'+str(out),'-MMD','-MF',str(out/'defaults.d'),'-I'+str(sdk/'lvp/vui/kws'),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(out/'defaults.o')],check=True)
    deps=(out/'defaults.d').read_text().replace('\\\n',' ').split(':',1)[1].split();headers={}
    for name in deps:
        path=source.__class__(name)
        if path==source:continue
        if path==out/'autoconf.h':
            headers['generated/autoconf.h']={'sha256':sha(path.read_bytes())};continue
        rel=str(path.relative_to(sdk));blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        headers[rel]={'blob':blob,'sha256':sha(authenticated_blob(path,blob))}
    rel='lvp/vui/kws/max_decoder.c';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();upstream=authenticated_blob(sdk/rel,blob);assert b'static VUI_KWS_STATE s_state = VUI_KWS_ACTIVE_STATE;' in upstream
    (out/'defaults.ld').write_text('SECTIONS { .decoder_state 0x20026d2c : { *(.data.decoder_state) } }\n')
    path=out/'defaults.elf';subprocess.run([prefix+'ld','-T',str(out/'defaults.ld'),str(out/'defaults.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'decoder');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==1
    section=sections[0];body=elf.contents(section);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert section['address']==0x20026d2c and section['flags']==3 and len(body)==4 and body==stock[0x18d40:0x18d44]
    assert not elf.relocations(section['index']) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    return {'source_sha256':sha(source.read_bytes()),'sdk_commit':SDK_COMMIT,'headers':headers,'upstream_initializer':{'path':rel,'blob':blob,'sha256':sha(upstream)},'elf_sha256':sha(path.read_bytes()),'compiled_sha256':sha(body),'bytes':4,'package_offset':0x18d40,'runtime_address':section['address'],'source_admitted':False,'limits':['Typed int storage matches existing consumer declaration; initializer uses authenticated upstream enum and agrees with upstream active-state default.','Startup, consumer and ownership qualification remain pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-decoder-default-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Decoder default: 4 bytes exact from upstream enum')
