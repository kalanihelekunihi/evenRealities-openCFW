# SPDX-License-Identifier: MIT
"""Experimental source admission for the recovered RFFT dispatcher only."""
import json,shutil
from pathlib import Path
from verify_gx8002_logging import check_paths
from verify_gx8002_backup_rfft import verify as behavior
from verify_gx8002_backup_rfft_mutation import verify as mutation
from verify_gx8002_backup_rfft_loader import verify as loader
from analyze_gx8002_backup_rfft_references import analyze as references
from build_gx8002_backup_rfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'behavior':behavior(),'mutation':mutation(),'loader':loader(),'references':references()}
    assert checks['behavior']['cases']==216 and checks['mutation']['cases']==126
    assert checks['loader']['loader_cases']==12 and checks['references']['reference_ready']
    path=ROOT/'build/gx8002-backup-rfft/rfft.elf';elf=Elf32(path.read_bytes(),'RFFT dispatcher')
    allocated=[s for s in elf.sections if s['size'] and s['flags']&2]
    assert len(allocated)==1
    section=allocated[0];body=elf.contents(section)
    assert section['name']=='.text' and section['address']==0x1000ef64 and len(body)==110 and section['flags']&4
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert checks['loader']['patches'][0]['sha256']==sha(body)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_backup_rfft'
    row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':110,'compiled_sha256':sha(body),
         'stock_occurrences':[{'symbol':symbol,'package_offset':0x478a4,'bytes':110,'sha256':sha(stock[0x478a4:0x47912]),'region':'image_b_sram_text'}]}
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'rfft.elf')
    files=('verify_gx8002_backup_rfft_source.py','build_gx8002_backup_rfft.py','build_gx8002_backup_fft_descriptors.py',
           'verify_gx8002_backup_rfft.py','verify_gx8002_backup_rfft_mutation.py','verify_gx8002_backup_rfft_loader.py',
           'analyze_gx8002_backup_rfft_references.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Dispatcher only: three transform helpers remain retained. Their arithmetic is not qualified by modeled calls.',
                      'Finite descriptor/output trace and mutation scenarios; valid nonoverlapping buffers, bounded lengths. Not exhaustive numeric or concurrency proof.',
                      'Four direct entry references checked; one false literal reference identified. Global computed-entry closure is not proven.',
                      'Original two-byte alignment remains retained. Experimental hybrid replacement, not complete source-only firmware.']}
if __name__=='__main__':
    r=verify(output=ROOT/'build/gx8002-source-candidate/backup-rfft')
    assert json.loads(json.dumps(r))==r
    (ROOT/'docs/research/gx8002-backup-rfft-source-verification.json').write_text(json.dumps(r,indent=2)+'\n')
    print('RFFT dispatcher source admission passed: 110 bytes')
