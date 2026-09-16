# SPDX-License-Identifier: MIT
"""Compile sine using the reconstructed source polynomial evaluator."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_trig_loop_probe import build as loops
from verify_gx8002_analog_source import FLAGS


def build():
    prior=loops();out=ROOT/'build/gx8002-sine-shared-probe';out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-trig-loop-probe'
    (out/'fdlibm.h').write_bytes((base/'fdlibm.h').read_bytes())
    source=(base/'k_sin.c').read_text()
    source=source.replace('#include "fdlibm.h"','#include "fdlibm.h"\nextern double open_cfw_gx8002_polynomial(const double *, unsigned, double);')
    pattern=r'int coefficient;\s*r = (\w+)\[(\d+)\];\s*for \(coefficient = \d+; coefficient >= 0; --coefficient\)\s*r = \w+\[coefficient\] \+ z\*r;'
    source,count=re.subn(pattern,r'r = open_cfw_gx8002_polynomial(\1, \2, z);',source);assert count==1
    path=out/'k_sin.c';path.write_text(source);obj=out/'sin.o'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc',*FLAGS,'-Os','-mno-high-registers','-fwrapv','-ffp-contract=off','-c',str(path),'-o',str(obj)]
    subprocess.run(command,check=True);elf=Elf32(obj.read_bytes(),'sine')
    allocated=[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']]
    assert allocated==[('.text.__kernel_sin',264)]
    result={'prior':prior,'source_sha256':sha(path.read_bytes()),'object_sha256':sha(obj.read_bytes()),'command':command,'allocated':allocated,'undefined_symbols':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0],'source_admitted':False,'limits':['Complete sine source fits 284-byte entry region at object stage. Shared polynomial reverses addition operands compared with original expression; finite arithmetic is commutative, but NaN payload behavior must be separately evaluated. Link, reference closure, execution, source constant placement and integration pending.']}
    (ROOT/'docs/research/gx8002-sine-shared-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['allocated'],r['undefined_symbols'])
