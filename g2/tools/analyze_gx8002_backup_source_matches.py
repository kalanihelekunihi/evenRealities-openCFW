# SPDX-License-Identifier: MIT
"""Find retained backup code matching reviewed primary-source stock envelopes."""
import json,re
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from analyze_g2_codec_stage2_sections import analyze as section_map, SEG2_OFF


def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    snapshot=(ROOT/'build/gx8002-source-candidate/build-report.json').read_bytes();ownership=json.loads(snapshot)
    assert ownership['stock_sha256']==IMAGE_SHA
    layout=section_map()['image_b']['stage2']['sram_text']
    low,high=[int(v,16)+SEG2_OFF for v in re.findall(r'0x[0-9a-fA-F]+',layout['flash'])]
    assert high-low==layout['size']
    retained=[(r['offset'],r['offset']+r['size']) for r in ownership['ownership'] if r['kind']=='retained_stock']
    rows=[]
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in sorted(set(re.findall(r"'(gx8002-[^']+\.json)'",registry))):
        report=json.loads((ROOT/'docs/research'/name).read_text())
        for row in report.get('functions',[report]):
            if row.get('ownership_kind')=='generated_source_data':continue
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a,n=occurrence.get('package_offset'),occurrence.get('bytes')
                if a is None or n is None or n<32 or a>=0x184fc:continue
                body=stock[a:a+n]
                if occurrence.get('sha256')!=sha(body):continue
                found=[];at=stock.find(body,low,high)
                while at>=0:
                    if at%2==0 and any(x<=at and at+n<=y for x,y in retained):found.append(at)
                    at=stock.find(body,at+1,high)
                if found:rows.append({'report':name,'symbol':row.get('symbol'),'primary_offset':a,'bytes':n,'sha256':sha(body),'backup_offsets':found})
    rows.sort(key=lambda r:(-r['bytes'],r['primary_offset']))
    intervals=sorted((a,a+r['bytes']) for r in rows for a in r['backup_offsets']);merged=[]
    for a,b in intervals:
        if merged and a<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],b)
        else:merged.append([a,b])
    return {'stock_sha256':IMAGE_SHA,'ownership_snapshot_sha256':sha(snapshot),'backup_search_interval':[low,high],'segment_package_offset':SEG2_OFF,'matches':rows,'unique_matching_bytes':sum(b-a for a,b in merged),'source_admitted':False,'limits':['Byte-identical reviewed stock envelopes are reconstruction leads, not source ownership. Embedded absolute addresses, cross-image calls and runtime mappings need separate qualification. Backup text boundary uses existing section-map heuristic.','Minimum 32-byte contiguous exact matches only; no-match results do not exclude upstream ancestry or equivalent code. Snapshot is last completed build, not live-build status.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-backup-source-matches.json').write_text(json.dumps(r,indent=2)+'\n');print('Backup leads:',len(r['matches']),'unique matched bytes:',r['unique_matching_bytes']);print([(x['symbol'],x['bytes'],[hex(a) for a in x['backup_offsets']]) for x in r['matches'][:8]])
