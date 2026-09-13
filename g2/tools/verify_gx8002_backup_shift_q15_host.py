# SPDX-License-Identifier: MIT
"""Native scalar shift checks over all Q15 values and boundary shift counts."""
import ctypes,json,subprocess
from build_gx8002_backup_shift_q15 import build,ROOT,sha

def expected(value,shift):
    if shift<0:
        amount=(0x7fffffff if shift==-0x80000000 else -shift)&31
        return value>>amount
    if shift>=16:return -32768 if value<0 else 32767 if value>0 else 0
    return max(-32768,min(32767,value*(1<<shift)))

def verify():
    provenance=json.loads((ROOT/'docs/research/gx8002-csky-dsp-upstream-evidence.json').read_text())
    for record in provenance['files']:
        assert sha((ROOT/'build/upstream-xuantie-qemu-csky'/record['file']).read_bytes())==record['sha256']
    evidence=build();source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_shift_q15.c'
    path=ROOT/'build/gx8002-backup-shift-q15/shift.dylib'
    subprocess.run(['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(path)],check=True)
    f=ctypes.CDLL(str(path)).open_cfw_gx8002_backup_shift_q15
    ptr=ctypes.POINTER(ctypes.c_int16);f.argtypes=[ptr,ctypes.c_int32,ptr,ctypes.c_uint32];f.restype=None
    values=list(range(-32768,32768));array=ctypes.c_int16*len(values);src=array(*values);dst=array()
    shifts=[-0x80000000,*range(-40,41),0x7fffffff];samples=0;cases=0
    for shift in shifts:
        f(src,shift,dst,len(values));assert list(dst)==[expected(v,shift) for v in values],shift
        assert list(src)==values;samples+=len(values);cases+=1
    for count in range(20):
        for shift in shifts:
            for delta in (-4,0,4):
                vals=[((i*1937)&65535)-32768 for i in range(64)];want=vals[:]
                a,b=8,8+delta
                for _ in range(count//4):
                    block=want[a:a+4];want[b:b+4]=[expected(v,shift) for v in block];a+=4;b+=4
                for _ in range(count&3):want[b]=expected(want[a],shift);a+=1;b+=1
                storage=(ctypes.c_int16*64)(*vals)
                f(ctypes.cast(ctypes.byref(storage,16),ptr),shift,ctypes.cast(ctypes.byref(storage,2*(8+delta)),ptr),count)
                assert list(storage)==want,(count,shift,delta);cases+=1;samples+=count
    f(None,0,None,0);cases+=1
    result={'upstream_semantics_commit':provenance['commit'],'build':evidence,'native_cases':cases,'sample_results_checked':samples,'shift_counts':shifts,'source_admitted':False,'hardware_qualified':False,
            'limits':['Native checks of explicit scalar interpretation including all Q15 inputs, shift boundaries and block-ordered overlap.','Vendor helper uses undefined C shifts for zero with very large positive counts; this implementation defines that result as zero. Hardware semantics for those cases still require qualification.','Target decoded behavior, load/store widths, full shift/count-domain proof and placement pending.']}
    (ROOT/'docs/research/gx8002-backup-shift-q15-host.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['native_cases'],r['sample_results_checked'])
