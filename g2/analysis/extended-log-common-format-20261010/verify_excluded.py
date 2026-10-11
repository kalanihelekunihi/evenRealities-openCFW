import hashlib,itertools,json
from pathlib import Path
import verify

HERE=Path(__file__).resolve().parent
cases=[
    (0x783550,[(0,),(ord('A'),),(0xff,)]),
    (0x715ca0,[('',ord('A')),('state',ord('Z'))]),
    (0x718b44,[(0,),(1,),(0xffffffff,)]),
    (0x7258e8,[(0,0,5),(1,0,1),(0,1,100),(0xffffffff,0xffffffff,0xffffffff)]),
    (0x6de254,[(1,2,3,4,0,0,5),(1,2,3,4,0xffffffff,0xffffffff,5),
                (1,2,3,4,0,0x80000000,5)]),
    (0x72c9c0,[()]),
]
total=0;selected=[]
for fmt,vectors in cases:
    selected.append({'address':hex(fmt),'text':verify.signature(fmt)})
    for values,capacity in itertools.product(vectors,[0,1,8,32,128,1024]):
        a=verify.run(True,fmt,capacity,values)
        b=verify.run(False,fmt,capacity,values)
        assert a==b,(hex(fmt),capacity,values,a[0],b[0],a[1][:150],b[1][:150])
        total+=1
receipt={'status':'PASS','comparisons':total,'formats':selected,
         'source_sha256':hashlib.sha256(verify.src.read_bytes()).hexdigest(),
         'image_sha256':hashlib.sha256(verify.raw).hexdigest(),
         'limit':'Sampled %c, %zu, %llu, %lld conversions; no whole-call ABI or float claim'}
(HERE/'excluded_results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'status':'PASS','comparisons':total}))
