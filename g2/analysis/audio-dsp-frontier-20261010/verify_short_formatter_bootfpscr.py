#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,itertools
h=Path(__file__).resolve().parent;p=h/'verify_short_formatter.py';ns={'__file__':str(p)};exec(compile(p.read_text().split('fmts=')[0],str(p),'exec'),ns)
values=(0,0x8000000000000000,0x3ff0000000000000,0xbff0000000000000,0x3ff8000000000000,0x7fefffffffffffff,0x0010000000000000,1,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001,0x7ff0000000000001)
rows=[]
for bits,fmt in itertools.product(values,('%f','%F','%f %d')):
 case=dict(fmt=fmt,flags=0,level=0,token=(3<<22)|0x12345,seq=0,tick=1000,fp64bits=bits,fpscr=0x02040000)
 a=ns['run'](False,case);b=ns['run'](True,case)
 if a!=b:raise AssertionError((case,a,b))
 rows.append(dict(bits=hex(bits),fmt=fmt,fpscr=hex(a['fpscr']),packet=a['calls'][-1]))
(h/'short-formatter-bootfpscr-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'startup_fpscr':'0x02040000','source_sha256':hashlib.sha256((h/'short_formatter.c').read_bytes()).hexdigest(),'rows':rows,'limits':'Startup FPSCR preset inferred from stock 0x5e4288; no external exception-mode changes or traps exercised.'},indent=2)+'\n')
print('PASS',len(rows))
