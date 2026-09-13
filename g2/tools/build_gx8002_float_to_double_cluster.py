# SPDX-License-Identifier: MIT
"""Rebuild pinned upstream float widening and unpack at original entries."""
import json,re,subprocess
from build_gx8002_double_to_float_cluster import build as prior_build
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    prior=prior_build();base=ROOT/'build/gx8002-double-to-float-cluster'
    out=ROOT/'build/gx8002-float-to-double-cluster';out.mkdir(exist_ok=True)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc';source=ROOT/'build/upstream-csky-toolchain-build/gcc/libgcc/fp-bit.c'
    names=['_sf_to_df.o','_unpack_sf.o']
    log=subprocess.check_output(['make','-W',str(source),*names],cwd=lib,text=True)
    assert all(' -o '+name+' ' in log for name in names);(out/'rebuild.log').write_text(log)
    script=(base/'convert.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)));records=[]
    for name,section,offset,limit in [('_sf_to_df.o','widen',0x4a434,44),('_unpack_sf.o','unpack_float',0x4adb0,124)]:
        obj=out/name;obj.write_bytes((lib/name).read_bytes());inputs.append(str(obj));address=offset-0x3b940+0x10003000
        script+=f'SECTIONS {{ .{section} {address:#x} : {{ {obj}(.text) }} }}\nASSERT(SIZEOF(.{section}) <= {limit}, "{section} overflow")\n'
        e=Elf32(obj.read_bytes(),name);size=next(s['size'] for s in e.sections if s['name']=='.text')
        records.append({'section':section,'offset':offset,'bytes':size,'object_sha256':sha(obj.read_bytes())})
    ld=out/'widen.ld';ld.write_text(script);path=out/'widen.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'widen');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    allocated=sorted((s for s in e.sections if s['flags']&2 and s['size']),key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(allocated,allocated[1:]))
    previous=Elf32((base/'convert.elf').read_bytes(),'prior');assert sha((base/'convert.elf').read_bytes())==prior['elf_sha256']
    for section in previous.sections:
        if section['flags']&2 and section['size']:
            current=next(s for s in allocated if s['name']==section['name'])
            assert current['address']==section['address'] and e.contents(current)==previous.contents(section)
    result={'prior':prior,'objects':records,'elf_sha256':sha(path.read_bytes()),'source_sha256':sha(source.read_bytes()),'source_admitted':False,'limits':['Whole source functions in original envelopes; execution, integration and hardware pending.']}
    (ROOT/'docs/research/gx8002-float-to-double-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['objects'])
