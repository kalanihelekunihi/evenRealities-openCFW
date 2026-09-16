# SPDX-License-Identifier: MIT
"""Compile complete pinned argument reducers and inventory their dependencies."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_analog_source import FLAGS


def build(helpers=False):
    upstream=ROOT/'build/upstream-newlib-math';receipt=json.loads((upstream/'receipt.json').read_text())
    assert receipt['commit']=='4aa696c8d6294897411cf78cae87f7f4680e9687'
    stem='gx8002-reduction-helpers-probe' if helpers else 'gx8002-reduction-probe'
    out=ROOT/'build'/stem;out.mkdir(exist_ok=True)
    headers={}
    for original,target in [('newlib_double_compat.h','newlib_double_compat.h'),('newlib_reduction_compat.h','fdlibm.h')]:
        data=(ROOT/'components/shared/gx8002'/original).read_bytes()
        if helpers and target=='fdlibm.h':data+=b'\ndouble copysign(double,double);\n'
        (out/target).write_bytes(data);headers[original]=sha(data)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for name in (('s_fabs.c','s_floor.c','s_scalbn.c','s_copysign.c') if helpers else ('e_rem_pio2.c','k_rem_pio2.c')):
        pin=next(r for r in receipt['files'] if r['path'].endswith('/'+name))
        data=(upstream/name).read_bytes();assert sha(data)==pin['sha256'];source=out/name;source.write_bytes(data)
        obj=out/(name+'.o');cmd=[pre+'gcc',*FLAGS,'-Os','-mno-high-registers','-fwrapv','-ffp-contract=off',*(['-Wno-error=misleading-indentation'] if name=='k_rem_pio2.c' else ['-Wno-error=sign-compare'] if name=='s_floor.c' else []),'-c',str(source),'-o',str(obj)]
        subprocess.run(cmd,check=True);elf=Elf32(obj.read_bytes(),name)
        rows.append({'source':pin,'command':cmd,'object_sha256':sha(obj.read_bytes()),'allocated':[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']],'undefined_symbols':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0]})
    result={'helpers':helpers,'commit':receipt['commit'],'header_hashes':headers,'objects':rows,'source_admitted':False,'limits':['Whole upstream reducers compile only; dependency linking, numerical/ABI execution, placement and hardware pending. Word setters support partial initialization without reading uninitialized double storage.']}
    (ROOT/'docs/research'/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([(r['source']['path'],r['allocated'],r['undefined_symbols']) for r in build()['objects']])
