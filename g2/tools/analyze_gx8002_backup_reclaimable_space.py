# SPDX-License-Identifier: MIT
"""Inventory reviewed source fill separately from unqualified retained ranges."""
import json
from build_gx8002_backup_cfft import ROOT,sha

def analyze():
    path=ROOT/'build/gx8002-source-candidate/build-report.json';report=json.loads(path.read_text())
    start,end=0x3b940,0x4ee5c
    fill=[r for r in report['ownership'] if r['kind']=='generated_unreachable_fill' and start<=r['offset'] and r['offset']+r['size']<=end]
    tails=[]
    ordered=report['ownership']
    for before,after in zip(ordered,ordered[1:]):
        if before['kind']=='compiled_c' and after['kind']=='retained_stock' and before['offset']+before['size']==after['offset'] and start<=after['offset']<end:
            tails.append({'preceding_source_symbol':before.get('symbol'),'offset':after['offset'],'retained_span_bytes':after['size'],'reclaimable':False})
    lto=json.loads((ROOT/'docs/research/gx8002-fft-lto-probe.json').read_text());size=sum(r['bytes'] for r in lto['sections'])
    total=sum(r['size'] for r in fill)
    result={'source_build_report_sha256':sha(path.read_bytes()),'source_firmware_sha256':report['firmware_sha256'],'backup_text_range':[start,end],'reviewed_fill':fill,'reviewed_fill_total_bytes':total,'largest_reviewed_fill_bytes':max((r['size'] for r in fill),default=0),'retained_spans_after_compiled_functions':tails,'fft_lto_component_bytes':size,'fft_original_component_bytes':4330,'minimum_shortfall_after_all_fill':max(0,size-4330-total),'limits':['Reviewed unreachable fill is a candidate for separate relocation analysis, not automatically approved storage.','Retained spans are not free: they can combine old function tails, other functions and shared data. Their lengths are not available-space estimates.','No code moved, no retained bytes overwritten. Aggregate fill ignores alignment, branches and fragmentation.']}
    (ROOT/'docs/research/gx8002-backup-reclaimable-space.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=analyze();print(r['reviewed_fill_total_bytes'],r['largest_reviewed_fill_bytes'],r['minimum_shortfall_after_all_fill'])
