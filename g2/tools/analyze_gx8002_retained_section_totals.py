# SPDX-License-Identifier: MIT
"""Intersect a completed ownership snapshot with authenticated firmware sections."""
import json,re
from pathlib import Path
from analyze_g2_codec_stage2_sections import analyze,SEG2_OFF,CODEC_SHA256
from analyze_gx8002_upstream_objects import sha
ROOT=Path(__file__).resolve().parents[1]

def analyze_retained():
    layout=analyze();p=ROOT/'build/gx8002-source-candidate/build-report.json';raw=p.read_bytes();report=json.loads(raw);assert report['stock_sha256']==CODEC_SHA256
    regions=[]
    for image in ('image_a','image_b'):
        for name,s in layout[image]['stage2'].items():
            if 'flash' not in s or 'size' not in s:continue
            start,end=[int(v,16)+SEG2_OFF for v in re.findall(r'0x[0-9A-Fa-f]+',s['flash'])]
            assert end-start==s['size'];regions.append((image+'/'+name,start,end))
    for name in ('cmd','weight'):
        s=layout['kws_model_payload'][name];start,end=[int(v,16)+SEG2_OFF for v in re.findall(r'0x[0-9A-Fa-f]+',s['flash'])];assert end-start==s['size'];regions.append(('model/'+name,start,end))
    regions.sort(key=lambda x:x[1]);assert all(a[2]<=b[1] for a,b in zip(regions,regions[1:]))
    totals={name:0 for name,_,_ in regions};totals['outside_mapped_stage2_sections']=0;pieces=[]
    for row in report['ownership']:
        if row['kind']!='retained_stock':continue
        start=row['offset'];end=start+row['size'];covered=0
        for name,a,b in regions:
            low,high=max(start,a),min(end,b)
            if low<high:
                size=high-low;totals[name]+=size;covered+=size;pieces.append({'section':name,'package_offset':low,'bytes':size})
        totals['outside_mapped_stage2_sections']+=row['size']-covered
    assert sum(totals.values())==report['byte_ownership']['retained_stock']
    return {'ownership_report_sha256':sha(raw),'ownership_firmware_sha256':report['firmware_sha256'],'stock_sha256':CODEC_SHA256,'retained_by_section':totals,'mapped_pieces':pieces,'limits':['Snapshot of the last completed ownership report, not the status of any live build.','Backup text/data boundary is the existing authenticated analyzer heuristic; text spans may include constants. Outside-mapped bytes include boot stages, headers and padding; no source ownership is inferred.']}
if __name__=='__main__':
    r=analyze_retained();(ROOT/'docs/research/gx8002-retained-section-totals.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['retained_by_section'],indent=2))
