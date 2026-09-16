# SPDX-License-Identifier: MIT
"""Inventory backup flash callback ownership; never generate firmware bytes."""
import json, struct
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32


def analyze():
    stock=IMAGE.read_bytes()
    assert sha(stock)==IMAGE_SHA
    layout=ROOT/'docs/research/gx8002-flash-interface-source-bindings.json'
    primary=json.loads(layout.read_text())
    assert len(primary)==30
    cluster_path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
    cluster=Elf32(cluster_path.read_bytes(),'startup');symbols=cluster.symbols()
    table=next(s for s in cluster.sections if s['name']=='.flash_interface_table')
    assert table['address']==0x20016d80 and cluster.contents(table)==stock[0x4f6c0:0x4f738]
    rows=[]
    for row,target in zip(primary,struct.unpack_from('<30I',stock,0x4f6c0)):
        assert not target or 0x10003000<=target<0x1001708c
        rows.append({'index':row['index'],'name':row['name'],'runtime_target':target,
                     'package_target':target-0x10000000+0x38940 if target else None,
                     'primary_source_candidate':row['source_file'] if target else None,
                     'allocated_source_symbols':[s['name'] for s in symbols if target and s['value']==target and s['section'] not in (0,0xfff1) and s['type']==2],
                     'primary_slot_populated':bool(row['runtime_address'])})
    report={'stock_sha256':IMAGE_SHA,'primary_layout_sha256':sha(layout.read_bytes()),
            'cluster_sha256':sha(cluster_path.read_bytes()),'table_runtime_address':0x20016d80,
            'table_package_offset':0x4f6c0,'slots':rows,
            'source_table_sha256':sha(cluster.contents(table)),'source_table_bytes':table['size'],
            'non_null_callbacks':sum(bool(r['runtime_target']) for r in rows),
            'limits':['Diagnostic stock reads only; this inventory is not source reconstruction or generated firmware data.',
                      'Names and candidate files use the recovered primary interface layout. Backup callback behavior must be independently checked.',
                      'The backup UID-read slot is null; do not transplant the populated primary slot.']}
    (ROOT/'docs/research/gx8002-backup-flash-callbacks.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__': print(json.dumps(analyze(),indent=2))
