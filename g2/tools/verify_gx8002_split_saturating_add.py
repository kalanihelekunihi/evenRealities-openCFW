# SPDX-License-Identifier: MIT
"""Native boundary/random checks of the split helper against widened arithmetic."""
import ctypes,json,random,subprocess
from build_gx8002_backup_split import ROOT,sha

def verify():
    out=ROOT/'build/gx8002-split-saturation-probe';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_split.c'
    harness='#include "'+str(source)+'"\nint32_t check_add(int32_t a,int32_t b) {return add_sat(a,b);}\n'
    (out/'boundary.c').write_text(harness);path=out/'boundary.dylib'
    subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(out/'boundary.c'),'-o',str(path)],check=True)
    lib=ctypes.CDLL(str(path));fn=lib.check_add;fn.argtypes=[ctypes.c_int32,ctypes.c_int32];fn.restype=ctypes.c_int32
    edges=(-2147483648,-2147483647,-1073741824,-65536,-32768,-1,0,1,32767,65535,1073741824,2147483646,2147483647)
    pairs=[(a,b) for a in edges for b in edges]
    # Sweep additions immediately below, at and above each saturation threshold.
    for a in range(-32768,32768):
        for limit in (-2147483648,2147483647):
            for delta in (-1,0,1):
                b=limit-a+delta
                if -2147483648<=b<=2147483647:pairs.append((a,b))
    rng=random.Random(0xadd32)
    pairs.extend((rng.randrange(-2147483648,2147483648),rng.randrange(-2147483648,2147483648)) for _ in range(10000))
    for a,b in pairs:assert fn(a,b)==max(-2147483648,min(2147483647,a+b)),(a,b)
    report={'source_sha256':sha(source.read_bytes()),'native_cases':len(pairs),'limits':['Native compiled helper versus widened integer arithmetic; boundary sweeps and random pairs are finite, not exhaustive 64-bit input-pair enumeration. Linked C-SKY transform verification is separate.']}
    (ROOT/'docs/research/gx8002-split-saturating-add-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['native_cases'])
