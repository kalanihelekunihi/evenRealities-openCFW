# SPDX-License-Identifier: MIT
"""Compile cosine using the reconstructed source polynomial evaluator."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_trig_loop_probe import build as loops
from verify_gx8002_analog_source import FLAGS


def build():
    prior=loops();out=ROOT/'build/gx8002-cosine-shared-probe';out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-trig-loop-probe'
    (out/'fdlibm.h').write_bytes((base/'fdlibm.h').read_bytes())
    source=(base/'k_cos.c').read_text()
    source=source.replace('#include "fdlibm.h"','#include "fdlibm.h"\nextern double open_cfw_gx8002_polynomial(const double *, unsigned, double);')
    pattern=r'int coefficient;\s*r = (\w+)\[(\d+)\];\s*for \(coefficient = \d+; coefficient >= 0; --coefficient\)\s*r = \w+\[coefficient\] \+ z\*r;'
    source,count=re.subn(pattern,r'r = open_cfw_gx8002_polynomial(\1, \2, z);',source);assert count==1
    source=source.replace('double a,hz,z,r,qx;','double a,hz,z,r,qx,correction,halfz;')
    source=source.replace('\tif(ix < 0x3FD33333)','\tcorrection = z*r - x*y;\n\thalfz = 0.5*z;\n\tif(ix < 0x3FD33333)')
    source=source.replace('one - (0.5*z - (z*r - x*y))','one - (halfz - correction)')
    source=source.replace('hz = 0.5*z-qx;','hz = halfz-qx;')
    source=source.replace('a - (hz - (z*r-x*y))','a - (hz - correction)')
    path=out/'k_cos.c';path.write_text(source);obj=out/'cos.o'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc',*FLAGS,'-Os','-mno-high-registers','-fwrapv','-ffp-contract=off','-c',str(path),'-o',str(obj)]
    subprocess.run(command,check=True);elf=Elf32(obj.read_bytes(),'cosine')
    allocated=[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']]
    assert allocated==[('.text.__kernel_cos',252)]
    result={'prior':prior,'source_sha256':sha(path.read_bytes()),'object_sha256':sha(obj.read_bytes()),'command':command,'allocated':allocated,'undefined_symbols':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0],'source_admitted':False,'limits':['Complete cosine source fits 276-byte entry region at object stage. Shared polynomial reverses addition operands compared with original expression; finite arithmetic is commutative, but NaN payload behavior must be separately evaluated. Common correction and half-square expressions are evaluated before branch selection without changing their arithmetic grouping. Exception/trap ordering, link, reference closure, execution, source constant placement and integration pending.']}
    (ROOT/'docs/research/gx8002-cosine-shared-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['allocated'],r['undefined_symbols'])
