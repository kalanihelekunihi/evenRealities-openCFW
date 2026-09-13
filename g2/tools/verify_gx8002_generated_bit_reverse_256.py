# SPDX-License-Identifier: MIT
"""Exhaust every sample position of the table-free CFFT256 specialization."""
import ctypes,json,subprocess
from build_gx8002_backup_cfft import ROOT,sha

def verify():
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_bit_reverse_256.c'
    out=ROOT/'build/gx8002-generated-bit-reverse-256';out.mkdir(exist_ok=True)
    library=out/'reverse.dylib'
    subprocess.run(['clang','-std=c99','-O2','-Wall','-Wextra','-Werror','-dynamiclib',str(source),'-o',str(library)],check=True)
    function=ctypes.CDLL(str(library)).open_cfw_gx8002_backup_bit_reverse
    function.argtypes=[ctypes.POINTER(ctypes.c_int16),ctypes.c_uint,ctypes.POINTER(ctypes.c_uint16)]
    function.restype=None
    # Unique real/imaginary labels expose every destination and lane ordering.
    values=list(range(512));samples=(ctypes.c_int16*512)(*values)
    function(samples,240,None)
    permutation=[int(f'{i:08b}'[::-1],2) for i in range(256)]
    expected=[values[2*permutation[i]+lane] for i in range(256) for lane in (0,1)]
    assert list(samples)==expected
    function(samples,240,None);assert list(samples)==values
    result={'source_sha256':sha(source.read_bytes()),'host':'macOS clang','positions_checked':512,'involution_checked':True,'null_table_checked':True,'scope':'Immutable CFFT256 descriptor in source RFFT512 cluster only; not arbitrary table semantics.','source_admitted':False}
    (ROOT/'docs/research/gx8002-generated-bit-reverse-256-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':print(json.dumps(verify(),indent=2))
