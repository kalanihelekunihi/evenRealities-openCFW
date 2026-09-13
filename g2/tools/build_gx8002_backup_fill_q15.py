# SPDX-License-Identifier: MIT
"""Compile the recovered Q15 fill helper with native macOS C-SKY tools."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-fill-q15';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_fill_q15.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-tree-scev-cprop','-c',str(source),'-o',str(out/'fill.o')],check=True)
    address=0x47aec-0x3b940+0x10003000
    (out/'fill.ld').write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text*) }} }}\n')
    path=out/'fill.elf';subprocess.run([pre+'ld','-T',str(out/'fill.ld'),str(out/'fill.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'fill');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['name']=='.text'
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['section']==0 and s['name'] for s in elf.symbols())
    body=elf.contents(sections[0]);(out/'fill.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'extra_flags':['-fno-tree-scev-cprop'],'source_sha256':sha(source.read_bytes()),'stock_sha256':IMAGE_SHA,'compiled_bytes':len(body),'stock_bytes':40,'fits':len(body)<=40,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Standalone candidate. Store trace, decoded behavior and placement qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-fill-q15-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
