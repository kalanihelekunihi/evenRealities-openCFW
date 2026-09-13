# SPDX-License-Identifier: MIT
"""Load compiled backup platform setter and switch table through the normal loader."""
import json,subprocess
from build_gx8002_backup_platform_config_preserved import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_backup_memset_loader import execute
from build_gx8002_backup_platform_literals import build as literals
from verify_gx8002_memcpy_source import decode
from build_gx8002_backup_flash_otp_configuration import build as otp


def verify():
    evidence={'setter':build(),'literals':literals(),'otp':otp()};stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    image=bytearray(stock);patches=[];occupied=set()
    targets=[(ROOT/'build/gx8002-backup-platform-config/preserved.elf',
              {'.text.entry':(0x1001574c,4),'.text.platform_config':(0x10015768,200),'.rodata.platform_config':(0x10012a3c,40)}),
             (ROOT/'build/gx8002-backup-platform-literals/literals.elf',
              {'.shared_literals':(0x10015758,16),'.otp_error':(0x10012a8c,22),'.otp_model':(0x10012aa4,6)}),
             (ROOT/'build/gx8002-backup-flash-otp-configuration/configuration.elf',
              {'.text':(0x100156d4,120)})]
    for path,expected in targets:
        elf=Elf32(path.read_bytes(),str(path));sections=[s for s in elf.sections if s['flags']&2 and s['size']]
        assert len(sections)==len(expected)
        for section in sections:
            address,size=expected[section['name']];assert (section['address'],section['size'])==(address,size)
            assert not elf.relocations(section['index'])
            offset=address-(0x20003000 if address>=0x20000000 else 0x10003000)+0x3b940
            span=set(range(offset,offset+size));assert not span&occupied;occupied|=span
            payload=elf.contents(section);image[offset:offset+size]=payload
            patches.append({'section':section['name'],'address':address,'offset':offset,'bytes':size,'sha256':sha(payload)})
    # The OTP section's final literal occupies the old two-byte alignment.
    # This proves boundary placement, not absence of external computed entries.
    assert stock[0x4e08a:0x4e08c]==b'\0\0'
    assert image[0x4e088:0x4e08c]==(0x10012a8c).to_bytes(4,'little')
    assert next(p for p in patches if p['section']=='.text')['offset']+120==0x4e08c
    assert image[0x4e090:0x4e0a8]==stock[0x4e090:0x4e0a8]
    assert all(a==b for i,(a,b) in enumerate(zip(stock,image)) if i not in occupied)
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x396a0','--stop-address=0x396ee',str(path)],text=True))
    cases=0
    for mode in (0,1,0xffffffff,0xaabbccdc):
      for seed in (0,91,0xffffffff):
        result,calls,memory=execute(code,bytes(image),mode,seed)
        loaded=b''.join(memory[a].to_bytes(4,'little') for a in range(0x10003000,0x1001708c,4))
        assert result==0 and loaded==image[0x3b940:0x4f9cc]
        cases+=1
    report={'build':evidence,'patches':patches,'replacement_bytes':len(occupied),'loader_cases':cases,
            'candidate_image_sha256':sha(bytes(image)),'source_admitted':False,'hardware_qualified':False,
            'limits':['Combined normal backup-loader placement, with no replacement fill and unrelated bytes unchanged.',
                      'Source-authored literals and text retain original values and addresses; consumer behavior and reference admission remain separate.']}
    (ROOT/'docs/research/gx8002-backup-otp-platform-loader.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    r=verify();print(r['loader_cases'],'combined loader cases;',r['replacement_bytes'],'source bytes')
