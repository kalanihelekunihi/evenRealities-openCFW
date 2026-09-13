# SPDX-License-Identifier: MIT
"""Admit shared source backup DMA callback setter at its original entry."""
import json,shutil
from verify_gx8002_backup_dma_callback import verify as compare
from verify_gx8002_backup_dma_callback_loader import verify as loader
from analyze_gx8002_backup_dma_callback_references import analyze as references
from build_gx8002_backup_dma_callback import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'comparison':compare(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(row['entry'] for row in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-dma-callback/callback.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    s=allocated[0];body=e.contents(s)
    assert s['name']=='.text' and s['address']==0x10004cb8 and len(body)==16 and s['flags']&4
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_dma_callback'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':16,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x3d5f8,'bytes':16,'sha256':sha(stock[0x3d5f8:0x3d608]),'region':'image_b_sram_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'callback.elf')
    files=('build_gx8002_backup_dma_callback.py','verify_gx8002_backup_dma_callback.py','verify_gx8002_backup_dma_callback_loader.py','analyze_gx8002_backup_dma_callback_references.py','verify_gx8002_backup_dma_callback_source.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Shared callback setter C with backup table binding; ordered callback then private-data stores.','Only 16 compiled bytes admitted; adjacent four stock bytes retained. No replacement tail fill.','Arithmetic cases outside channels zero and one do not assert valid storage. Computed entries and physical callback delivery remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-callback-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup DMA callback source gate passed')
