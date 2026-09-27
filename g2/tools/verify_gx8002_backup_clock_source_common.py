# SPDX-License-Identifier: MIT
"""Shared admission evidence for upstream backup clock lookup/tables and gate."""
import json,shutil
from pathlib import Path
from compare_gx8002_backup_clock_lookup import verify as lookup
from verify_gx8002_backup_clock_gate_composition import verify as composition
from verify_gx8002_backup_clock_loader import verify as loader
from analyze_gx8002_backup_clock_references import analyze as references
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_logging import check_paths


def verify_part(part,prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);assert part in ('lookup','gate')
    checks={'lookup':lookup(),'composition':composition(),'loader':loader(),'references':references()}
    refs=checks['references']
    if 'functions' in refs:
        for name,record in refs['functions'].items():
            assert not record['external_pool_loads']
            assert all(r['entry'] for r in record['branches'])
            assert all(r['entry'] or (name=='gate' and r['replaced_switch_word']) for r in record['runtime_words'])
        assert all(r['within_replaced_code'] for r in refs['tables']['switch']['pointer_matches'])
    else:
        assert not refs['external_literal_pools']
        assert not refs['stored_address_words']
        assert all(r['entry'] for r in refs['external_branches'])
    if part=='lookup':
        path=ROOT/'build/gx8002-backup-clock-tables/tables.elf';artifact='tables.elf'
        expected=[('.text',0x100034e0,160,'compiled_c','__module_get_info'),
                  ('.data.gx_clock_param_table',0x2001699c,416,'generated_source_data','gx_clock_param_table'),
                  ('.data.gx_clock_dto_table',0x20016b3c,3,'generated_source_data','gx_clock_dto_table'),
                  ('.data.gx_clock_div_table',0x20016b40,68,'generated_source_data','gx_clock_div_table')]
    else:
        path=ROOT/'build/gx8002-backup-platform-gate/gate.elf';artifact='gate.elf'
        expected=[('.text',0x10003be8,254,'compiled_c','open_cfw_gx8002_platform_gate'),
                  ('.rodata',0x1001295c,148,'generated_source_data','open_cfw_gx8002_platform_gate_switches')]
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    elf=Elf32(path.read_bytes(),str(path));alloc=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(alloc)==len(expected)
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    rows=[]
    for name,address,size,kind,symbol in expected:
        section=next(s for s in alloc if s['name']==name);body=elf.contents(section)
        assert section['address']==address and len(body)==size
        assert bool(section['flags']&4)==(kind=='compiled_c')
        offset=address-(0x20003000 if address>=0x20000000 else 0x10003000)+0x3b940
        if name.startswith('.data'):assert body==stock[offset:offset+size]
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':size,'compiled_sha256':sha(body),
                     'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_b_sram_data' if address>=0x20000000 else 'image_b_sram_text'}]})
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/artifact)
    files=('build_gx8002_backup_platform_gate.py','build_gx8002_backup_clock_tables.py','compare_gx8002_backup_clock_lookup.py',
           'compare_gx8002_backup_platform_gate.py','verify_gx8002_backup_clock_gate_composition.py','verify_gx8002_backup_clock_loader.py',
           'analyze_gx8002_backup_clock_references.py','verify_gx8002_backup_clock_source_common.py',
           'verify_gx8002_backup_clock_lookup_source.py','verify_gx8002_backup_platform_gate_source.py',
           'verify_gx8002_backup_memset_loader.py','verify_gx8002_memcpy_source.py')
    return {'functions':rows,'checks':checks,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Pinned upstream source, original entry/table addresses; adjacent code tails and alignment padding retained without replacement fill.',
                      'Observed gate interior references confined to regenerated switch words. Computed/nonstandard entry closure is not globally proven.',
                      'Fixed nonoverlapping tables/output, abstract frames and modeled registers; physical clock transitions and concurrent mutations unqualified.']}
