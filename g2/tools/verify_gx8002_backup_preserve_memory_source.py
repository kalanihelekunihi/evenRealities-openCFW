# SPDX-License-Identifier: MIT
"""Admit recovered backup memory-preservation predicate at its original entry."""
import json,shutil
from verify_gx8002_backup_preserve_memory import verify as compare
from verify_gx8002_backup_preserve_memory_loader import verify as loader
from analyze_gx8002_backup_preserve_memory_references import analyze as references
from build_gx8002_backup_preserve_memory import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'comparison':compare(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(row['entry'] for row in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-preserve-memory/predicate.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    s=allocated[0];body=e.contents(s)
    assert s['name']=='.text' and s['address']==0x10003ffc and len(body)==32 and s['flags']&4
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_backup_preserve_memory'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':32,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x3c93c,'bytes':32,'sha256':sha(stock[0x3c93c:0x3c95c]),'region':'image_b_sram_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'predicate.elf')
    files=('build_gx8002_backup_preserve_memory.py','verify_gx8002_backup_preserve_memory.py','verify_gx8002_backup_preserve_memory_loader.py','analyze_gx8002_backup_preserve_memory_references.py','verify_gx8002_backup_preserve_memory_source.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Original entry and exact read sequence preserved, with status decoder composed into C. No replacement fill.','Physical meanings and effects of status registers remain unconfirmed; synthetic MMIO values used.','Observed references target entry; computed/nonstandard entries not globally excluded. Not complete source-only firmware.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-preserve-memory-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Preservation predicate source gate passed')
