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
    original=deps['libgcc/fp-bit.c'];start=original.index('FLO_type\npack_d (');end=original.index('\n}\n#endif',start)+2
    source=original[:original.index('#include')]+ '\n#include <stdint.h>\ntypedef uint64_t fractype;\ntypedef union { double value; uint64_t value_raw; } FLO_union_type;\ntypedef struct { unsigned class; unsigned sign; int normal_exp; union { uint64_t ll; } fraction; } fp_number_type;\n_Static_assert(sizeof(fp_number_type)==20,"parts ABI");\ntypedef double FLO_type;\n#define isnan(p) ((p)->class==0 || (p)->class==1)\n#define isinf(p) ((p)->class==4)\n#define iszero(p) ((p)->class==2)\n#define NORMAL_EXPMIN (-1022)\n#define FRAC_NBITS 64\n#define GARDMASK 255\n#define GARDMSB 128\n#define GARDROUND 127\n#define IMPLICIT_2 (UINT64_C(1)<<61)\n#define FRACBITS 52\n#define EXPBITS 11\n#define EXPBIAS 1023\n#define EXPMAX 2047\n#define NGARDS 8\n#define IMPLICIT_1 (UINT64_C(1)<<60)\n#define QUIET_NAN (UINT64_C(1)<<51)\n#define CLASS_SNAN 0\n#define CLASS_QNAN 1\n#define CLASS_ZERO 2\n#define CLASS_NUMBER 3\n#define CLASS_INFINITY 4\n'+original[start:end]
    # In the denormal branch shift is 1..56. Split the right shift and
    # discarded-bit test into 32-bit words, avoiding compiler runtime calls.
    old='int lowbit = (fraction & (((fractype)1 << shift) - 1)) ? 1 : 0;\n\t      fraction = (fraction >> shift) | lowbit;'
    assert source.count(old)==1
    new='uint32_t lo = (uint32_t)fraction, hi = (uint32_t)(fraction >> 32);\n              uint32_t lowbit, out_lo, out_hi;\n              if (shift >= 32) {\n                unsigned tail = shift - 32;\n                lowbit = lo != 0 || (hi & ((UINT32_C(1) << tail) - 1)) != 0;\n                out_lo = hi >> tail; out_hi = 0;\n              } else {\n                lowbit = (lo & ((UINT32_C(1) << shift) - 1)) != 0;\n                out_lo = (lo >> shift) | (hi << (32 - shift));\n                out_hi = hi >> shift;\n              }\n              fraction = ((uint64_t)out_hi << 32) | out_lo | lowbit;'
    source=source.replace(old,new)
    # Equivalent ties-to-even bias before the eight guard bits are removed.
    # Intermediate guard bits differ, but retained significand and carry agree.
    marker='if ((fraction & GARDMASK) == GARDMSB)'
    assert source.count(marker)==2
    for _ in range(2):
        begin=source.index(marker)
        else_at=source.index('else',begin)
        brace=source.index('{',else_at);depth=1;finish=brace+1
        while depth:
            depth += (source[finish]=='{')-(source[finish]=='}');finish+=1
        source=source[:begin]+'fraction += GARDROUND + ((fraction >> NGARDS) & 1);'+source[finish:]
    out=ROOT/'build/gx8002-pack_double';out.mkdir(exist_ok=True);path=out/'candidate.c';path.write_text(source);(out/'COPYING.RUNTIME').write_text(deps['COPYING.RUNTIME'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(path),'-o',str(out/'candidate.o')],check=True)
    script=out/'candidate.ld';script.write_text('SECTIONS { .text 0x1020a574 : { *(.text.pack_d) } }\n')
    target=out/'candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'candidate.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    (out/'candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    r={'upstream_commit':commit,'upstream_sha256':sha(original.encode()),'source_sha256':sha(source.encode()),'adaptation':'Split guarded denormal shifts; equivalent ties-to-even bias 127 plus retained-bit parity','runtime_license_sha256':sha(deps['COPYING.RUNTIME'].encode()),'compiled_bytes':len(data),'envelope_bytes':400,'fits':len(data)<=400,'byte_exact':data==IMAGE.read_bytes()[0x13b00:0x13c90],'compiled_sha256':sha(data),'source_admitted':False,'limits':['Upstream candidate; behavioral and ownership checks outstanding.']}
    (ROOT/'docs/research/gx8002-pack_double-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
