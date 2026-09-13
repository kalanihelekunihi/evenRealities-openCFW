# SPDX-License-Identifier: MIT
"""Compile authenticated GCC double division with runtime provenance."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    gcc=ROOT/'build/upstream-csky-toolchain-build/gcc';commit='1e9b70447a8417f5c692370de4533e43d754e8fa';deps={}
    for name in ('libgcc/fp-bit.c','COPYING.RUNTIME'):
        blob=subprocess.check_output(['git','-C',str(gcc),'rev-parse',commit+':'+name],text=True).strip();deps[name]=authenticated_blob(gcc/name,blob).decode()
    original=deps['libgcc/fp-bit.c'];start=original.index('static inline __attribute__ ((__always_inline__)) const fp_number_type *\n_fpdiv_parts');end=original.index('\n#endif /* L_div_sf',start)
    source=original[:original.index('#include')]+ '\n#include <stdint.h>\ntypedef uint64_t fractype;\ntypedef union { double value; uint64_t value_raw; } FLO_union_type;\ntypedef struct { unsigned class; unsigned sign; int normal_exp; union { uint64_t ll; } fraction; } fp_number_type;\n_Static_assert(sizeof(fp_number_type)==20,"parts ABI");\ntypedef double FLO_type;\ntypedef uint32_t USItype;\ntypedef uint64_t UDItype;\n#define BITS_PER_SI 32\n#define FRAC_NBITS 64\n#define FRACHIGH (UINT64_C(1)<<63)\n#define IMPLICIT_2 (UINT64_C(1)<<61)\n#define GARDMASK 255\n#define GARDMSB 128\n#define GARDROUND 127\n#define isnan(p) ((p)->class<2)\n#define isinf(p) ((p)->class==4)\n#define iszero(p) ((p)->class==2)\nextern const fp_number_type open_cfw_nan;\n#define makenan() (&open_cfw_nan)\nextern void unpack_d(FLO_union_type *,fp_number_type *);\nextern double pack_d(const fp_number_type *);\n#define FRACBITS 52\n#define EXPBITS 11\n#define EXPBIAS 1023\n#define EXPMAX 2047\n#define NGARDS 8\n#define IMPLICIT_1 (UINT64_C(1)<<60)\n#define QUIET_NAN (UINT64_C(1)<<51)\n#define CLASS_SNAN 0\n#define CLASS_QNAN 1\n#define CLASS_ZERO 2\n#define CLASS_NUMBER 3\n#define CLASS_INFINITY 4\n'+original[start:end]
    begin=source.index('    if ((quotient & GARDMASK) == GARDMSB)')
    end=source.index('    a->fraction.ll = quotient;',begin)
    source=source[:begin]+'    quotient |= (numerator != 0);\n'+source[end:]
    out=ROOT/'build/gx8002-divdf3-fixed';out.mkdir(exist_ok=True);path=out/'candidate.c';path.write_text(source);(out/'COPYING.RUNTIME').write_text(deps['COPYING.RUNTIME'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x1020a308 : { *(.text.divide) } }\nunpack_d = 0x1020a704;\npack_d = 0x1020a574;\nopen_cfw_nan = 0x1020bd08;\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    r={'upstream_commit':commit,'upstream_sha256':sha(original.encode()),'source_sha256':sha(source.encode()),'runtime_license_sha256':sha(deps['COPYING.RUNTIME'].encode()),'compiled_bytes':len(data),'envelope_bytes':280,'fits':len(data)<=280,'byte_exact':data==IMAGE.read_bytes()[0x13894:0x139ac],'compiled_sha256':sha(data),'adaptations':['Preserve nonzero division remainder as sticky information; defer rounding until pack_d.'],'source_admitted':False,'limits':['Upstream candidate; behavioral and ownership checks outstanding.']}
    (ROOT/'docs/research/gx8002-divdf3-fixed-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
