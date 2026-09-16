# SPDX-License-Identifier: MIT
"""Native macOS development build of reconstructed DRC stage initialization."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    out=ROOT/'build/gx8002-drc-stage4-initialize';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_drc_stage4_initialize.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    bindings={'open_cfw_gx8002_memset':0x100113c4,'drc_logf':0x100100ac,'open_cfw_gx8002_powf':0x100100a4,'open_cfw_gx8002_backup_exp':0x1000f84c,'__extendsfdf2':0x10011af4,'__truncdfsf2':0x10012398}
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'spectrums.o')],check=True)
    script='SECTIONS { .drc_stage4_initialize 0x1000ed7c : { *(.text*) } }\n'
    script+=''.join(f'{name} = 0x{address:x};\n' for name,address in bindings.items())
    (out/'spectrums.ld').write_text(script)
    target=out/'spectrums.elf'
    subprocess.run([pre+'ld','-T',str(out/'spectrums.ld'),str(out/'spectrums.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),'beam');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'spectrums.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(target.read_bytes()),'bytes':sections[0]['size'],'envelope_bytes':232,'fits':sections[0]['size']<=232,'helper_bindings':bindings,'source_admitted':False,'limits':['Development reconstruction; decoded behavioral comparison pending.','Log/power/double-exp/conversion/memset dependencies remain standalone absolute bindings; no composed source closure.','No startup or full-image integration, hardware or arbitrary-state qualification.']}
    (ROOT/'docs/research/gx8002-drc-stage4-initialize.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(build())
