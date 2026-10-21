#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Create exclusive resource ranges from authenticated recovered data maps."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cutting'))
import firmware_cut as cut
EVIDENCE = 'g2/evidence/bundle-accounting/resource-expansion/resources-full.json'


def main():
    manifests={m['payload']:m for m in cut.load_manifests()}
    stocks={p:cut.official_bytes(m) for p,m in manifests.items()}
    value=json.loads((ROOT/EVIDENCE).read_text())
    claims=defaultdict(list)
    components={'apollo_main':'g2-apollo-main','apollo_bootloader':'g2-apollo-bootloader',
                'case':'g2-case','touch':'g2-touch','codec':'g2-codec','ble_em9305':'g2-em9305'}
    def add(payload,lo,hi,kind,label,evidence,digest=None):
        data=stocks[payload]
        if not 0 <= lo < hi <= len(data): raise ValueError('resource range out of bounds')
        actual=cut.sha256(data[lo:hi])
        if digest and digest != actual: raise ValueError('resource hash mismatch: '+label)
        claims[payload].append(dict(start=lo,end=hi,kind=kind,label=label,evidence=evidence))
    allowed={'image','image_descriptor','embedded_text','DSP_table','model_weights','readonly_table',
             'configuration_table','lookup_table','container_metadata'}
    for r in value['resources']:
        if r['kind'] not in allowed: continue
        payload=components[r['component']]
        if r.get('payloadSha256') and r['payloadSha256']!=manifests[payload]['sha256']:
            raise ValueError('wrong resource payload identity')
        add(payload,*r['payloadRange'],r['kind'],r['label'],EVIDENCE,r['sha256'])
    roots=[]
    for font in value['customFontCandidates']:
        if not font['classification'].startswith('corroborated custom font data'):
            raise ValueError('font lacks consumer corroboration')
        root=hex(font['address']);roots.append(root)
        for span in font['validatedSpans']:
            add('g2-apollo-main',*span['payloadRange'],'font',root+':'+span['kind'],EVIDENCE,span['sha256'])
    palette=value['fontConsumerEvidence']['opacityPalette']
    add('g2-apollo-main',*palette['payloadRange'],'font','font opacity palette',EVIDENCE,palette['sha256'])
    # R1 has no font claim: its recovered startup map identifies exact strings,
    # literal data and a callback function. Exclude the executable noop body.
    path='r1/src/config/startup/device-reset-data-regions.json'
    for label,address,size in json.loads((ROOT/path).read_text()):
        if label=='rtc_noop': continue
        add('r1-application',address-0x27000,address-0x27000+size,
            'embedded_text' if label.endswith(('_ring','_sdk')) else 'configuration_table',label,path)
    rows=[]
    for payload, items in sorted(claims.items()):
        points=sorted({v for item in items for v in (item['start'],item['end'])})
        for lo,hi in zip(points,points[1:]):
            owners=[r for r in items if r['start']<=lo and hi<=r['end']]
            if not owners:continue
            kinds={r['kind'] for r in owners}
            if len(kinds)>1:raise ValueError(f'conflicting resource classifications: {payload} {lo:x}: {kinds}')
            rows.append(dict(payload=payload,start=lo,end=hi,kind=next(iter(kinds)),
                             label='; '.join(sorted({r['label'] for r in owners})),
                             evidence=sorted({r['evidence'] for r in owners}),
                             sha256=cut.sha256(stocks[payload][lo:hi]),payload_sha256=manifests[payload]['sha256']))
    (ROOT/'tools/build/resources.json').write_text(json.dumps(rows,indent=2)+'\n')
    metadata=dict(font_roots=roots,font_qualification=value['fontConsumerEvidence']['qualification'],
                  policy='unique stored ranges; shared font stores count once; compressed mixed code/data not called non-executable',
                  evidence_sha256={EVIDENCE:cut.sha256((ROOT/EVIDENCE).read_bytes())},
                  excluded_kinds=['compressed_initializer','initialized_ram_copy','vector_pair','vector_table'])
    (ROOT/'tools/build/resource-inventory.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'{len(rows)} exclusive resource ranges; {len(roots)} corroborated font roots')

if __name__=='__main__':main()
