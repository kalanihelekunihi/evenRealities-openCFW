# SPDX-License-Identifier: MIT
"""Admit source architecture backup IRQ entry at its original entry."""
import json,shutil
from verify_gx8002_backup_irq_entry import verify as compare
from verify_gx8002_backup_irq_entry_loader import verify as loader
from analyze_gx8002_backup_irq_entry_references import analyze as references
from build_gx8002_backup_irq_entry import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_irq_architecture_frame import MANUAL_SHA
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    assert sha((ROOT/'build/csky-isa-manual.pdf').read_bytes())==MANUAL_SHA
    checks={'comparison':compare(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(row['entry'] for row in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-irq-entry/entry.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    s=allocated[0];body=e.contents(s)
    assert s['name']=='.text' and s['address']==0x10004880 and len(body)==80 and s['flags']&4
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_irq_compact_entry'
    row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_assembly','compiled_bytes':80,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x3d1c0,'bytes':80,'sha256':sha(stock[0x3d1c0:0x3d210]),'region':'image_b_sram_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'entry.elf')
    files=('build_gx8002_backup_irq_entry.py','verify_gx8002_backup_irq_entry.py','verify_gx8002_backup_irq_entry_loader.py','analyze_gx8002_backup_irq_entry_references.py','verify_gx8002_backup_irq_entry_source.py','verify_gx8002_irq_compact.py','verify_gx8002_irq_architecture_frame.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'isa_manual_sha256':MANUAL_SHA,'limits':['Source architecture assembly, counted separately from C; byte-exact original entry and frame.','Decoded context and nested-interrupt model assumes valid external vectors and ABI-compliant callbacks.','Observed references target entry; computed/nonstandard entries not globally excluded. Hardware exception timing and stack capacity remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-irq-entry-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup IRQ entry source gate passed')
