# SPDX-License-Identifier: MIT
"""Native output and sentinel checks for reconstructed halfword fill."""
import ctypes,json,subprocess
from build_gx8002_backup_fill_q15 import build,ROOT,sha

def verify():
    evidence=build();source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_fill_q15.c'
    path=ROOT/'build/gx8002-backup-fill-q15/fill.dylib'
    subprocess.run(['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(path)],check=True)
    f=ctypes.CDLL(str(path)).open_cfw_gx8002_backup_fill_q15
    f.argtypes=[ctypes.c_uint32,ctypes.POINTER(ctypes.c_int16),ctypes.c_uint32];f.restype=None
    cases=0
    for count in range(1025):
        for value in (0,1,0x7fff,0x8000,0xffff,0x12345678,0x80000000,0xffffffff):
            storage=(ctypes.c_uint32*((count+1)//2+4))()
            ctypes.memset(storage,0xa5,ctypes.sizeof(storage))
            address=ctypes.addressof(storage)+8
            f(value,ctypes.cast(address,ctypes.POINTER(ctypes.c_int16)),count)
            actual=ctypes.string_at(ctypes.addressof(storage),ctypes.sizeof(storage))
            expected=b'\xa5'*8+(value&65535).to_bytes(2,'little')*count+b'\xa5'*(len(actual)-8-count*2)
            assert actual==expected,(count,value)
            cases+=1
    f(0xffffffff,None,0)
    result={'build':evidence,'host_cases':cases+1,'null_zero_count_checked':True,'source_sha256':sha(source.read_bytes()),'source_admitted':False,
            'limits':['macOS clang output and guard-byte checks for counts 0..1024 and eight values. Does not prove target instruction equivalence, store-width trace or enormous-count execution.','C-SKY candidate exceeds original envelope; no firmware replacement.']}
    (ROOT/'docs/research/gx8002-backup-fill-q15-host.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['host_cases'],'native cases')
