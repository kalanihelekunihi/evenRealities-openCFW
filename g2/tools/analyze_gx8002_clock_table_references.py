# SPDX-License-Identifier: MIT
"""Literal-pointer inventory for proposed table interval, not absence proof."""
import json
import struct
from analyze_gx8002_clock_table_placement import analyze,ROOT,sha
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA


def scan(data,low,high):
    return [{'package_offset':i,'value':struct.unpack_from('<I',data,i)[0]}
            for i in range(len(data)-3) if low<=struct.unpack_from('<I',data,i)[0]<high]


def analyze_references():
    placement=analyze();low=placement['table_runtime_address'];high=low+16
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Reference stock identity')
    candidate=(ROOT/'build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin').read_bytes()
    report=json.loads((ROOT/'build/gx8002-source-candidate/build-report.json').read_text())
    if sha(candidate)!=report['firmware_sha256']:raise ValueError('Reference candidate identity')
    hits=scan(stock,low,high)
    for hit in hits:
        hit['current_owner']=next(row for row in report['ownership'] if row['offset']<=hit['package_offset'] and hit['package_offset']+4<=row['offset']+row['size'])
    return {'placement':placement,'interval':[low,high],
            'stock_literal_hits':hits,'candidate_literal_hits':scan(candidate,low,high),
            'source_admitted':False,'limits':['All byte alignments scanned for little-endian 32-bit literals only. No computed-reference, instruction-flow, relocation or hardware absence proof.']}

if __name__=='__main__':
    report=analyze_references();(ROOT/'docs/research/gx8002-clock-table-references.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Stock hits:',report['stock_literal_hits'],'Candidate hits:',report['candidate_literal_hits'])
