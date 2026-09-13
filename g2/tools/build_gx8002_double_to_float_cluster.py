# SPDX-License-Identifier: MIT
"""Build upstream binary64-to-binary32 conversion with source pack dependency."""
import json,re,shlex,subprocess
from build_gx8002_uint32_double_cluster import build as prior_build
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    prior=prior_build();base=ROOT/'build/gx8002-uint32-double-cluster'
    out=ROOT/'build/gx8002-double-to-float-cluster';out.mkdir(exist_ok=True)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    source=ROOT/'build/upstream-csky-toolchain-build/gcc/libgcc/fp-bit.c'
    names=['_df_to_sf.o','_make_sf.o','_pack_sf.o']
    log=subprocess.check_output(['make','-W',str(source),*names],cwd=lib,text=True)
    assert all(' -o '+name+' ' in log for name in names);(out/'rebuild.log').write_text(log)
    command=shlex.split(next(line for line in log.splitlines() if ' -o _pack_sf.o ' in line))
    command=['-Os' if arg=='-O2' else arg for arg in command]
    command[command.index('-o')+1]=str(out/'pack-os.o')
    subprocess.run(command,cwd=lib,check=True)
    (out/'pack-command.json').write_text(json.dumps(command,indent=2)+'\n')
    script=(base/'uint.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    records=[]
    for name,section,address,limit in [('_df_to_sf.o','convert',0x4acd8-0x3b940+0x10003000,52),('_make_sf.o','make_float',0x4ae2c-0x3b940+0x10003000,24),('_pack_sf.o','pack_float',0x4b17c-0x3b940+0x10003000,192)]:
        obj=out/name;obj.write_bytes(((out/'pack-os.o') if name=='_pack_sf.o' else lib/name).read_bytes());inputs.append(str(obj))
        script+=f'SECTIONS {{ .{section} {address:#x} : {{ {obj}(.text) }} }}\n'
        if limit:script+=f'ASSERT(SIZEOF(.{section}) <= {limit}, "{section} overflow")\n'
        e=Elf32(obj.read_bytes(),name);size=next(s['size'] for s in e.sections if s['name']=='.text')
        records.append({'name':section,'address':address,'bytes':size,'object_sha256':sha(obj.read_bytes())})
    ld=out/'convert.ld';ld.write_text(script);path=out/'convert.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'convert');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    allocated=sorted((s for s in e.sections if s['flags']&2 and s['size']),key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(allocated,allocated[1:]))
    previous=Elf32((base/'uint.elf').read_bytes(),'prior')
    for section in previous.sections:
        if section['flags']&2 and section['size']:
            current=next(s for s in allocated if s['name']==section['name'])
            assert current['address']==section['address'] and e.contents(current)==previous.contents(section),section['name']
    (out/'convert.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'prior':prior,'upstream_source_sha256':sha(source.read_bytes()),'objects':records,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Whole source objects placed inside original function envelopes. Bounded reference analysis, firmware integration and hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-double-to-float-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['objects'])
