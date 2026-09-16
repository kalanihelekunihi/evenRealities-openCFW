# SPDX-License-Identifier: MIT
"""Compile pinned double fmod intact for dependency and placement analysis."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    upstream=ROOT/'build/upstream-newlib-math';receipt=json.loads((upstream/'receipt.json').read_text());assert receipt['commit']=='4aa696c8d6294897411cf78cae87f7f4680e9687'
    pin=next(r for r in receipt['files'] if r['path']=='newlib/libm/math/e_fmod.c');data=(upstream/'e_fmod.c').read_bytes();assert sha(data)==pin['sha256']
    out=ROOT/'build/gx8002-fmod-probe';out.mkdir(exist_ok=True)
    header=(ROOT/'components/shared/gx8002/newlib_double_compat.h').read_bytes();(out/'fdlibm.h').write_bytes(header);source=out/'e_fmod.c';source.write_bytes(data)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'fmod.o'
    command=[pre+'gcc',*FLAGS,'-fwrapv','-ffp-contract=off','-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
    elf=Elf32(obj.read_bytes(),'fmod');undefined=[s['name'] for s in elf.symbols() if s['name'] and s['section']==0]
    variants=[]
    for label,extra in [('size',['-Os']),('low-registers',['-Os','-mno-high-registers']),('ck803',['-Os','-mno-high-registers','-mcpu=ck803ef'])]:
        target=out/(label+'.o');cmd=[pre+'gcc',*FLAGS,*extra,'-fwrapv','-ffp-contract=off','-c',str(source),'-o',str(target)]
        subprocess.run(cmd,check=True);variant=Elf32(target.read_bytes(),label)
        variants.append({'label':label,'command':cmd,'sha256':sha(target.read_bytes()),'allocated':[(s['name'],s['size']) for s in variant.sections if s['flags']&2 and s['size']]})
    patch=ROOT/'components/shared/gx8002/newlib-fmod-signed-zero.patch'
    adapted=out/'adapted';adapted.mkdir(exist_ok=True)
    (adapted/'e_fmod.c').write_bytes(data);(adapted/'fdlibm.h').write_bytes(header)
    subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=adapted,check=True)
    target=out/'signed-zero-compact.o'
    compact_command=[pre+'gcc',*FLAGS,'-Os','-mno-high-registers','-fno-tree-forwprop','-fwrapv','-ffp-contract=off','-c',str(adapted/'e_fmod.c'),'-o',str(target)]
    subprocess.run(compact_command,check=True);compact=Elf32(target.read_bytes(),'compact')
    compact_evidence={'patch_sha256':sha(patch.read_bytes()),'source_sha256':sha((adapted/'e_fmod.c').read_bytes()),'command':compact_command,'object_sha256':sha(target.read_bytes()),'allocated':[(s['name'],s['size']) for s in compact.sections if s['flags']&2 and s['size']],'undefined_symbols':[s['name'] for s in compact.symbols() if s['name'] and s['section']==0]}
    assert compact_evidence['allocated']==[('.text.__ieee754_fmod',576)]
    assert set(compact_evidence['undefined_symbols'])=={'__muldf3','__divdf3'}
    result={'compact':compact_evidence,'variants':variants,'commit':receipt['commit'],'source':pin,'header_sha256':sha(header),'object_sha256':sha(obj.read_bytes()),'command':command,'undefined_symbols':undefined,'allocated':[(s['name'],s['size']) for s in elf.sections if s['flags']&2 and s['size']],'source_admitted':False,'limits':['Complete source object only. Link existing source arithmetic dependencies, verify stock boundaries and execute before integration.']}
    (ROOT/'docs/research/gx8002-fmod-probe.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['allocated'],r['undefined_symbols'])
