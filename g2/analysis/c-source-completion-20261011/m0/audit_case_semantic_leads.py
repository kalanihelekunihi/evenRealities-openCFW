#!/usr/bin/env python3
"""Triage full and abbreviated native-address leads without claiming bodies."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3]
prior=json.loads((H/'case-body-crosswalk.json').read_text())
files=sorted((R/'g2/components/case').rglob('*.c'))
heads={str(p.relative_to(R)):p.read_text(errors='replace')[:700].lower() for p in files}
rows=[]
for row in prior['rows']:
 address=row['entry'];short='0x'+address[-4:]
 exact=[p for p,h in heads.items() if address in h]
 abbreviated=[p for p,h in heads.items() if short in h and p not in exact]
 classification='exact_header_lead' if exact else ('abbreviated_header_lead' if abbreviated else 'no_header_lead')
 rows.append({'entry':address,'classification':classification,
              'exact_header_sources':exact,'abbreviated_header_sources':abbreviated})
counts={k:sum(r['classification']==k for r in rows) for k in
        ('exact_header_lead','abbreviated_header_lead','no_header_lead')}
report={'status':'ADDRESS_TRIAGE_ONLY','fixed_pseudocode_sha256':prior['summary']['fixed_pseudocode_sha256'],
 'recognized_entries':len(rows),'counts':counts,
 'limitations':['An address in a comment is a lead, not proof of a C body or semantic equivalence.',
                'Four-digit short addresses may collide or merely label a called child.',
                'Native indirect calls, vector entries, uncalled routines and data/layout are not covered.'],
 'rows':rows}
(H/'case-semantic-leads.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'recognized_entries':len(rows),'counts':counts},indent=2))
