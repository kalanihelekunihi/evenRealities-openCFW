# SPDX-License-Identifier: MIT
"""Identify arithmetic table data that linear disassembly mistakes for branches."""
import json
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    authored=bytes(value.bit_length() for value in range(256))
    start,end=0x4df14,0x4e014
    assert stock[start:end]==authored==stock[0x152a8:0x153a8]
    refs=json.loads((ROOT/'docs/research/gx8002-backup-platform-config-references.json').read_text())
    branches=refs['functions']['platform_config']['branches']
    data=[r for r in branches if start<=r['offset']<end]
    remaining=[r for r in branches if not start<=r['offset']<end]
    report={'image_sha256':IMAGE_SHA,'interval':[start,end],'bytes':256,'sha256':sha(authored),
            'definition':'Entry n is the unsigned integer bit length of n; entry zero is zero.',
            'primary_source_table_interval':[0x152a8,0x153a8],
            'data_decoded_as_branches':data,'remaining_branch_findings':remaining,
            'source_admitted':False,'limits':['Exact mathematical table identity identifies these branch-like byte patterns as data. Runtime consumer and source-data admission are separate; remaining interior findings are not waived.']}
    (ROOT/'docs/research/gx8002-backup-bit-length-table.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    r=analyze();print(len(r['data_decoded_as_branches']),'data artifacts;',len(r['remaining_branch_findings']),'remaining branch findings')
