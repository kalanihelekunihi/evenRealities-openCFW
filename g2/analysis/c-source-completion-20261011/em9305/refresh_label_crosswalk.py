#!/usr/bin/env python3
"""Refresh static label inclusion; not function/runtime/completion coverage."""
import csv,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];folder=Path(__file__).resolve().parent
src=root/'g2/symbols/ble_em9305.tsv';boundary=folder/'body-coverage-boundary.json'
data=json.loads(boundary.read_text());ranges=[(int(x['start'],16),int(x['end_exclusive'],16)) for x in data['native_envelopes_with_C_candidates']]
rows=list(csv.DictReader(src.open(),delimiter='\t'));covered=[];remaining=[]
for row in rows:
 start=int(row['address'],16);end=int(row['end'],16)
 (covered if any(a<=start and end<=b for a,b in ranges) else remaining).append(row)
out={'scope':'Retained labels vs individual static C envelopes; includes inferred gaps, not a function census or source completion percentage','input':str(src.relative_to(root)),'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'body_boundary_sha256':hashlib.sha256(boundary.read_bytes()).hexdigest(),'rows':len(rows),'rows_within_C_envelopes':len(covered),'remaining_label_rows':len(remaining),'remaining':remaining,'source_complete':False}
(folder/'native-label-source-crosswalk.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['rows','rows_within_C_envelopes','remaining_label_rows','source_complete']}))
