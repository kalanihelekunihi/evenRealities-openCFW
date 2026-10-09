from pathlib import Path
import json,itertools
D=Path(__file__).resolve().parent
exec((D/'verify_constructor.py').read_text().split('rows=[]\ndef compare')[0])
rows=[]
def compare(operations):
 c=dict(full_heap=True,heap_ops=operations);o=constructor(False,**c);n=constructor(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for size in [1,2,3,4,7,8,9,15,16,17,31,32,33,64,116,128,208,4096,192480,192488,192495,192496,0,0x7ffffff0,0x80000000,0xffffffff]:compare([['alloc',size],['free',0]])
for a,b,c,order in itertools.product([1,8,116],[4,16,208],[12,32],[[0,1,2],[2,1,0],[1,0,2],[0,2,1]]):compare([['alloc',a],['alloc',b],['alloc',c]]+[['free',i] for i in order]+[['alloc',a+b+c],['free',3]])
for remainder in [0,8,16,24,32]:compare([['alloc',192504-remainder-16],['free',0]])
compare([['free','null']]);compare([['alloc',116],['free',0],['free',0]]);compare([['init',0]])
(D/'heap-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Stock charged-size arithmetic including strict split>16 and invalid/failure callback entry cuts; no fatal logger or exception delivery executed.','Synthetic isolated free heap and task state; no actual boot heap/lifecycle trace.','Algorithm reused from already recovered bootloader heap helper with independently validated main-image bindings, not first public-source attribution.']},indent=2)+'\n');print('PASS',len(rows),'main heap allocation/coalescing comparisons')
