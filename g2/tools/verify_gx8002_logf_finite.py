# SPDX-License-Identifier: MIT
"""Execute positive finite logarithm against stock and a Decimal reference."""
import json,subprocess,random,struct
from decimal import Decimal,localcontext
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from gx8002_binary32_rational import operation

def verify():
    path=ROOT/'build/gx8002-log-exp-placed/math.elf';data=path.read_bytes()
    report=json.loads((ROOT/'docs/research/gx8002-log-exp-placed.json').read_text());assert sha(data)==report['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x490a8','--stop-address=0x49300',str(wrapper)],text=True))
    rng=random.Random(8712);values=[(e<<23)|f for e in range(255) for f in (1,0x3fffff,0x400000,0x7fffff)]+[0x3f800000]+[rng.randrange(1,0x7f800000) for _ in range(3000)]
    differences=[];errors=[];max_ulp=0
    value=lambda raw:struct.unpack('<f',struct.pack('<I',raw))[0]
    for raw in values:
        args=[raw]+[0]*15
        actual=execute(source,0x490a8-0x3b940+0x10003000,bytes(20),float_arguments=args,return_float=True,float_operation=operation)
        original=execute(old,0x490a8,bytes(20),float_arguments=args,return_float=True,float_operation=operation)
        with localcontext() as ctx:
            ctx.prec=90;exact=Decimal.from_float(value(raw)).ln()
            center=struct.unpack('<I',struct.pack('<f',float(exact)))[0]
            expected=min(range(max(0,center-1),center+2),key=lambda x:(abs(Decimal.from_float(value(x))-exact),x&1))
        ulp=abs(actual-expected);max_ulp=max(max_ulp,ulp)
        if actual!=original:differences.append({'input':hex(raw),'source':hex(actual),'stock':hex(original)})
        if ulp>1:errors.append({'input':hex(raw),'source':hex(actual),'reference':hex(expected),'ulp':ulp})
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(values),'differences':differences,'max_ulp':max_ulp,'accuracy_errors':errors,'source_admitted':False,'limits':['Positive finite sample with 90-digit Decimal reference. Explicit finite nearest-even arithmetic and separately rounded accumulates; hardware status, special values and integration pending.']}
    (ROOT/'docs/research/gx8002-logf-finite.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['cases'],len(r['differences']),r['max_ulp'],r['accuracy_errors'][:3])
