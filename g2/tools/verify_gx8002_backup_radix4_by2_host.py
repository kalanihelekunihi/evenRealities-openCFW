# SPDX-License-Identifier: MIT
"""Native C arithmetic comparison with packed-lane instruction reference.

This does not execute the C-SKY candidate or lower radix-4 butterflies.
"""
import ctypes,json,random,subprocess
from build_gx8002_backup_radix4_by2 import build,ROOT,sha

def s16(v):return (v&65535)-65536 if v&32768 else v&65535

def packed_half(v):return ((s16(v)>>1)&65535)|(((s16(v>>16)>>1)&65535)<<16)

def reference(values,coefficients,inverse):
    words=[(values[i]&65535)|((values[i+1]&65535)<<16) for i in range(0,len(values),2)]
    half=len(words)//2
    for i in range(half):
        a=packed_half(words[i]);b=packed_half(words[i+half])
        alo,ahi=s16(a),s16(a>>16);blo,bhi=s16(b),s16(b>>16)
        diff=((alo-blo)&65535)|(((ahi-bhi)&65535)<<16)
        summed=(((alo+blo)>>1)&65535)|((((ahi+bhi)>>1)&65535)<<16)
        x,y=s16(diff),s16(diff>>16);c,s=coefficients[2*i:2*i+2]
        p0,p1=x*c,y*s;q0,q1=x*s,y*c
        real=(p0-p1 if inverse else p0+p1)&0xffffffff
        imag=(q1+q0 if inverse else q1-q0)&0xffffffff
        words[i]=summed;words[i+half]=(real>>16)|((imag>>16)<<16)
    # No-op lower transform stubs isolate first-stage arithmetic and final scaling.
    return [s16((w>>shift)*2) for w in words for shift in (0,16)]

def verify():
    evidence=build();out=ROOT/'build/gx8002-backup-radix4-by2';source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4_by2.c'
    harness='''#include <stdint.h>
static int16_t *base; static const int16_t *twiddle;
static unsigned count, errors, n, wanted_inverse;
void reset(int16_t *p,const int16_t *q,unsigned size,unsigned inverse) {base=p;twiddle=q;n=size;wanted_inverse=inverse;count=errors=0;}
static void call(int16_t *p,unsigned half,const int16_t *q,unsigned stride,unsigned inverse) {
 if(count>1 || p!=base+(count?n:0) || half!=(n>>1) || q!=twiddle || stride!=2 || inverse!=wanted_inverse) errors++;
 count++;
}
void backup_radix4(int16_t *p,unsigned h,const int16_t *q,unsigned s) {call(p,h,q,s,0);}
void backup_radix4_inverse(int16_t *p,unsigned h,const int16_t *q,unsigned s) {call(p,h,q,s,1);}
unsigned good(void) {return count==2 && !errors;}
'''
    (out/'host-harness.c').write_text(harness)
    for inv in (0,1):
        subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror','-fPIC','-DINVERSE='+str(inv),'-c',str(source),'-o',str(out/('host-'+str(inv)+'.o'))],check=True)
    path=out/'host.dylib';subprocess.run(['clang','-dynamiclib',str(out/'host-0.o'),str(out/'host-1.o'),str(out/'host-harness.c'),'-o',str(path)],check=True)
    lib=ctypes.CDLL(str(path));ptr=ctypes.POINTER(ctypes.c_int16)
    lib.reset.argtypes=[ptr,ptr,ctypes.c_uint,ctypes.c_uint];lib.good.restype=ctypes.c_uint
    rng=random.Random(0x47bf4);cases=0;edge=(-32768,-32767,-1,0,1,32766,32767)
    for inverse in (0,1):
      fn=getattr(lib,'open_cfw_gx8002_backup_radix4_by2'+('_inverse' if inverse else ''));fn.argtypes=[ptr,ctypes.c_uint,ptr]
      for length in (2,4,16,32,128,512,2048):
       for trial in range(100):
        values=[edge[(i+trial)%len(edge)] if trial<7 else rng.randrange(-32768,32768) for i in range(2*length)]
        coefficients=[edge[(i+trial*3)%len(edge)] if trial<7 else rng.randrange(-32768,32768) for i in range(length)]
        data=(ctypes.c_int16*len(values))(*values);coeff=(ctypes.c_int16*len(coefficients))(*coefficients)
        lib.reset(data,coeff,length,inverse);fn(data,length,coeff)
        assert lib.good() and list(data)==reference(values,coefficients,inverse),(inverse,length,trial)
        assert list(coeff)==coefficients
        cases+=1
    report={'build':evidence,'native_arithmetic_cases':cases,'harness_sha256':sha(harness.encode()),'source_admitted':False,'hardware_qualified':False,
            'limits':['Native macOS C execution compared against packed-lane reference with no-op lower radix-4 helpers; not decoded C-SKY equivalence.','Checks complete sample buffers, unchanged coefficients and both helper call arguments. Valid disjoint buffers and even lengths only.','Candidate placement exceeds original envelopes; lower radix-4 arithmetic still retained.']}
    (ROOT/'docs/research/gx8002-backup-radix4-by2-host-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['native_arithmetic_cases'])
