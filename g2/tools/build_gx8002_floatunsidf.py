# SPDX-License-Identifier: MIT
"""Compile authenticated GCC unsigned-double conversion with runtime provenance."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    gcc=ROOT/'build/upstream-csky-toolchain-build/gcc';commit='1e9b70447a8417f5c692370de4533e43d754e8fa';deps={}
    for name in ('libgcc/fp-bit.c','COPYING.RUNTIME'):
        blob=subprocess.check_output(['git','-C',str(gcc),'rev-parse',commit+':'+name],text=True).strip();deps[name]=authenticated_blob(gcc/name,blob).decode()
    original=deps['libgcc/fp-bit.c'];start=original.index('FLO_type\nusi_to_float (');end=original.index('\n}\n#endif',start)+2
    source=original[:original.index('#include')]+ '\n#include <stdint.h>\ntypedef uint64_t fractype;\ntypedef union { double value; uint64_t value_raw; } FLO_union_type;\ntypedef struct { unsigned class; unsigned sign; int normal_exp; union { uint64_t ll; } fraction; } fp_number_type;\n_Static_assert(sizeof(fp_number_type)==20,"parts ABI");\ntypedef double FLO_type;\ntypedef uint32_t USItype;\n#define BITS_PER_SI 32\n#define clzusi(x) __builtin_clz(x)\nextern double pack_d(fp_number_type *);\n#define FRACBITS 52\n#define EXPBITS 11\n#define EXPBIAS 1023\n#define EXPMAX 2047\n#define NGARDS 8\n#define IMPLICIT_1 (UINT64_C(1)<<60)\n#define QUIET_NAN (UINT64_C(1)<<51)\n#define CLASS_SNAN 0\n#define CLASS_QNAN 1\n#define CLASS_ZERO 2\n#define CLASS_NUMBER 3\n#define CLASS_INFINITY 4\n'+original[start:end]
    out=ROOT/'build/gx8002-floatunsidf';out.mkdir(exist_ok=True);path=out/'candidate.c';path.write_text(source);(out/'COPYING.RUNTIME').write_text(deps['COPYING.RUNTIME'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-O2',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x1020a4d0 : { *(.text.usi_to_float) } }\npack_d = 0x1020a574;\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    r={'upstream_commit':commit,'upstream_sha256':sha(original.encode()),'source_sha256':sha(source.encode()),'runtime_license_sha256':sha(deps['COPYING.RUNTIME'].encode()),'compiled_bytes':len(data),'envelope_bytes':88,'fits':len(data)<=88,'byte_exact':data==IMAGE.read_bytes()[0x13a5c:0x13ab4],'compiled_sha256':sha(data),'source_admitted':False,'limits':['Upstream candidate; behavioral and ownership checks outstanding.']}
    (ROOT/'docs/research/gx8002-floatunsidf-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
