import hashlib,itertools,json
import verify
from pathlib import Path

HERE=Path(__file__).resolve().parent
cases=[
    (0x78ca3c,[(0,),(1,),(15,),(0xab,),(0x1234,)]),
    (0x77de20,[(0,),(1,),(0xab,),(0xdeadbeef,)]),
    (0x725bc0,[(0,''),(42,'A'),(0xffffffff,'X'*32)]),
    (0x749e34,[(0,0,''),(5,3,'abcdef'),(0xffffffff,0,'abc'),(20,0xffffffff,'abcd')]),
    (0x77505c,[(0,),(1,),(0xffffffff,)]),
    (0x752424,[(0,0),(1,0xff),(0xdeadbeef,0x20001000)]),
    (0x771a64,[(0,'',''),(1,'ABC','X'),(0xffffffff,'A'*32,'Y')]),
    (0x72d3e8,[(0,0,0,0),(1,0x1234,23,0x20001000),(0xffffffff,0xdeadbeef,0x80000000,0xffffffff)]),
]
total=0; selected=[]
for fmt,vectors in cases:
    selected.append({'address':hex(fmt),'text':verify.signature(fmt)})
    for values,capacity in itertools.product(vectors,[0,1,2,8,32,128,1024]):
        a=verify.run(True,fmt,capacity,values)
        b=verify.run(False,fmt,capacity,values)
        assert a==b,(hex(fmt),capacity,values,a[0],b[0],a[1][:120],b[1][:120])
        total+=1
src=verify.src
receipt={'status':'PASS','comparisons':total,'formats':selected,
         'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'image_sha256':hashlib.sha256(verify.raw).hexdigest(),
         'limit':'Selected stock width/precision/length/flag literals and argument vectors only'}
(HERE/'width_results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','comparisons':total}))
