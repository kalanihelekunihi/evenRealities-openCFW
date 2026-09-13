# SPDX-License-Identifier: MIT
"""Build pinned GCC binary64-to-uint32 with complete source dependencies."""
import json,re,subprocess
from build_gx8002_float_to_double_cluster import build as prior_build
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    prior=prior_build();base=ROOT/'build/gx8002-float-to-double-cluster'
    out=ROOT/'build/gx8002-fixunsdfsi-cluster';out.mkdir(exist_ok=True)
    upstream=ROOT/'build/upstream-csky-toolchain-build/gcc';source=upstream/'libgcc/libgcc2.c';pin='1e9b70447a8417f5c692370de4533e43d754e8fa'
    assert source.read_bytes()==subprocess.check_output(['git','show',pin+':libgcc/libgcc2.c'],cwd=upstream)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    log=subprocess.check_output(['make','-W',str(source),'_fixunsdfsi.o'],cwd=lib,text=True)
    assert ' -o _fixunsdfsi.o ' in log;(out/'rebuild.log').write_text(log)
    obj=out/'fix.o';obj.write_bytes((lib/'_fixunsdfsi.o').read_bytes())
    script=(base/'widen.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)));inputs.append(str(obj))
    address=0x49da4-0x3b940+0x10003000
    script+=f'SECTIONS {{ .fix_unsigned {address:#x} : {{ {obj}(.text) }} }}\nASSERT(SIZEOF(.fix_unsigned) <= 56, "unsigned fix overflow")\n__gedf2 = open_cfw_gx8002_double_compare_4ab20;\n'
    ld=out/'fix.ld';ld.write_text(script);path=out/'fix.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'fix');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    old=Elf32((base/'widen.elf').read_bytes(),'prior');assert sha((base/'widen.elf').read_bytes())==prior['elf_sha256']
    for section in old.sections:
        if section['flags']&2 and section['size']:
            current=next(s for s in e.sections if s['name']==section['name'])
            assert current['address']==section['address'] and e.contents(current)==old.contents(section)
    allocated=sorted((s for s in e.sections if s['flags']&2 and s['size']),key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(allocated,allocated[1:]))
    sec=next(s for s in allocated if s['name']=='.fix_unsigned')
    result={'prior':prior,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'bytes':sec['size'],'package_offset':0x49da4,'source_admitted':False,'limits':['GE comparison aliases previously verified stock 4ab20 source twin. Actual conversion execution, integration and hardware pending.']}
    (ROOT/'docs/research/gx8002-fixunsdfsi-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['bytes'])
