# SPDX-License-Identifier: MIT
"""Native macOS cross-build of the recovered audio completion forwarding wrapper."""
import json,subprocess
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob


def build(extra_flags=()):
    out=ROOT/'build/gx8002-board';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_completion_forward.c'
    flags=['-Os',*FLAGS[1:],'-fno-shrink-wrap','-fira-algorithm=priority',*extra_flags]
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='include/driver/gx_snpu.h'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    header=authenticated_blob(sdk/rel,blob)
    config=out/'audio-completion-config';config.mkdir(exist_ok=True);(config/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    subprocess.run([pre+'gcc',*flags,'-I'+str(config),'-I'+str(sdk/'include'),'-c',str(source),'-o',str(out/'audio-completion-forward.o')],check=True)
    script=out/'audio-completion-forward.ld';script.write_text('SECTIONS { .text 0x100260d0 : { *(.text.open_cfw_gx8002_audio_completion_forward) } }\nopen_cfw_gx8002_audio_completion_callback = 0x20027b50;\n')
    path=out/'audio-completion-forward.elf'
    subprocess.run([pre+'ld','-T',str(script),str(out/'audio-completion-forward.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),str(path));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    assert sha(IMAGE.read_bytes())==IMAGE_SHA and not elf.relocations(section['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert {s['name'] for s in elf.sections if s['size'] and s['flags']&2}=={'.text'}
    (out/'audio-completion-forward.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'sdk_commit':SDK_COMMIT,'header':{'path':rel,'blob':blob,'sha256':sha(header)},'config_sha256':sha((config/'autoconf.h').read_bytes()),'flags':flags,'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(data),'compiled_sha256':sha(data),'package_offset':0x180e4,'envelope_bytes':20,'fits':len(data)<=20,'source_admitted':False,'limits':['Build-only reconstruction; decoded behavior and caller integration pending. Original external literal must not remain an opaque placement dependency.']}
    (ROOT/'docs/research/gx8002-audio-completion-forward-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
