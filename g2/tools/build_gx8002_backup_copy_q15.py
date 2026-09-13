# SPDX-License-Identifier: MIT
"""Compile the recovered Q15 copy helper with native macOS C-SKY tools."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-copy-q15';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_copy_q15.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-c',str(source),'-o',str(out/'copy.o')],check=True)
    address=0x47ac0-0x3b940+0x10003000
    (out/'copy.ld').write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text*) }} }}\n')
    path=out/'copy.elf';subprocess.run([pre+'ld','-T',str(out/'copy.ld'),str(out/'copy.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'copy');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['name']=='.text'
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['section']==0 and s['name'] for s in elf.symbols())
    body=elf.contents(sections[0]);(out/'copy.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'extra_flags':['-fno-tree-loop-optimize'],'source_sha256':sha(source.read_bytes()),'stock_sha256':IMAGE_SHA,'compiled_bytes':len(body),'stock_bytes':44,'fits':len(body)<=44,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Standalone candidate. Store trace, decoded behavior and placement qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-copy-q15-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
