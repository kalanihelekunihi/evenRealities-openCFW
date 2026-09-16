# SPDX-License-Identifier: MIT
"""Native macOS build of the reconstructed top-level DRC initializer."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    assert sha(IMAGE.read_bytes()) == IMAGE_SHA
    out = ROOT / 'build/gx8002-drc-initialize'; out.mkdir(exist_ok=True)
    source = ROOT / 'components/shared/gx8002/runtime_gx8002_drc_initialize.c'
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    bindings = {
        'open_cfw_gx8002_memset':0x100113c4,
        'open_cfw_gx8002_drc_stage1_initialize':0x1000ea74,
        'open_cfw_gx8002_drc_stage2_initialize':0x1000eb54,
        'open_cfw_gx8002_drc_stage3_initialize':0x1000ec38,
        'open_cfw_gx8002_drc_stage4_initialize':0x1000ed7c,
        'open_cfw_gx8002_drc_stage4_set_gain':0x1000ed2c,
    }
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'spectrums.o')], check=True)
    script = '''SECTIONS {
      .drc_initialize 0x1000e784 : { *(.drc_initialize) }
      .drc_stage1_size 0x1000ea68 : { *(.drc_stage1_size) }
      .drc_stage2_size 0x1000eb48 : { *(.drc_stage2_size) }
      .drc_stage3_size 0x1000ec2c : { *(.drc_stage3_size) }
      .drc_parameters 0x20016fb8 : { *(.drc_parameters) }
      .drc_stage1_control 0x2002d7b4 (NOLOAD) : { *(.drc_stage1_control) }
    }
'''+''.join(f'{n} = 0x{a:x};\n' for n,a in bindings.items())
    (out/'spectrums.ld').write_text(script)
    target=out/'spectrums.elf'
    subprocess.run([pre+'ld','-T',str(out/'spectrums.ld'),str(out/'spectrums.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),'beam')
    (out/'spectrums.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    report={'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(target.read_bytes()),'sections':[(s['name'],hex(s['address']),s['size']) for s in sections], 'helper_bindings':bindings,'source_admitted':False,'limits':['Development reconstruction; decoded behavioral comparison pending.','No full-image, hardware or arbitrary-state qualification.']}
    (ROOT/'docs/research/gx8002-drc-initialize.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__': print(build())
