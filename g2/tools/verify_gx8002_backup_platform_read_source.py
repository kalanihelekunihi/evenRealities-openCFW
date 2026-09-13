# SPDX-License-Identifier: MIT
"""Admit reconstructed backup platform getter code within documented finite model scope."""
import json,shutil
from pathlib import Path
from verify_gx8002_logging import check_paths
from verify_gx8002_backup_platform_read_loader import verify as loader
from compare_gx8002_backup_platform_read import verify as behavior
from analyze_gx8002_backup_platform_read_references import analyze as references
from build_gx8002_backup_platform_read import ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'loader':loader(),'references':references()}
    checks['behavior']=behavior()
    assert checks['behavior']['cases']==504 and checks['behavior']['relocated_record_cases']==33
    path=ROOT/'build/gx8002-backup-platform-read/platform-read.elf'
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    elf=Elf32(path.read_bytes(),'backup platform getter');alloc=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(alloc)==2
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    rows=[]
    for name,address,size,kind,symbol in (
        ('.text.platform_read',0x10003edc,188,'compiled_c','open_cfw_gx8002_platform_read'),
        ('.rodata.platform_read',0x10012a64,40,'generated_source_data','open_cfw_gx8002_platform_read_switch')):
        section=next(s for s in alloc if s['name']==name);body=elf.contents(section)
        assert (section['address'],len(body))==(address,size)
        assert bool(section['flags']&4)==(kind=='compiled_c')
        offset=address-0x10003000+0x3b940
        patch=next(r for r in checks['loader']['patches'] if r['section']==name)
        assert (patch['offset'],patch['bytes'],patch['sha256'])==(offset,size,sha(body))
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':size,
                     'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,
                     'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_b_sram_text'}]})
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'platform-read.elf')
    files=('verify_gx8002_backup_platform_read_source.py','build_gx8002_backup_platform_read.py',
           'compare_gx8002_backup_platform_read.py','verify_gx8002_backup_platform_read_loader.py',
           'analyze_gx8002_backup_platform_read_references.py','verify_gx8002_backup_memset_loader.py',
           'verify_gx8002_memcpy_source.py')
    return {'functions':rows,'checks':checks,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Recovered C with readable narrow-store assembly preserves access ordering; 32-byte original tail retained without fill.',
                      '537 finite stock/source cases with ordered MMIO/output oracle and ABI checks; physical hardware and timing unqualified.',
                      'Observed direct references and stored switch pointers checked; arbitrary computed entry closure is not globally proven.',
                      'Cached low-bit state remains at 0x20017398; this gate admits the getter, not its retained setter or BSS storage. Experimental hybrid admission only.']}


if __name__=='__main__':
    report=verify(output=ROOT/'build/gx8002-source-candidate/backup-platform-read')
    assert json.loads(json.dumps(report))==report
    (ROOT/'docs/research/gx8002-backup-platform-read-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Backup platform getter admitted: 188 C + 40 generated table bytes; hardware unqualified')
