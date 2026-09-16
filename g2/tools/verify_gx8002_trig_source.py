# SPDX-License-Identifier: MIT
"""Compare decoded stock/source trig kernels with a high precision Taylor oracle."""
import json,subprocess,math
from decimal import Decimal,localcontext
from build_gx8002_backup_cfft import ROOT,sha,Elf32,IMAGE,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute
from verify_gx8002_double_addsub_target import bits


def reference(name,x,y=0.0):
    with localcontext() as ctx:
        ctx.prec=90
        d=Decimal.from_float(x)+Decimal.from_float(y);term=d if name=='sin' else Decimal(1);total=term
        for n in range(1,70):
            term *= -d*d/Decimal((2*n)*(2*n+1) if name=='sin' else (2*n-1)*(2*n))
            total += term
        return bits(float(total))


def verify(tails=False,loops=False,placed_sine=False,placed_cosine=False):
    assert not (placed_sine and placed_cosine)
    stem='gx8002-cosine-placed' if placed_cosine else 'gx8002-sine-placed' if placed_sine else 'gx8002-trig-loop-closure' if loops else 'gx8002-trig-source-closure'
    path=ROOT/'build'/stem/('cosine.elf' if placed_cosine else 'sine.elf' if placed_sine else 'trig.elf')
    report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text())
    assert sha(path.read_bytes())==report['elf_sha256']
    elf=Elf32(path.read_bytes(),'trig');pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([pre,'-d',str(path)],text=True))
    memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';se=Elf32(wrapper.read_bytes(),'stock')
    assert se.contents(next(s for s in se.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x49890','--stop-address=0x4b238',str(wrapper)],text=True))
    sm={base+i:b for base in (0x10003000,0x20003000) for i,b in enumerate(stock[0x3b940:0x4f9cc])}
    # Fifth integer ABI argument iy resides at the incoming stack pointer.
    memory.update({0x8000+i:0 for i in range(4)});sm.update({0x8000+i:0 for i in range(4)})
    samples=[(index/128,0.0,0) for index in range(-100,101)]
    if tails:
        points=[index/128 for index in range(-100,101) if index]
        for boundary in (2.0**-27,0.3,0.78125,math.pi/4):
            for value in (math.nextafter(boundary,0.0),boundary,math.nextafter(boundary,math.inf)):
                points.extend((value,-value))
        samples=[(x,direction*math.ulp(x)/4,1) for x in points for direction in (-1,1)]
    results={}
    entries=[('cos',0x499ac+0x10003000-0x3b940,0x499ac)] if placed_cosine else [('sin',0x49890+0x10003000-0x3b940,0x49890)] if placed_sine else [('sin',0x10018000,0x49890),('cos',0x10018200,0x499ac)]
    for name,entry,original_entry in entries:
        differences=[];errors=[];maximum=[0,0]
        for x,y,iy in samples:
            xb=bits(x);yb=bits(y);args=[xb&0xffffffff,xb>>32,yb&0xffffffff,yb>>32]
            memory[0x8000]=iy;sm[0x8000]=iy
            values=[execute(c,e,bytes(20),arguments=args,readonly=m,return_pair=True,max_steps=100000) for c,e,m in [(code,entry,memory),(old,original_entry,sm)]]
            expected=reference(name,x,y)
            ulps=[abs(v-expected) for v in values]
            maximum=[max(a,b) for a,b in zip(maximum,ulps)]
            if values[0]!=values[1]:differences.append({'x':hex(xb),'tail':hex(yb),'iy':iy,'source':hex(values[0]),'stock':hex(values[1]),'reference':hex(expected)})
            if ulps[0]>1:errors.append({'x':hex(xb),'tail':hex(yb),'source_ulp_error':ulps[0]})
        results[name]={'cases':len(samples),'maximum_ulp_error_source_stock':maximum,'stock_differences':differences,'source_accuracy_errors_over_one_ulp':errors}
    result={'placed_cosine':placed_cosine,'placed_sine':placed_sine,'loops':loops,'nonzero_tails':tails,'source_elf_sha256':report['elf_sha256'],'stock_sha256':IMAGE_SHA,'results':results,'source_admitted':False,'limits':['Reduced interval grid; optional quarter-ULP nonzero tails with sine iy=1 and neighboring branch-boundary inputs. Decimal 90-digit Taylor reference of exact x+y. Reports differences, does not assert universal accuracy or correct rounding. Exceptional inputs, full reducer contract, placement and hardware pending.']}
    (ROOT/'docs/research'/(('gx8002-cosine-placed' if placed_cosine else 'gx8002-sine-placed' if placed_sine else 'gx8002-trig')+('-loop' if loops else '')+('-tail' if tails else '')+'-source.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    print({k:{'cases':v['cases'],'max_ulp':v['maximum_ulp_error_source_stock'],'differences':len(v['stock_differences'])} for k,v in verify()['results'].items()})
