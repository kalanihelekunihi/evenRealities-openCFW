# SPDX-License-Identifier: MIT
"""Build the complete C power forwarding wrapper, excluding unrelated wrappers."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-power-wrapper';out.mkdir(exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_math_wrappers.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-DOPEN_CFW_POWER_ONLY','-fno-optimize-sibling-calls','-c',str(source),'-o',str(out/'wrapper.o')],check=True)
    (out/'wrapper.ld').write_text('SECTIONS { .power_wrapper 0x100100a4 : { *(.text.open_cfw_gx8002_powf) } /DISCARD/ : { *(.text.open_cfw_gx8002_logf) *(.text.open_cfw_gx8002_expf) } }\n__ieee754_powf = 0x100100bc;\n')
    path=out/'wrapper.elf';subprocess.run([pre+'ld','-T',str(out/'wrapper.ld'),str(out/'wrapper.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrapper');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    body=elf.contents(allocated[0]);assert body==stock[0x489e4:0x489ec]
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    report={'source_sha256':sha(source.read_bytes()),'bytes':len(body),'exact_stock':True,'source_admitted':False,'limits':['Complete wrapper byte-identical; power core binding must resolve to source during integration.']}
    (ROOT/'docs/research/gx8002-backup-power-wrapper.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
