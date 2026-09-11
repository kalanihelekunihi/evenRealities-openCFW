# SPDX-License-Identifier: MIT
"""Build an authenticated upstream arithmetic reference for later trace checks."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,authenticated_blob,sha

def build():
    gcc=ROOT/'build/upstream-csky-toolchain-build/gcc';commit='1e9b70447a8417f5c692370de4533e43d754e8fa';deps={}
    for name in ('libgcc/fp-bit.c','libgcc/fp-bit.h','COPYING.RUNTIME'):
        blob=subprocess.check_output(['git','-C',str(gcc),'rev-parse',commit+':'+name],text=True).strip();deps[name]=authenticated_blob(gcc/name,blob).decode()
    original=deps['libgcc/fp-bit.c'];start=original.index('_fpadd_parts (');end=original.index('\nFLO_type\nadd (',start)
    core=original[start:end]
    shift=re.search(r'^#define LSHIFT.*$',deps['libgcc/fp-bit.h'],re.M)[0]
    prelude='''#include <stdint.h>
#include <assert.h>
typedef uint64_t fractype;
typedef int64_t intfrac;
typedef struct { int class; unsigned sign; int normal_exp; union { uint64_t ll; } fraction; } fp_number_type;
#define FRAC_NBITS 64
#define IMPLICIT_1 (UINT64_C(1)<<60)
#define IMPLICIT_2 (UINT64_C(1)<<61)
#define CLASS_NUMBER 3
#define isnan(a) ((a)->class<2)
#define isinf(a) ((a)->class==4)
#define iszero(a) ((a)->class==2)
static fp_number_type nan_value={1,0,0,{0}};
#define makenan() (&nan_value)
'''
    out=ROOT/'build/gx8002-fpadd-reference';out.mkdir(parents=True,exist_ok=True)
    source=out/'reference.c';source.write_text('/* GCC fp-bit.c extracted reference; original licenses remain at pinned source. */\n'+prelude+shift+'\nstatic fp_number_type *\n'+core+'''
int main(void) {
  unsigned cases=0;
  for(int exponent=-32;exponent<=32;exponent++)
    for(unsigned sign=0;sign<2;sign++)
      for(unsigned delta=0;delta<256;delta++) {
        fp_number_type a={3,sign,exponent,{(UINT64_C(1)<<60)+((uint64_t)delta<<32)}};
        fp_number_type b=a,tmp={0}; b.sign^=1;
        fp_number_type *r=_fpadd_parts(&a,&b,&tmp);
        assert(r==&tmp && r->class==3 && r->fraction.ll==0 && r->sign==0);
        b=a;r=_fpadd_parts(&a,&b,&tmp);
        assert(r==&tmp && r->class==3 && r->sign==sign && r->normal_exp==exponent+1 && r->fraction.ll==a.fraction.ll);
        cases++;
      }
  return cases==33280?0:1;
}
''')
    exe=out/'reference';subprocess.run(['clang','-std=c11','-O1','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(source),'-o',str(exe)],check=True);subprocess.run([str(exe)],check=True)
    return {'gcc_commit':commit,'source_hashes':{n:sha(v.encode()) for n,v in deps.items()},'extracted_core_sha256':sha(core.encode()),'reference_source_sha256':sha(source.read_bytes()),'host':'macOS clang','sanitizers':['address','undefined'],'input_cases':33280,'arithmetic_checks':66560,'source_admitted':False,'limits':['Exact upstream core with host type/class scaffolding; cancellation and doubling invariants only. Not a stock-binary comparison or target ABI test. Reference is for later decoded arithmetic checks.']}

if __name__=='__main__':
    result=build();(ROOT/'docs/research/gx8002-fpadd-reference.json').write_text(json.dumps(result,indent=2)+'\n');print('Upstream core checks:',result['arithmetic_checks'])
