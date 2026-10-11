#!/usr/bin/env python3
"""Additional stock/source file-close cases using the prior full TLSF fixture."""
import hashlib,json
from pathlib import Path

D=Path(__file__).resolve().parent
PRIOR=D.parent/'audio-file-close-closure-2026-10-08'/'verify.py'
scope={'__file__':str(PRIOR)}
exec(compile(PRIOR.read_text().split('rows=[]\nfor recursive')[0],str(PRIOR),'exec'),scope)
run=scope['run'];cases=[
 (0,0x100000,'head','thread','valid'),
 (1,0x100000,'second','thread','valid'),
 (0,0x100000,'head','isr','valid'),
 (1,0x100000,'second','null_mutex','valid'),
]
rows=[]
for recursive,flags,position,context,heap_mutex in cases:
 o=run(False,recursive,flags,position,context,heap_mutex)
 n=run(True,recursive,flags,position,context,heap_mutex)
 assert o==n,(recursive,flags,position,context,heap_mutex,o,n)
 rows.append(dict(recursive=recursive,file_flags=flags,position=position,context=context,heap_mutex=heap_mutex,state=o))
(D/'file-close-extra-execution.json').write_text(json.dumps(dict(status='PASS',fresh_cases=len(rows),
 prior_fixture=str(PRIOR.relative_to(scope['root'])),source_elf_sha256=hashlib.sha256(scope['elf'].read_bytes()).hexdigest(),
 cases=rows,limits=['Fresh flag cases reuse the prior full TLSF/static-mutex fixture and prior GCC source ELF; selected Clang source object is separately compared byte-for-byte to its alias rebuild.','Synthetic file and heap; no live media I/O or scheduling.']),indent=2)+'\n')
print('PASS',len(rows),'fresh file-close cases')
