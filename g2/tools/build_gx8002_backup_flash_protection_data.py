# SPDX-License-Identifier: MIT
"""Build named protection policies and reset-cleared profile storage."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
ROWS=[('256k',0x20016dfc,5),('512k',0x20016e24,7),('1024k',0x20016e5c,9)]
def build():
    out=ROOT/'build/gx8002-backup-flash-protection-data';out.mkdir(parents=True,exist_ok=True);base=ROOT/'components/shared/gx8002';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    sources={'tables':'runtime_gx8002_flash_protection_tables.c','profiles':'runtime_gx8002_backup_flash_protection_profiles.c'}
    for name,src in sources.items():subprocess.run([pre+'gcc',*FLAGS,'-c',str(base/src),'-o',str(out/(name+'.o'))],check=True)
    script='SECTIONS {\n'+''.join(f'.flash_protect_{name} {address:#x} : {{ *(.rodata.open_cfw_gx8002_flash_protection_{name}) }}\n' for name,address,count in ROWS)+'.flash_protect_profiles 0x20017644 (NOLOAD) : { *(.bss.open_cfw_gx8002_flash_protection_profiles) }\n}\n'
    (out/'data.ld').write_text(script);path=out/'data.elf';subprocess.run([pre+'ld','-T',str(out/'data.ld'),str(out/'tables.o'),str(out/'profiles.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'protection');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;sections=[]
    for name,address,count in ROWS:
        sec=next(s for s in elf.sections if s['name']=='.flash_protect_'+name);payload=elf.contents(sec);offset=address-0x20000000+0x38940
        assert sec['address']==address and len(payload)==count*8 and not elf.relocations(sec['index']) and payload==stock[offset:offset+len(payload)]
        sections.append({'name':name,'address':address,'bytes':len(payload),'sha256':sha(payload),'package_offset':offset,'byte_exact':True})
    profiles=next(s for s in elf.sections if s['name']=='.flash_protect_profiles');assert profiles['type']==8 and profiles['size']==24 and profiles['address']==0x20017644 and 0x20017090<=profiles['address']<profiles['address']+24<=0x2002d79c
    report={'source_sha256':{n:sha((base/f).read_bytes()) for n,f in sources.items()},'header_sha256':sha((base/'runtime_gx8002_flash_protection_tables.h').read_bytes()),'sections':sections,'profiles':{'address':profiles['address'],'bytes':24,'kind':'reset-cleared NOBITS'},'source_admitted':False,'hardware_qualified':False,'limits':['Named status mask/value and protected-prefix policies match stock; hardware protection behavior remains unqualified.']}
    (ROOT/'docs/research/gx8002-backup-flash-protection-data.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
