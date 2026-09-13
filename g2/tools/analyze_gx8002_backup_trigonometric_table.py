# SPDX-License-Identifier: MIT
"""Check a mathematical definition for backup paired Q14 coefficients."""
import json,math,struct
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from analyze_gx8002_backup_bit_length_table import analyze as bit_length

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    values=[(round(16384*(1-math.cos(n*math.pi/256))),round(16384*math.sin(n*math.pi/256))) for n in range(-128,128)]
    authored=b''.join(struct.pack('<hh',*pair) for pair in values)
    start,end=0x4da18,0x4de18;assert stock[start:end]==authored
    remaining=bit_length()['remaining_branch_findings']
    data=[r for r in remaining if start<=r['offset']<end]
    code=[r for r in remaining if not start<=r['offset']<end]
    assert all(r['entry'] for r in code)
    report={'image_sha256':IMAGE_SHA,'interval':[start,end],'bytes':len(authored),'sha256':sha(authored),
            'definition':'For integer n from -128 through 127: signed int16 pairs round(16384*(1-cos(n*pi/256))), round(16384*sin(n*pi/256)).',
            'data_decoded_as_branches':data,'remaining_branch_findings':code,
            'source_admitted':False,'limits':['All 512 coefficients match the stated formula on this macOS Python runtime. Consumer semantics and reproducible cross-runtime rounding qualification remain pending; not source admission.']}
    (ROOT/'docs/research/gx8002-backup-trigonometric-table.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
if __name__=='__main__':
    r=analyze();print(len(r['data_decoded_as_branches']),'trigonometric data artifacts;',len(r['remaining_branch_findings']),'entry callers')
