# SPDX-License-Identifier: MIT
"""Exhaust Q15 magnitudes and exercise maximum reduction and output aliasing."""
import ctypes,json,random,subprocess
from build_gx8002_backup_maxabs_q15 import build,ROOT,sha

def verify():
    evidence=build();provenance=json.loads((ROOT/'docs/research/gx8002-csky-dsp-upstream-evidence.json').read_text())
    record=next(r for r in provenance['files'] if r['file']=='op_dspv2.c')
    vendor=ROOT/'build/upstream-xuantie-qemu-csky/op_dspv2.c';assert sha(vendor.read_bytes())==record['sha256']
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_maxabs_q15.c'
    path=ROOT/'build/gx8002-backup-maxabs-q15/maxabs.dylib'
    subprocess.run(['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(path)],check=True)
    f=ctypes.CDLL(str(path)).open_cfw_gx8002_backup_maxabs_q15
    ptr=ctypes.POINTER(ctypes.c_int16);f.argtypes=[ptr,ptr,ctypes.c_uint32];f.restype=None
    result=ctypes.c_int16();sample=ctypes.c_int16();cases=0
    for value in range(-32768,32768):
        sample.value=value;result.value=-1234;f(ctypes.byref(sample),ctypes.byref(result),1)
        assert result.value==min(abs(value),32767) and sample.value==value;cases+=1
    rng=random.Random(0x47a74)
    for count in range(1,258):
        values=[rng.randrange(-32768,32768) for _ in range(count)]
        for alias in (0,count//2,count-1):
            storage=(ctypes.c_int16*(count+2))(-1234,*values,-2345)
            output=ctypes.cast(ctypes.byref(storage,2*(alias+1)),ptr)
            f(ctypes.cast(ctypes.byref(storage,2),ptr),output,count)
            expected=[-1234,*values,-2345];expected[alias+1]=min(max(map(abs,values)),32767)
            assert list(storage)==expected;cases+=1
    result.value=123;f(None,ctypes.byref(result),0);assert result.value==0;cases+=1
    report={'build':evidence,'native_cases':cases,'exhaustive_single_sample_values':65536,'upstream_semantics':record,'source_admitted':False,'hardware_qualified':False,
            'limits':['All Q15 single values plus bounded random reductions with aliased output and zero-count null input.','Scalar halfword access widths differ from stock grouped loads; normal sample-memory behavior tested, not MMIO. Decoded target equivalence and placement/reference qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-maxabs-q15-host.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['native_cases'],'native cases')
