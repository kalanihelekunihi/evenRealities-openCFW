# SPDX-License-Identifier: MIT
"""Source gate for conditional backup BSS clear and original bound literals."""
import json,shutil
from verify_gx8002_backup_clear_bss import verify as compare
from verify_gx8002_backup_clear_bss_loader import verify as loader
from analyze_gx8002_backup_clear_bss_references import analyze as references
from build_gx8002_backup_clear_bss import ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'comparison':compare(),'loader':loader(),'references':references()}
    refs=checks['references'];assert not refs['external_pool_loads']
    assert all(r['entry'] for r in refs['external_branches']+refs['runtime_word_matches'])
    path=ROOT/'build/gx8002-backup-clear-bss/clear.elf';e=Elf32(path.read_bytes(),str(path))
    allocated=[s for s in e.sections if s['flags']&2 and s['size']];assert len(allocated)==2
    assert not any(e.relocations(s['index']) for s in e.sections)
    assert not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for name,offset,size,kind,symbol in (
        ('.text',0x3ba68,28,'compiled_c','open_cfw_gx8002_backup_clear_bss'),
        ('.bounds',0x3ba84,8,'generated_source_data','open_cfw_gx8002_backup_bss_bounds'),
    ):
        s=next(s for s in allocated if s['name']==name);body=e.contents(s)
        assert s['address']==offset-0x3b940+0x10003000 and len(body)==size
        assert bool(s['flags']&4)==(kind=='compiled_c')
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':size,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_b_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'clear.elf')
    files=('build_gx8002_backup_clear_bss.py','verify_gx8002_backup_clear_bss.py','verify_gx8002_backup_clear_bss_loader.py','analyze_gx8002_backup_clear_bss_references.py','verify_gx8002_backup_clear_bss_source.py','verify_gx8002_backup_dma_callback_clear.py','verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':rows,'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Fixed recovered range and ordered word clearing, invoked conditionally by existing startup. No unconditional zero-default claim.','Entry preserved, observed references target entry; computed/nonstandard entries not globally excluded.','Hardware memory retention and whole firmware remain separately unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-clear-bss-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup clear source gate passed')
