# SPDX-License-Identifier: MIT
"""Reconstruct shared semantic pointers and flash identification text."""
import json,subprocess
from build_gx8002_backup_platform_config import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build():
    out=ROOT/'build/gx8002-backup-platform-literals';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_platform_literals.c'
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(source),'-o',str(out/'literals.o')],check=True)
    (out/'literals.ld').write_text('''SECTIONS {
.shared_literals 0x10015758 : { *(.shared_literals) }
.otp_error 0x10012a8c : { *(.otp_error) }
.otp_model 0x10012aa4 : { *(.otp_model) }
}
open_cfw_gx8002_backup_flash_probe_slot = 0x20016d80;
open_cfw_gx8002_backup_platform_dispatch = 0x10012a3c;
''')
    path=out/'literals.elf'
    subprocess.run([pre+'ld','-T',str(out/'literals.ld'),str(out/'literals.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'shared literals');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for s in elf.sections:
        if not s['flags']&2 or not s['size']:continue
        assert not s['flags']&4 and not elf.relocations(s['index'])
        offset=s['address']-0x10003000+0x3b940;body=elf.contents(s)
        assert body==stock[offset:offset+len(body)]
        rows.append({'section':s['name'],'offset':offset,'bytes':len(body),'sha256':sha(body)})
    assert len(rows)==3
    report={'source_sha256':sha(source.read_bytes()),'sections':rows,'source_admitted':False,
            'limits':['Exact source-authored text and symbolic pointers. Consumer and provider qualification, reference census and loader integration remain separate.']}
    (ROOT/'docs/research/gx8002-backup-platform-literals-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
