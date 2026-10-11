#!/usr/bin/env python3
"""Seeded accepted-string exploration using the public-entry oracle."""
from pathlib import Path
import random,json,hashlib
h=Path(__file__).resolve().parent
source=(h/'verify_short_formatter.py').read_text()
exec(compile(source.split('fmts=')[0],str(h/'verify_short_formatter.py'),'exec'))
rng=random.Random(0x43cb84)
rows=[]
for _ in range(3000):
    n=rng.randrange(1,6)
    parts=[]
    for i in range(n):
        flag=rng.choice(['','0','-','+',' ','#','+-'])
        width=rng.choice(['','1','2','08','32','100'])
        precision=rng.choice(['','.0','.2','.16','.*'])
        length=rng.choice(['','l','ll','h','hh'])
        conversion=rng.choice(['d','x','u','o','p','c','f','F','q','%'])
        parts.append('%'+flag+width+precision+length+conversion)
    fmt='foo'.join(parts)
    case=dict(fmt=fmt,flags=rng.choice([0,1,4,5]),level=rng.randrange(0,8),token=(rng.randrange(0,8)<<26)|(rng.randrange(0,16)<<22)|rng.randrange(0,1<<22),seq=rng.randrange(0,256),tick=rng.randrange(0,65536),fpscr=rng.choice([0,0x00400000,0x00800000,0x00c00000,0x01000000,0x02000000]))
    a=run(False,case);b=run(True,case)
    if a!=b:raise AssertionError((case,a,b))
    rows.append(case)
(h/'short-formatter-fuzz-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'seed':'0x43cb84','source_sha256':hashlib.sha256((h/'short_formatter.c').read_bytes()).hexdigest(),'cases_data':rows,'limits':'Seeded well-formed accessible formats and synthetic state; not exhaustive callsite corpus or malformed-pointer proof.'},indent=2)+'\n')
print('PASS',len(rows))
