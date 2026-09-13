# SPDX-License-Identifier: MIT
"""Admit recovered backup IRQ registration helper at its original entry."""
import json,shutil
from verify_gx8002_backup_request_irq import verify as compare
from verify_gx8002_backup_request_irq_loader import verify as loader
from analyze_gx8002_backup_request_irq_references import analyze as references
from build_gx8002_backup_request_irq import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'comparison':compare(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(row['entry'] for row in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-request-irq/request.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    s=allocated[0];body=e.contents(s)
    assert s['name']=='.text' and s['address']==0x10004844 and len(body)==40 and s['flags']&4
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_backup_request_irq'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':40,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x3d184,'bytes':40,'sha256':sha(stock[0x3d184:0x3d1ac]),'region':'image_b_sram_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'request.elf')
    files=('build_gx8002_backup_request_irq.py','verify_gx8002_backup_request_irq.py','verify_gx8002_backup_request_irq_loader.py','analyze_gx8002_backup_request_irq_references.py','verify_gx8002_backup_request_irq_source.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Unsigned IRQ-range and null-handler guards preserve stock behavior. Handler/context stores precede the write-one interrupt enable.','Decoded comparison checks ordered stores and ABI; normal loader and observed direct-entry references checked.','Computed/nonstandard entries and physical asynchronous interrupt effects remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-request-irq-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup IRQ registration source gate passed')
