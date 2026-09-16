# SPDX-License-Identifier: MIT
"""Build original-address beam spectrum entry from C on macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-beam-spectrums-entry';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_beam_spectrums_entry.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'entry.o')],check=True)
    (out/'entry.ld').write_text('SECTIONS { .beam_spectrums_entry 0x1000de94 : { *(.text*) } }\nopen_cfw_gx8002_beam_spectrums = 0x1000d2a4;\n')
    target=out/'entry.elf';subprocess.run([pre+'ld','-T',str(out/'entry.ld'),str(out/'entry.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),'entry');section=next(s for s in elf.sections if s['name']=='.beam_spectrums_entry');body=elf.contents(section)
    assert len(body)<=12 and body==stock[0x467d4:0x467d4+len(body)]
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    report={'source_sha256':sha(source.read_bytes()),'bytes':len(body),'exact_stock_code':True,'source_admitted':False,'limits':['Identical relative-call wrapper code; source core must be linked at its assigned address. No complete beamforming or hardware qualification.']}
    (ROOT/'docs/research/gx8002-beam-spectrums-entry.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
