# SPDX-License-Identifier: MIT
"""Host numerical check of recovered exp C against high-precision Decimal."""
import ctypes,json,math,random,struct,subprocess
from decimal import Decimal,localcontext
from build_gx8002_backup_cfft import ROOT,sha


def bits(x):return struct.unpack('<Q',struct.pack('<d',x))[0]

def verify():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_exp.c'
    out=ROOT/'build/gx8002-exp-host';out.mkdir(exist_ok=True)
    lib=out/'exp.dylib'
    subprocess.run(['clang','-O2','-ffp-contract=off','-fno-builtin','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(lib)],check=True)
    fn=ctypes.CDLL(str(lib)).open_cfw_gx8002_backup_exp;fn.argtypes=[ctypes.c_double];fn.restype=ctypes.c_double
    values=[0.0,-0.0,1.0,-1.0,709.782712893384,-745.1332191019411]
    for center in [2**-28,-2**-28,math.log(2)/2,-math.log(2)/2,1.5*math.log(2),-1.5*math.log(2),709.782712893384,-745.1332191019411]:
        values.append(center)
        for direction in (-math.inf,math.inf):
            x=center
            for _ in range(32):x=math.nextafter(x,direction);values.append(x)
    for k in range(-1075,1025):
        x=k*math.log(2);values.extend([x,math.nextafter(x,-math.inf),math.nextafter(x,math.inf)])
    rng=random.Random(804);values += [rng.uniform(-746,710) for _ in range(10000)]
    worst=0;histogram={};failures=[]
    with localcontext() as ctx:
        ctx.prec=110
        for x in values:
            expected=float(Decimal.from_float(x).exp());actual=fn(x)
            distance=abs(bits(actual)-bits(expected))
            worst=max(worst,distance);histogram[distance]=histogram.get(distance,0)+1
            if not actual>=0 or distance>1:failures.append({'x':x,'actual':actual,'expected':expected,'ulp':distance})
    specials=[(math.inf,math.inf),(-math.inf,0.0)]
    for x,expected in specials:assert bits(fn(x))==bits(expected)
    for raw in [0x7ff8000000000001,0xfff8000000001234,0x7ff0000000000001]:
        x=struct.unpack('<d',struct.pack('<Q',raw))[0];assert math.isnan(fn(x))
    result={'source_sha256':sha(source.read_bytes()),'library_sha256':sha(lib.read_bytes()),'finite_cases':len(values),'special_cases':5,'maximum_ulp_distance':worst,'ulp_histogram':histogram,'failures':failures[:20],
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Host ARM64 arithmetic, round-to-nearest default; Decimal 110-digit exp converted to binary64 oracle. Allows one ULP, not correctly-rounded proof.',
                      'Does not execute target GCC fp-bit helpers or establish stock equivalence, exception flags, all NaN payloads, timing or hardware behavior.']}
    (ROOT/'docs/research/gx8002-exp-host.json').write_text(json.dumps(result,indent=2)+'\n')
    assert not failures,result
    return result
if __name__=='__main__':
    r=verify();print(r['finite_cases'],r['maximum_ulp_distance'])
