# SPDX-License-Identifier: MIT
"""Native macOS build of the backup IMCRA workspace sizing."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-imcra-workspace';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_imcra_workspace.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'index.o')],check=True)
    (out/'index.ld').write_text('SECTIONS { .imcra_workspace 0x1000e314 : { *(.text*) } }\n\n')
    path=out/'index.elf';subprocess.run([pre+'ld','-T',str(out/'index.ld'),str(out/'index.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'index');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    body=elf.contents(allocated[0]);assert len(body)<=112
    (out/'index.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'bytes':len(body),'envelope_bytes':112,'fits':len(body)<=112,'exact_stock':body==stock[0x46c54:0x46cc4],'source_admitted':False,'limits':['Partial state fields only; complete algorithm and buffer ownership are not established.']}
    (ROOT/'docs/research/gx8002-backup-imcra-workspace.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
