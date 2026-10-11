#!/usr/bin/env python3
"""Find aligned Thumb code-pointer candidates missed by direct BL census."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3]
payload=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
fixed={int(x['entry'],16) for x in json.loads((H/'case-body-crosswalk.json').read_text())['rows']}
direct={int(x['target'],16) for x in json.loads((H/'case-native-call-target-audit.json').read_text())['rows']}
sources=list((R/'g2/components/case').rglob('*.c'))
heads={str(p.relative_to(R)):p.read_text(errors='replace')[:700].lower() for p in sources}
targets={}
for offset in range(0,len(payload)-3,4):
 value=int.from_bytes(payload[offset:offset+4],'little')
 if 0x08000001<=value<0x0800d26d and value&1:
  targets.setdefault(value&~1,[]).append(offset)
rows=[]
for target,places in sorted(targets.items()):
 full=f'0x{target:08x}';short=f'0x{target&0xffff:04x}'
 leads=[p for p,h in heads.items() if full in h or short in h]
 rows.append({'target':full,'literal_offsets':[f'0x{x:04x}' for x in places],
              'fixed_catalogue':target in fixed,'direct_bl_target':target in direct,
              'source_header_leads':leads})
report={'status':'CANDIDATE_POINTER_TRIAGE_ONLY',
 'stock_payload_sha256':hashlib.sha256(payload).hexdigest(),
 'aligned_thumb_pointer_targets':len(rows),
 'outside_fixed_and_direct':sum(not r['fixed_catalogue'] and not r['direct_bl_target'] for r in rows),
 'limitations':['Aligned odd words can occur as data or code literals; each pointer role needs a consumer/entry check.',
                'Code pointers built at runtime, unaligned words and indirect calls without retained literals are absent.',
                'Source address mentions do not prove body equivalence.'],
 'rows':rows}
(H/'case-indirect-pointer-targets.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'targets':report['aligned_thumb_pointer_targets'],
                  'outside_fixed_and_direct':report['outside_fixed_and_direct']},indent=2))
