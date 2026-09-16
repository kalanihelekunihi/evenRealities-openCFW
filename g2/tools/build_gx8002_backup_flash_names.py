# SPDX-License-Identifier: MIT
"""Build backup device names with pinned SDK provenance and stock references."""
import json,struct,subprocess
from verify_gx8002_flash_device_names import verify as primary_verify
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
ROWS=[('p25q21l',0x10012e38,0x854012),('p25q40l',0x10012e40,0x856013),('p25q80l',0x10012e48,0x856014),('en25s20a',0x10012e50,0x1c3812),('en25s40a',0x10012e5c,0x1c3813),('zb25wq80a',0x10012e68,0x5e3414)]

def build():
    provenance=primary_verify();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-flash-names';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_device_names.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(source),'-o',str(out/'names.o')],check=True)
    (out/'names.ld').write_text('SECTIONS {\n'+''.join(f'.flash_name_{name} {address:#x} : {{ *(.rodata.open_cfw_gx8002_flash_name_{name}) }}\n' for name,address,_ in ROWS)+'}\n')
    path=out/'names.elf';subprocess.run([pre+'ld','-T',str(out/'names.ld'),str(out/'names.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'names');sections=[]
    for i,(name,address,jedec) in enumerate(ROWS):
        sec=next(s for s in elf.sections if s['name']=='.flash_name_'+name);payload=elf.contents(sec);offset=address-0x10000000+0x38940
        assert payload==name.encode()+b'\0' and payload==stock[offset:offset+len(payload)]
        assert sec['address']==address and not elf.relocations(sec['index'])
        assert struct.unpack_from('<II',stock,0x4f7e4+i*24)==(address,jedec)
        sections.append({'name':name,'address':address,'bytes':len(payload),'sha256':sha(payload),'package_offset':offset})
    report={'source_sha256':sha(source.read_bytes()),'sdk_commit':provenance['sdk_commit'],'sdk_object_git_blob':provenance['sdk_object_git_blob'],'sections':sections,'source_admitted':False,'hardware_qualified':False,'limits':['Labels and record references only; descriptor offset12 remains unresolved. No whole-table source completion claim.']}
    (ROOT/'docs/research/gx8002-backup-flash-names.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
