# SPDX-License-Identifier: MIT
"""Compile symbolic denoise diagnostics, compare text, and enforce placement."""
import json,subprocess
from build_gx8002_backup_denoise_initialize import build as initialize_build,ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA


def build():
    evidence=initialize_build();out=ROOT/'build/gx8002-backup-denoise-messages';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_denoise_messages.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-c',str(source),'-o',str(out/'messages.o')],check=True)
    placements={name:address for name,address in evidence['bindings'].items() if name.startswith('denoise_msg_')}
    ld='SECTIONS {\n'+''.join(f'.{name} {address:#x} : {{ *(.denoise_msg.{name[12:]}) }}\n' for name,address in placements.items())+'}\n'
    (out/'messages.ld').write_text(ld);path=out/'messages.elf';subprocess.run([pre+'ld','-T',str(out/'messages.ld'),str(out/'messages.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'messages');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==12
    rows=[]
    for name,address in placements.items():
        sec=next(s for s in alloc if s['name']=='.'+name);body=elf.contents(sec);offset=address-0x10000000+0x38940
        assert sec['address']==address and body==stock[offset:offset+len(body)] and body.endswith(b'\0')
        rows.append({'name':name,'address':address,'bytes':len(body),'sha256':sha(body)})
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    report={'source_sha256':sha(source.read_bytes()),'messages':rows,'source_admitted':False,'limits':['C literals supply output; original firmware used only for comparison. No executable dependency closed by this data component alone.']}
    (ROOT/'docs/research/gx8002-backup-denoise-messages.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(sum(row['bytes'] for row in build()['messages']))
