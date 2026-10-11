#!/usr/bin/env python3
"""Additional original/source CMSIS mutex-release states using prior oracle."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
PRIOR=D.parent/'audio-semaphore-take-closure-2026-10-09'/'verify_recursive.py'
scope={'__file__':str(PRIOR)}
exec(compile(PRIOR.read_text().split("for kind in ['recursive_take'")[0],str(PRIOR),'exec'),scope)
compare=scope['compare'];rows=scope['rows']
for tagged in (False,True):
 for depth in (1,2):
  for held in (2,3):
   compare(dict(kind='mutex_release',size=0,tagged=tagged,owner_current=True,held=held,recursive_depth=depth))
(D/'mutex-release-extra-execution.json').write_text(json.dumps(dict(status='PASS',fresh_cases=len(rows),
 prior_fixture=str(PRIOR.relative_to(scope['R'])),source_elf_sha256=hashlib.sha256(scope['elf'].read_bytes()).hexdigest(),cases=rows,
 limits=['Fresh held-count states reuse prior GCC source ELF and complete synthetic queue/task fixture; selected Clang source object compared separately to alias rebuild.','No live task scheduling.']),indent=2)+'\n')
print('PASS',len(rows),'fresh mutex-release cases')
