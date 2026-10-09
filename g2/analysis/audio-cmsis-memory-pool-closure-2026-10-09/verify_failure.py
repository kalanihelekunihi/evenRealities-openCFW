from pathlib import Path
import json,itertools
D=Path(__file__).resolve().parent
exec((D/'verify_constructor.py').read_text().split('rows=[]\ndef compare')[0])
rows=[]
for size,logging in itertools.product([0,192496,0x80000000,0xffffffff],[False,True]):
 c=dict(full_heap=True,full_failure=True,logging=logging,heap_ops=[['alloc',size]])
 o=constructor(False,**c);n=constructor(True,**c);assert o==n,(c,o,n)
 assert o['boundary'][0]['kind']==('before_opaque_formatter' if logging else 'nonreturning_failure_spin')
 rows.append(dict(inputs=c,**o))
(D/'failure-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Actual heap failure callback and disabled logger execute to real self-loop; no allocation return fabricated.','Enabled logger stops before original opaque formatter; formatter and registered sink do not execute or receive fake results.']},indent=2)+'\n');print('PASS',len(rows),'fatal failure/logger-boundary comparisons')
