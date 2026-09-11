# SPDX-License-Identifier: MIT
"""Validate actual source-built table/host partition without emitting firmware."""
import json
from analyze_gx8002_clock_table_placement import analyze,ROOT,Elf32,sha
from analyze_gx8002_upstream_objects import IMAGE
from gx8002_source_tail_data import partition


def verify():
    placement=analyze();stock=IMAGE.read_bytes()
    host_report=json.loads((ROOT/'docs/research/gx8002-platform-config-verification.json').read_text())['functions'][0]
    occurrence=host_report['stock_occurrences'][0]
    host_elf=Elf32((ROOT/'build/gx8002-board/config.elf').read_bytes(),'partition host')
    section=next(s for s in host_elf.sections if s['name']==host_report['section_name'])
    host_code=host_elf.contents(section)
    if len(host_code)!=host_report['compiled_bytes'] or sha(host_code)!=host_report['compiled_sha256']:
        raise ValueError('Partition host code identity')
    host=dict(occurrence,compiled_bytes=len(host_code),compiled_sha256=sha(host_code),
              payload=host_code+bytes(occurrence['bytes']-len(host_code)))
    elf=Elf32((ROOT/'build/gx8002-clock-frequency-table-probe/placement.elf').read_bytes(),'partition table')
    table_section=next(s for s in elf.sections if s['name']=='.rodata.subband_hz')
    payload=elf.contents(table_section);offset=placement['table_package_offset']
    table=dict(symbol='open_cfw_gx8002_clock_subband_hz',package_offset=offset,bytes=len(payload),
               compiled_bytes=len(payload),compiled_sha256=sha(payload),payload=payload,
               sha256=sha(stock[offset:offset+len(payload)]),ownership_kind='generated_source_data')
    rows=partition(stock,[host],table,host['symbol'],host['sha256'])
    if rows[0]['payload']!=host_code or rows[1]['payload']!=payload:
        raise ValueError('Partition changes compiled bytes')
    return {'placement':placement,'partitioned_regions':[{k:v for k,v in r.items() if k!='payload'} for r in rows],
            'source_admitted':False,'firmware_emitted':False,
            'limits':['Actual compiled host/table ownership partition only; full clock qualification and provider integration pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-table-partition.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(r['symbol'],r['package_offset'],r['bytes']) for r in report['partitioned_regions']])
