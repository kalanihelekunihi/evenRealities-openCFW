# SPDX-License-Identifier: MIT
"""Compile unchanged pinned public trig wrappers on macOS."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_analog_source import FLAGS


def build():
    upstream=ROOT/'build/upstream-newlib-math';receipt=json.loads((upstream/'receipt.json').read_text())
    assert receipt['commit']=='4aa696c8d6294897411cf78cae87f7f4680e9687'
    out=ROOT/'build/gx8002-public-trig-probe';out.mkdir(exist_ok=True)
    header=(ROOT/'build/gx8002-trig-probe/fdlibm.h').read_bytes()
    header+=b'\ndouble __kernel_sin(double,double,int);\ndouble __kernel_cos(double,double);\n__int32_t __ieee754_rem_pio2(double,double *);\n'
    (out/'fdlibm.h').write_bytes(header);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for name in ('s_sin.c','s_cos.c'):
        pin=next(r for r in receipt['files'] if r['path']=='newlib/libm/math/'+name)
        data=(upstream/name).read_bytes();assert sha(data)==pin['sha256']
        source=out/name;source.write_bytes(data)
        for label,extra in [('size',['-Os']),('low',['-Os','-mno-high-registers'])]:
            obj=out/(name+'.'+label+'.o');cmd=[pre+'gcc',*FLAGS,*extra,'-fwrapv','-ffp-contract=off','-c',str(source),'-o',str(obj)]
            subprocess.run(cmd,check=True);elf=Elf32(obj.read_bytes(),name)
            rows.append({'source':pin,'variant':label,'command':cmd,'object_sha256':sha(obj.read_bytes()),'allocated':[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']],'undefined_symbols':[s['name'] for s in elf.symbols() if s['name'] and s['section']==0]})
    result={'commit':receipt['commit'],'header_sha256':sha(header),'objects':rows,'source_admitted':False,'limits':['Complete public wrappers compiled only. Angle reducer and its large-argument kernel require reconstruction and qualification; no full-domain trig closure claimed.']}
    (ROOT/'docs/research/gx8002-public-trig-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([(r['source']['path'],r['variant'],r['allocated'],r['undefined_symbols']) for r in build()['objects']])
