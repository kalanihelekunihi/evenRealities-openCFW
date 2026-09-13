# SPDX-License-Identifier: MIT
"""Native radix-4 invariants; not a replacement for decoded stock comparison."""
import ctypes,json,subprocess
from build_gx8002_backup_radix4 import build,ROOT,sha
from generate_gx8002_backup_math_tables import coefficients

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-radix4';source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4.c'
    libs=[]
    for inverse in (0,1):
        path=out/('host-'+str(inverse)+'.dylib')
        subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror','-dynamiclib','-DINVERSE='+str(inverse),str(source),'-o',str(path)],check=True)
        libs.append(ctypes.CDLL(str(path)))
    raw=coefficients(complex_fft=True)
    # The generator returns coefficient words and its rounding margin.
    values=raw[0] if isinstance(raw,tuple) else raw
    table=(ctypes.c_int16*len(values))(*values);cases=0
    for inverse,lib in enumerate(libs):
        fn=getattr(lib,'open_cfw_gx8002_backup_radix4'+('_inverse' if inverse else ''))
        fn.argtypes=[ctypes.POINTER(ctypes.c_int16),ctypes.c_uint,ctypes.POINTER(ctypes.c_int16),ctypes.c_uint]
        for length in (16,64,256):
            for real,imag in ((0,0),(1024,0),(0,1024),(-1024,1024),(32764,-32768),(-32768,32764),(1001,-1001)):
                data=(ctypes.c_int16*(2*length))(*([real,imag]*length))
                fn(data,length,table,256//length)
                expected=[(real>>2)*4,(imag>>2)*4]+[0]*(2*length-2)
                assert list(data)==expected,(inverse,length,real,imag,list(data)[:8])
                cases+=1
    report={'build':evidence,'constant_transform_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Native forward/inverse constant complex inputs yield only DC, including first-stage truncation; not arbitrary-input FFT or decoded target proof.','Lengths 16,64,256 use generated 256-point coefficients and stride 16,4,1. Full buffer output checked.','Candidate exceeds original placement; no firmware integration.']}
    (ROOT/'docs/research/gx8002-backup-radix4-host-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['constant_transform_cases'])
