# SPDX-License-Identifier: MIT
"""Place reconstructed setter after preceding routine's shared literal pool."""
import json,subprocess
from build_gx8002_backup_platform_config import build as candidate,ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    evidence=candidate();out=ROOT/'build/gx8002-backup-platform-config';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    (out/'entry.S').write_text(''' .section .text.entry,"ax",@progbits
.global open_cfw_gx8002_platform_config_entry
open_cfw_gx8002_platform_config_entry:
    br open_cfw_gx8002_platform_config
''')
    subprocess.run([pre+'gcc','-mcpu=ck804ef','-mhard-float','-c',str(out/'entry.S'),'-o',str(out/'entry.o')],check=True)
    (out/'preserved.ld').write_text('''SECTIONS {
.text.entry 0x1001574c : { *(.text.entry) }
.text.platform_config 0x10015768 : { *(.text.open_cfw_gx8002_platform_config) }
.rodata.platform_config 0x10012a3c : { *(.rodata.open_cfw_gx8002_platform_config) }
}
''')
    path=out/'preserved.elf'
    subprocess.run([pre+'ld','-T',str(out/'preserved.ld'),str(out/'entry.o'),str(out/'config.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'preserved setter');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for s in elf.sections:
        if not s['size'] or not s['flags']&2:continue
        assert not elf.relocations(s['index'])
        offset=s['address']-0x10003000+0x3b940
        assert not (offset<0x4e0a8 and offset+s['size']>0x4e098)
        assert offset+s['size']<=0x4e170
        rows.append({'section':s['name'],'address':s['address'],'offset':offset,'bytes':s['size'],'sha256':sha(elf.contents(s))})
    (out/'preserved.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'candidate':evidence,'sections':rows,'retained_shared_pool':[0x4e098,0x4e0a8],
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Placement candidate only; entry branch, relocated switch/body and preceding consumer require verification. Shared literals are retained, not claimed as reconstructed source.']}
    (ROOT/'docs/research/gx8002-backup-platform-config-preserved.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(build(),indent=2))
