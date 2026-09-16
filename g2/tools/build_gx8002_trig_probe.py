# SPDX-License-Identifier: MIT
"""Compile pinned binary64 trig kernels intact, retaining provenance and sizes."""
import json, subprocess
from build_gx8002_backup_cfft import ROOT, sha, Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    upstream=ROOT/'build/upstream-newlib-math'
    receipt=json.loads((upstream/'receipt.json').read_text())
    assert receipt['commit']=='4aa696c8d6294897411cf78cae87f7f4680e9687'
    out=ROOT/'build/gx8002-trig-probe';out.mkdir(exist_ok=True)
    header=(ROOT/'components/shared/gx8002/newlib_double_compat.h').read_bytes()
    header+=b'\n#define GET_HIGH_WORD(hi,x) do { union { double d; uint64_t u; } w_={.d=(x)}; (hi)=(uint32_t)(w_.u>>32); } while(0)\n'
    (out/'fdlibm.h').write_bytes(header)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for name in ('k_sin.c','k_cos.c'):
        pin=next(r for r in receipt['files'] if r['path']=='newlib/libm/math/'+name)
        data=(upstream/name).read_bytes();assert sha(data)==pin['sha256']
        source=out/name;source.write_bytes(data)
        for label,extra in [('size',['-Os']),('low',['-Os','-mno-high-registers'])]:
            obj=out/(name+'.'+label+'.o')
            cmd=[pre+'gcc',*FLAGS,*extra,'-fwrapv','-ffp-contract=off','-c',str(source),'-o',str(obj)]
            subprocess.run(cmd,check=True)
            elf=Elf32(obj.read_bytes(),name)
            rows.append({'source':pin,'variant':label,'command':cmd,'object_sha256':sha(obj.read_bytes()),'allocated':[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']],'undefined_symbols':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0]})
    result={'commit':receipt['commit'],'header_sha256':sha(header),'objects':rows,'source_admitted':False,'limits':['Unchanged upstream kernel objects, not linked or executed. Stock coefficients differ; numerical and behavioral equivalence cannot be assumed. Shared literal pools must be separated from function boundaries before placement.']}
    (ROOT/'docs/research/gx8002-trig-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    print([(r['source']['path'],r['variant'],r['allocated'],r['undefined_symbols']) for r in build()['objects']])
