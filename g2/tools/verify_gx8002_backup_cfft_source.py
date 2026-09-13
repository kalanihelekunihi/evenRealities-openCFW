# SPDX-License-Identifier: MIT
"""Experimental source admission for the recovered CFFT dispatcher only."""
import json,shutil
from pathlib import Path
from verify_gx8002_logging import check_paths
from verify_gx8002_backup_cfft import verify as behavior
from verify_gx8002_backup_cfft_loader import verify as loader
from analyze_gx8002_backup_cfft_references import analyze as references
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'behavior':behavior(),'loader':loader(),'references':references()}
    assert checks['behavior']['cases']==66736
    assert checks['loader']['loader_cases']==12 and checks['references']['reference_ready']
    path=ROOT/'build/gx8002-backup-cfft/cfft.elf';elf=Elf32(path.read_bytes(),'CFFT dispatcher')
    allocated=[s for s in elf.sections if s['size'] and s['flags']&2]
    assert len(allocated)==1
    section=allocated[0];body=elf.contents(section)
    assert section['name']=='.text' and section['address']==0x1000f1d4 and len(body)==150 and section['flags']&4
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert checks['loader']['patches'][0]['sha256']==sha(body)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_backup_cfft'
    row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':150,'compiled_sha256':sha(body),
         'stock_occurrences':[{'symbol':symbol,'package_offset':0x47b14,'bytes':150,'sha256':sha(stock[0x47b14:0x47baa]),'region':'image_b_sram_text'}]}
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'cfft.elf')
    files=('verify_gx8002_backup_cfft_source.py','build_gx8002_backup_cfft.py','build_gx8002_backup_fft_descriptors.py',
           'verify_gx8002_backup_cfft.py','verify_gx8002_backup_cfft_loader.py',
           'analyze_gx8002_backup_cfft_references.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Dispatcher only: five transform/reversal helpers remain retained. Their arithmetic is not qualified by modeled calls.',
                      'Every 16-bit length checked for forward/no-reversal dispatch; boundary flags and helper-induced descriptor mutations also compared. Lower helper arithmetic is modeled.',
                      'Two direct entry references checked, no stored runtime pointers or external literal-pool loads. Global computed-entry closure is not proven.',
                      'Original 74-byte unused function tail remains retained. Experimental hybrid replacement, not complete source-only firmware.']}
if __name__=='__main__':
    r=verify(output=ROOT/'build/gx8002-source-candidate/backup-cfft')
    assert json.loads(json.dumps(r))==r
    (ROOT/'docs/research/gx8002-backup-cfft-source-verification.json').write_text(json.dumps(r,indent=2)+'\n')
    print('CFFT dispatcher source admission passed: 150 bytes')
