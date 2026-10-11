#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,random
h=Path(__file__).resolve().parent;p=h/'verify_short_formatter.py';ns={'__file__':str(p)};exec(compile(p.read_text().split('fmts=')[0],str(p),'exec'),ns)
records=json.loads((h/'short-logger-call-domain.json').read_text())['calls']
resolved=[r for r in records if r['format'] is not None and len(r['format'])<180]
# Prefer accepted actual strings with only 0-4 conversion markers and no `%s`/`%f` pointer/FP assumptions.
selected=[r for r in resolved if 0<=r['format'].count('%')<=4 and '%s' not in r['format'] and '%f' not in r['format'] and '%F' not in r['format']]
rng=random.Random(0x43ce9e);rng.shuffle(selected);selected=selected[:500]
rows=[]
for r in selected:
 case=dict(fmt=r['format'],flags=0,level=0,token=(4<<22)|0x12345,seq=1,tick=1000,fpscr=0x02040000)
 a=ns['run'](False,case);b=ns['run'](True,case)
 if a!=b:raise AssertionError((r,a,b))
 rows.append({'call':r['call'],'format':r['format'],'packet':a['calls'][-1]})
(h/'short-formatter-actual-literals-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'static_resolved_source_pool':len(resolved),'selected_pool':len(selected),'source_sha256':hashlib.sha256((h/'short_formatter.c').read_bytes()).hexdigest(),'rows':rows,'limits':'Real stock literal strings at conservative short-logger calls; synthetic token/varargs, not original whole-caller execution or pointer ownership.'},indent=2)+'\n')
print('PASS',len(rows))
