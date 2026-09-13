# SPDX-License-Identifier: MIT
"""Admit shared source backup DMA configuration at its original entry."""
import json,shutil
from verify_gx8002_backup_dma_configure import verify as compare
from verify_gx8002_backup_dma_configure_loader import verify as loader
from analyze_gx8002_backup_dma_configure_references import analyze as references
from build_gx8002_backup_dma_configure import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_backup_dma_configure_mutation import verify as mutation

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'comparison':compare(),'mutation':mutation(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(row['entry'] for row in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-dma-configure/configure.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    s=allocated[0];body=e.contents(s)
    assert s['name']=='.text' and s['address']==0x100049d4 and len(body)==344 and s['flags']&4
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_backup_dma_configure'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':344,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x3d314,'bytes':344,'sha256':sha(stock[0x3d314:0x3d46c]),'region':'image_b_sram_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'configure.elf')
    files=('execute_gx8002_backup_dma_configure.py','verify_gx8002_backup_dma_configure_mutation.py','build_gx8002_backup_dma_configure.py','verify_gx8002_backup_dma_configure.py','verify_gx8002_backup_dma_configure_loader.py','analyze_gx8002_backup_dma_configure_references.py','verify_gx8002_backup_dma_configure_source.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Recovered C with authenticated pinned upstream configuration layout, inline acknowledgements and original helper bindings.','344 compiled bytes replace the routine prefix; adjacent 64 stock bytes retained. No tail fill. Whole original routine scanned for observed interior references.','Ordered effects, error exits and modeled helper mutations checked. Physical DMA operation, timing and computed-entry closure remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-configure-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup DMA configuration source gate passed')
