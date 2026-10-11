#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,itertools
h=Path(__file__).resolve().parent;p=h/'verify_short_formatter.py'
ns={'__file__':str(p)};exec(compile(p.read_text().split('fmts=')[0],str(p),'exec'),ns)
run=ns['run'];rows=[]
for length,null,fmt,limit in itertools.product((0,1,15,16,17,31,32,63),(False,True),('%s','%s%s','%s%d','%s%s%s'),(0,1,2,3)):
 case=dict(fmt=fmt,flags=0,level=0,token=(limit<<22)|0x12345,seq=254,tick=999,str_bytes=bytes((65+i%26 for i in range(length))),null_string=null)
 a=run(False,case);b=run(True,case)
 if a!=b:raise AssertionError((case,a,b))
 rows.append(dict(length=length,null=null,fmt=fmt,limit=limit))
(h/'short-formatter-strings-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'source_sha256':hashlib.sha256((h/'short_formatter.c').read_bytes()).hexdigest(),'rows':rows,'limits':'Synthetic readable string memory and ABI provider boundaries; not production pointer ownership.'},indent=2)+'\n')
print('PASS',len(rows))
