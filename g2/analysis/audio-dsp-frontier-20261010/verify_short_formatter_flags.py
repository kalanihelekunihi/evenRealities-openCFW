#!/usr/bin/env python3
from pathlib import Path
import itertools,json,hashlib
h=Path(__file__).resolve().parent;p=h/'verify_short_formatter.py';ns={'__file__':str(p)};exec(compile(p.read_text().split('fmts=')[0],str(p),'exec'),ns)
rows=[]
for a,b,c,category,level in itertools.product((0,1,4),(0,1,4),(0,1,4),(0,5,6),(0,5)):
 case=dict(fmt='%d',flags=0,flags_sequence=[a,b,c],level=level,token=(category<<26)|(2<<22)|0x12345,seq=1,tick=1)
 x=ns['run'](False,case);y=ns['run'](True,case)
 if x!=y:raise AssertionError((case,x,y))
 rows.append(case)
(h/'short-formatter-flags-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'source_sha256':hashlib.sha256((h/'short_formatter.c').read_bytes()).hexdigest(),'rows':rows,'limits':'Changing flags provider returns only; other lower providers synthetic.'},indent=2)+'\n')
print('PASS',len(rows))
