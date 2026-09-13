# SPDX-License-Identifier: MIT
"""Check Q15 copy output including block-ordered overlap effects on macOS."""
import ctypes,json,random,subprocess
from build_gx8002_backup_copy_q15 import build,ROOT

def verify():
    evidence=build();source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_copy_q15.c'
    path=ROOT/'build/gx8002-backup-copy-q15/copy.dylib'
    subprocess.run(['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(path)],check=True)
    f=ctypes.CDLL(str(path)).open_cfw_gx8002_backup_copy_q15
    ptr=ctypes.POINTER(ctypes.c_int16);f.argtypes=[ptr,ptr,ctypes.c_uint32];f.restype=None
    rng=random.Random(0x47ac0);cases=0
    for count in range(257):
        for delta in (*range(-32,33,4),1024):
            source_offset=64;dest_offset=source_offset+delta
            original=bytes(rng.randrange(256) for _ in range(2048));expected=bytearray(original)
            a,b=source_offset,dest_offset
            for _ in range(count//4):
                first=bytes(expected[a:a+4]);second=bytes(expected[a+4:a+8])
                expected[b:b+4]=first;expected[b+4:b+8]=second;a+=8;b+=8
            for _ in range(count&3):
                value=bytes(expected[a:a+2]);expected[b:b+2]=value;a+=2;b+=2
            storage=(ctypes.c_uint32*512).from_buffer_copy(original);base=ctypes.addressof(storage)
            f(ctypes.cast(base+source_offset,ptr),ctypes.cast(base+dest_offset,ptr),count)
            assert bytes(storage)==expected,(count,delta)
            cases+=1
    f(None,None,0)
    report={'build':evidence,'native_cases':cases+1,'null_zero_count_checked':True,'source_admitted':False,'hardware_qualified':False,
            'limits':['Native output against ordered block-copy model for counts 0..256 and 18 overlap/separate-buffer placements. Entire allocation compared for unintended changes.','Target instruction/read-write trace qualification and layout pending. Not memmove semantics.']}
    (ROOT/'docs/research/gx8002-backup-copy-q15-host.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['native_cases'],'native overlap cases')
