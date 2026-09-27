# SPDX-License-Identifier: MIT
"""Source admission for original-entry backup DMA deallocator/IRQ pair."""
import json,shutil
from build_gx8002_backup_dma_shared import ROOT,Elf32,sha
from verify_gx8002_backup_dma_deallocate import verify as deallocate
from verify_gx8002_backup_dma_irq import verify as irq
from verify_gx8002_backup_dma_shared import verify as shared
from verify_gx8002_backup_dma_shared_loader import verify as loader
from analyze_gx8002_backup_dma_shared_references import analyze as references
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'deallocate':deallocate(),'irq':irq(),'shared':shared(),'loader':loader(),'references':references()}
    refs=checks['references']
    assert not refs['external_pool_loads']
    assert all(r['entry'] for r in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-dma-shared-pool/pair.elf';elf=Elf32(path.read_bytes(),str(path))
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    rows=[]
    for name,offset,size,kind,symbol in (
        ('.text',0x3d500,180,'compiled_c','open_cfw_gx8002_backup_dma_pair'),
        ('.callback_pointer',0x3d5b8,4,'generated_source_data','open_cfw_gx8002_backup_dma_callback_pointer'),
    ):
        section=next(s for s in elf.sections if s['name']==name);body=elf.contents(section)
        assert len(body)==size and section['address']==offset-0x3b940+0x10003000
        assert bool(section['flags']&4)==(kind=='compiled_c')
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':size,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_b_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'pair.elf')
    files=('build_gx8002_backup_dma_shared.py','build_gx8002_backup_dma_deallocate.py','build_gx8002_backup_dma_irq.py','verify_gx8002_backup_dma_deallocate.py','verify_gx8002_backup_dma_irq.py','verify_gx8002_backup_dma_shared.py','verify_gx8002_backup_dma_shared_loader.py','verify_gx8002_backup_dma_shared_source.py','verify_gx8002_backup_memset_loader.py','analyze_gx8002_backup_dma_shared_references.py','verify_gx8002_memcpy_source.py')
    return {'functions':rows,'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid source admission: both original entries preserved, no tail fill, observed references target entries. Computed/nonstandard entries not globally proven absent.','IRQ/resource/callback dependencies modeled and separately reconstructed; DMA state and callback storage remain separate ownership.','No physical IRQ, timing or complete source-only firmware claim.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-shared-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Shared DMA source gate passed')
