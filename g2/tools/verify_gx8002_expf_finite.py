# SPDX-License-Identifier: MIT
"""Execute finite-input exponential against stock and a Decimal reference."""
import json,subprocess,random,struct
from decimal import Decimal,localcontext
from collections import Counter
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
    source=decode(subprocess.check_output([pre,'-d',str(path)],text=True));old=decode(subprocess.check_output([pre,'-D','--start-address=0x49300','--stop-address=0x4950c',str(wrapper)],text=True))
    source_elf=Elf32(data,'source')
    source_memory={sec['address']+i:b for sec in source_elf.sections if sec['flags']&2 and sec['size'] for i,b in enumerate(source_elf.contents(sec))}
    stock_memory={0x10003000+i:b for i,b in enumerate(stock[0x3b940:0x4f9cc])}
    rng=random.Random(9332)
    values=[struct.unpack('<I',struct.pack('<f',x))[0] for x in [i/16 for i in range(-1280,1281)]+[rng.uniform(-80,80) for _ in range(1000)]]
    values += [center+delta for center in (0x42b17217,0xc2cff1b5,0xc2aeac50) for delta in range(-64,65)]
    differences=[];errors=[];max_ulp=0;classes=Counter()
    value=lambda raw:struct.unpack('<f',struct.pack('<I',raw))[0]
    for raw in values:
        args=[raw]+[0]*15
        actual=execute(source,0x49300-0x3b940+0x10003000,bytes(20),float_arguments=args,return_float=True,float_operation=operation,readonly=source_memory)
        original=execute(old,0x49300,bytes(20),float_arguments=args,return_float=True,float_operation=operation,readonly=stock_memory)
        with localcontext() as ctx:
            ctx.prec=90;exact=Decimal.from_float(value(raw)).exp()
            overflow=Decimal(2)**128-Decimal(2)**103
            if exact>=overflow:expected=0x7f800000
            else:
                try:center=struct.unpack('<I',struct.pack('<f',float(exact)))[0]
                except OverflowError:center=0x7f7fffff
                expected=min(range(max(0,center-1),min(0x7f7fffff,center+1)+1),key=lambda x:(abs(Decimal.from_float(value(x))-exact),x&1))
        classify=lambda x: 'zero' if x==0 else 'infinite' if x==0x7f800000 else 'subnormal' if x<0x800000 else 'normal'
        assert classify(actual)==classify(expected),(hex(raw),hex(actual),hex(expected))
        classes[classify(actual)]+=1
        ulp=abs(actual-expected);max_ulp=max(max_ulp,ulp)
        if actual!=original:differences.append({'input':hex(raw),'source':hex(actual),'stock':hex(original)})
        if ulp>1:errors.append({'input':hex(raw),'source':hex(actual),'reference':hex(expected),'ulp':ulp})
    result={'elf_sha256':sha(data),'stock_sha256':IMAGE_SHA,'cases':len(values),'differences':differences,'max_ulp':max_ulp,'result_classes':dict(classes),'accuracy_errors':errors,'source_admitted':False,'limits':['Finite inputs -80..80 plus threshold neighborhoods with 90-digit Decimal reference. Explicit finite nearest-even arithmetic and separately rounded accumulates; hardware status, special values and integration pending.']}
    (ROOT/'docs/research/gx8002-expf-finite.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['cases'],len(r['differences']),r['max_ulp'],r['accuracy_errors'][:3])
