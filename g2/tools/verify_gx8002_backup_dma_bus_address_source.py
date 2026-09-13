# SPDX-License-Identifier: MIT
"""Admit shared source backup DMA address translation at its original entry."""
import json,shutil
from verify_gx8002_backup_dma_bus_address import verify as compare
from verify_gx8002_backup_dma_bus_address_loader import verify as loader
from analyze_gx8002_backup_dma_bus_address_references import analyze as references
from build_gx8002_backup_dma_bus_address import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'comparison':compare(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(row['entry'] for row in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-dma-bus-address/bus_address.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    s=allocated[0];body=e.contents(s)
    assert s['name']=='.text' and s['address']==0x100051c4 and len(body)==20 and s['flags']&4
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    symbol='open_cfw_gx8002_dma_bus_address'
    row={'symbol':symbol,'section_name':'.text','compiled_bytes':20,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x3db04,'bytes':20,'sha256':sha(stock[0x3db04:0x3db18]),'region':'image_b_sram_text'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'bus_address.elf')
    files=('build_gx8002_backup_dma_bus_address.py','verify_gx8002_backup_dma_bus_address.py','verify_gx8002_backup_dma_bus_address_loader.py','analyze_gx8002_backup_dma_bus_address_references.py','verify_gx8002_backup_dma_bus_address_source.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Shared C RAM-alias address mapper at the original backup entry; all 20 bytes compiled, no replacement tail fill.','Decoded mapping corpus covers every 64-KiB block endpoints and dense alias boundaries; observed references target entry.','Physical bus addressability and computed/nonstandard entry closure remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-bus-address-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup DMA address translation source gate passed')
