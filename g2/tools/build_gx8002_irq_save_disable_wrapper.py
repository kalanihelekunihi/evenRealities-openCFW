# SPDX-License-Identifier: MIT
"""Compile the retained IRQ save/disable forwarding entry on native macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-irq-save-disable-wrapper';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_irq_save_disable_wrapper.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-fno-optimize-sibling-calls','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'wrapper.o')],check=True)
    (out/'wrapper.ld').write_text('SECTIONS { .text 0x10025534 : { *(.text*) } }\nopen_cfw_gx8002_irq_save_disable = 0x1002550c;\n');path=out/'wrapper.elf';subprocess.run([pre+'ld','-T',str(out/'wrapper.ld'),str(out/'wrapper.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrapper');sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==1;s=sections[0];body=elf.contents(s);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert s['address']==0x10025534 and len(body)==8 and body==stock[0x17548:0x17550]
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    return {'source_sha256':sha(source.read_bytes()),'compiled_bytes':8,'compiled_sha256':sha(body),'elf_sha256':sha(path.read_bytes()),'package_offset':0x17548,'runtime_address':0x10025534,'callee_address':0x1002550c,'source_admitted':False,'limits':['Byte-exact source wrapper; original public function name not established. Registered callee binding and composed execution pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-irq-save-disable-wrapper-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('IRQ wrapper compiled:',r['compiled_bytes'])
