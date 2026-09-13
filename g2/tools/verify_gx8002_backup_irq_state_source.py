# SPDX-License-Identifier: MIT
"""Source gate for pinned upstream backup IRQ state primitives."""
import json,shutil
from verify_gx8002_backup_irq_state import verify as compare
from verify_gx8002_backup_irq_state_loader import verify as loader
from analyze_gx8002_backup_irq_state_references import analyze as references
from build_gx8002_backup_irq_state import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'comparison':compare(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(r['entry'] for r in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-irq-state/state.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==2
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for name,offset,size,kind,symbol in (
        ('.save',0x3d1ac,10,'compiled_c','open_cfw_gx8002_irq_save'),
        ('.restore',0x3d1b8,6,'compiled_c','open_cfw_gx8002_irq_restore'),
    ):
        s=next(s for s in allocated if s['name']==name);body=e.contents(s)
        assert s['address']==offset-0x3b940+0x10003000 and len(body)==size
        assert bool(s['flags']&4)==(kind=='compiled_c')
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':size,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_b_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'state.elf')
    files=('build_gx8002_backup_irq_state.py','verify_gx8002_backup_irq_state.py','verify_gx8002_backup_irq_state_loader.py','analyze_gx8002_backup_irq_state_references.py','verify_gx8002_backup_irq_state_source.py','verify_gx8002_csi_source.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':rows,'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Pinned upstream CSI save/restore, exact stock instruction prefixes. Adjacent two-byte padding per routine retained.','Decoded PSR and token semantics, loader and observed entry references checked.','Physical exception acceptance, privileged execution and computed/nonstandard entries remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-irq-state-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup clear source gate passed')
