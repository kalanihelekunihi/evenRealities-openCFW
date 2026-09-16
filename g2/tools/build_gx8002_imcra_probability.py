# SPDX-License-Identifier: MIT
"""Native macOS build of a development-only IMCRA smooth block."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-imcra-probability';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_imcra_probability.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'power.o')],check=True)
    (out/'power.ld').write_text('SECTIONS { .power 0x10016228 : { *(.text*) } }\n')
    path=out/'power.elf'
    subprocess.run([pre+'ld','-T',str(out/'power.ld'),str(out/'power.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'power');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    (out/'power.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'bytes':sections[0]['size'],'source_admitted':False,'startup_integrated':False,'limits':['Standalone processing block only; no placement or full processing replacement.', 'Positive bins; finite in-range float-to-uint conversion; target symbolic reciprocal instruction.', 'Decoded numeric verification and hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-imcra-probability.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(build())
