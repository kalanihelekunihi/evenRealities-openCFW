# SPDX-License-Identifier: MIT
"""Compile source board pin policy, diagnostics and reset-cleared state."""
import json,subprocess
from build_gx8002_backup_padmux import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
ROWS=[('pins',0x10012ecc,26),('conflict',0x10012ee8,28),('fatal',0x10012f04,49),('error',0x10012f38,19),('initialized',0x200176d8,4)]
def build():
    out=ROOT/'build/gx8002-backup-board-pin-data';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_board_pin_data.c'
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(source),'-o',str(out/'data.o')],check=True)
    script='SECTIONS {\n'
    for name,address,size in ROWS:
        section='bss' if name=='initialized' else 'rodata'
        script+=f'.{section}.board_{name} {address:#x} : {{ *(.{section}.open_cfw_gx8002_backup_board_{name}) }}\n'
    script+='}\n';(out/'data.ld').write_text(script)
    subprocess.run([pre+'ld','-T',str(out/'data.ld'),str(out/'data.o'),'-o',str(out/'data.elf')],check=True)
    elf=Elf32((out/'data.elf').read_bytes(),'board data');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,address,size in ROWS:
        section=next(s for s in elf.sections if s['name'].endswith('.board_'+name));assert section['size']==size and section['address']==address
        if name=='initialized':assert section['type']==8 and 0x20017090<=address and address+size<=0x2002d79c
        else:assert elf.contents(section)==stock[address-0x10000000+0x38940:address-0x10000000+0x38940+size]
        rows.append({'name':name,'address':address,'bytes':size,'reset_bss':name=='initialized'})
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    report={'source_sha256':sha(source.read_bytes()),'stock_sha256':IMAGE_SHA,'rows':rows,'source_admitted':False,'limits':['Source policy/literals match stock; flag relies on separately reconstructed reset BSS clearing.']}
    (ROOT/'docs/research/gx8002-backup-board-pin-data.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build()['rows'])
