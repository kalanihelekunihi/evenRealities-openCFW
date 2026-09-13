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
    original=deps['libgcc/fp-bit.c'];start=original.index('FLO_type\nsub (');end=original.index('\n#endif',start)
    source=original[:original.index('#include')]+ '\n#include <stdint.h>\n#include <stddef.h>\ntypedef int CMPtype;\ntypedef double FLO_type;\ntypedef union { double value; uint64_t raw; } FLO_union_type;\ntypedef struct { unsigned classification; unsigned sign; int exponent; union { uint64_t ll; } fraction; } fp_number_type;\n_Static_assert(sizeof(fp_number_type)==20,"parts ABI");\n#define isnan(p) ((p)->classification==0 || (p)->classification==1)\nextern void unpack_d(const FLO_union_type *,fp_number_type *);\nextern const fp_number_type *_fpadd_parts(fp_number_type *,fp_number_type *,fp_number_type *);\nextern double pack_d(const fp_number_type *);\n'+original[start:end]
    out=ROOT/'build/gx8002-subdf3';out.mkdir(exist_ok=True);path=out/'candidate.c';path.write_text(source);(out/'COPYING.RUNTIME').write_text(deps['COPYING.RUNTIME'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x1020a0cc : { *(.text.sub) } }\nunpack_d = 0x1020a704;\n_fpadd_parts = 0x10209dd8;\npack_d = 0x1020a574;\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    r={'upstream_commit':commit,'upstream_sha256':sha(original.encode()),'source_sha256':sha(source.encode()),'runtime_license_sha256':sha(deps['COPYING.RUNTIME'].encode()),'compiled_bytes':len(data),'envelope_bytes':56,'fits':len(data)<=56,'byte_exact':data==IMAGE.read_bytes()[0x13658:0x13690],'compiled_sha256':sha(data),'source_admitted':False,'limits':['Upstream candidate; behavioral and ownership checks outstanding.']}
    (ROOT/'docs/research/gx8002-subdf3-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
