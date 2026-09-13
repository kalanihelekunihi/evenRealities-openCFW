# SPDX-License-Identifier: MIT
"""Compile the recovered Q15 shift helper with native macOS C-SKY tools."""
import json,subprocess
from verify_gx8002_memcpy_source import decode
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build():
    assert sha(IMAGE.read_bytes())==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-shift-q15';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_shift_q15.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-c',str(source),'-o',str(out/'shift.o')],check=True)
    address=0x47a00-0x3b940+0x10003000
    (out/'shift.ld').write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text.open_cfw_gx8002_backup_shift_q15) *(.text*) }} }}\n')
    path=out/'shift.elf';subprocess.run([pre+'ld','-T',str(out/'shift.ld'),str(out/'shift.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'shift');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['name']=='.text'
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['section']==0 and s['name'] for s in elf.symbols())
    body=elf.contents(sections[0]);(out/'shift.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    entry=next(s['value'] for s in elf.symbols() if s['name']=='open_cfw_gx8002_backup_shift_q15')
    assert entry==address
    code=decode((out/'shift.disassembly.txt').read_text());calls=[]
    for pc,(op,args,width) in code.items():
        if op=='bsr':
            target=int(args,0);assert target in code and address<=target<address+len(body)
            calls.append({'pc':pc,'target':target})
    assert calls
    report={'direct_calls':calls,'entry':entry,'linked_section_address':address,'extra_flags':['-fno-tree-loop-optimize'],'source_sha256':sha(source.read_bytes()),'stock_sha256':IMAGE_SHA,'compiled_bytes':len(body),'stock_bytes':116,'fits':len(body)<=116,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Standalone candidate. Store trace, decoded behavior and placement qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-shift-q15-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
