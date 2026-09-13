# SPDX-License-Identifier: MIT
"""Compile authenticated GCC floating addition core with runtime provenance."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    gcc=ROOT/'build/upstream-csky-toolchain-build/gcc';commit='1e9b70447a8417f5c692370de4533e43d754e8fa';deps={}
    for name in ('libgcc/fp-bit.c','COPYING.RUNTIME'):
        blob=subprocess.check_output(['git','-C',str(gcc),'rev-parse',commit+':'+name],text=True).strip();deps[name]=authenticated_blob(gcc/name,blob).decode()
    original=deps['libgcc/fp-bit.c'];start=original.index('_fpadd_parts (');end=original.index('\n#endif',start)
    # First endif closes the disabled NaN block, so take the function terminator.
    end=original.index('\nFLO_type\nadd (',start)
    source=original[:original.index('#include')]+ '\n#include <stdint.h>\ntypedef struct { unsigned class; unsigned sign; int normal_exp; union { uint64_t ll; } fraction; } fp_number_type;\n_Static_assert(sizeof(fp_number_type)==20,"parts ABI");\n#define isnan(p) ((p)->class==0 || (p)->class==1)\n#define isinf(p) ((p)->class==4)\n#define iszero(p) ((p)->class==2)\ntypedef int64_t intfrac;\ntypedef uint64_t fractype;\n#define FRAC_NBITS 64\n#define IMPLICIT_1 (UINT64_C(1)<<60)\n#define IMPLICIT_2 (UINT64_C(1)<<61)\n#define CLASS_NUMBER 3\n#define LSHIFT(a,s) { a = (a >> s) | !!(a & (((fractype)1 << s) - 1)); }\nconst fp_number_type open_cfw_nan = {0,0,0,{0}};\n#define makenan() (&open_cfw_nan)\nconst fp_number_type *\n'+original[start:end]
    source=source.replace('#define LSHIFT(a,s) { a = (a >> s) | !!(a & (((fractype)1 << s) - 1)); }', """static inline __attribute__((always_inline)) uint64_t shift_sticky(uint64_t value, unsigned count) {
    /* Callers supply 1..63; zero exponent gaps never shift. */
    uint32_t lo=(uint32_t)value, hi=(uint32_t)(value>>32), sticky;
    if (count >= 32) {
        unsigned tail=count-32;
        sticky=lo != 0;
        if (tail) sticky |= (hi << (32-tail)) != 0;
        lo=(hi >> tail) | sticky; hi=0;
    } else {
        sticky=(lo << (32-count)) != 0;
        lo=(lo >> count) | (hi << (32-count)) | sticky;
        hi >>= count;
    }
    return ((uint64_t)hi<<32)|lo;
}
#define LSHIFT(a,s) { a = shift_sticky(a,s); }""")
    out=ROOT/'build/gx8002-fpadd_parts';out.mkdir(exist_ok=True);path=out/'candidate.c';path.write_text(source);(out/'COPYING.RUNTIME').write_text(deps['COPYING.RUNTIME'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-O2',*FLAGS[1:],'-fno-tree-ter']
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x10209dd8 : { *(.text._fpadd_parts) } .rodata.nan 0x1020bd08 : { *(.rodata.open_cfw_nan) } }\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    r={'upstream_commit':commit,'upstream_sha256':sha(original.encode()),'source_sha256':sha(source.encode()),'runtime_license_sha256':sha(deps['COPYING.RUNTIME'].encode()),'compiled_bytes':len(data),'envelope_bytes':708,'fits':len(data)<=708,'byte_exact':data==IMAGE.read_bytes()[0x13364:0x13628],'compiled_sha256':sha(data),'compiler_flags':flags,'adaptations':['Split positive-count 64-bit sticky shifts into bounded 32-bit operations.'],'protected_next_entry':{'package_offset':0x13628,'symbol':'__adddf3'},'source_admitted':False,'limits':['Upstream candidate; behavioral and ownership checks outstanding.']}
    (ROOT/'docs/research/gx8002-fpadd_parts-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
