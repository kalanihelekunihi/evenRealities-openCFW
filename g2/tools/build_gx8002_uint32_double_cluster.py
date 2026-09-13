# SPDX-License-Identifier: MIT
"""Build pinned GCC unsigned integer to binary64 conversion, without firmware extraction."""
import json,re,shlex,subprocess
from build_gx8002_make_dp_cluster import build as prior_build
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    prior=prior_build();base=ROOT/'build/gx8002-make-dp-cluster'
    out=ROOT/'build/gx8002-uint32-double-cluster';out.mkdir(exist_ok=True)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    log=(ROOT/'build/gx8002-exp-source-closure/rebuild.log').read_text()
    cmd=shlex.split(next(l for l in log.splitlines() if ' -o _gt_df.o ' in l));assert cmd.count('-DL_gt_df')==1
    cmd[cmd.index('-DL_gt_df')]='-DL_usi_to_df';obj=out/'uint.o'
    for flag,target in [('-o',obj),('-MT',obj),('-MF',out/'uint.dep')]:cmd[cmd.index(flag)+1]=str(target)
    subprocess.run(cmd,cwd=lib,check=True)
    script=(base/'make.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)));inputs.append(str(obj))
    address=0x4ad0c-0x3b940+0x10003000
    script+=f'SECTIONS {{ .uint {address:#x} : {{ {obj}(.text) }} }}\nASSERT(SIZEOF(.uint) <= 88, "unsigned conversion overflow")\n'
    ld=out/'uint.ld';ld.write_text(script);path=out/'uint.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'make');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    old=Elf32((base/'make.elf').read_bytes(),'prior');assert sha((base/'make.elf').read_bytes())==prior['elf_sha256']
    for section in old.sections:
        if section['flags']&2 and section['size']:
            current=next(s for s in e.sections if s['name']==section['name'])
            assert current['address']==section['address'] and e.contents(current)==old.contents(section)
    allocated=sorted([s for s in e.sections if s['flags']&2 and s['size']],key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(allocated,allocated[1:]))
    sec=next(s for s in e.sections if s['name']=='.uint')
    (out/'uint.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'prior':prior,'compile_command':cmd,'object_sha256':sha(obj.read_bytes()),'elf_sha256':sha(path.read_bytes()),'package_offset':0x4ad0c,'bytes':sec['size'],'source_admitted':False,'limits':['Pinned GCC __floatunsidf normalizes unsigned integers and invokes source pack. Fresh macOS source build; numerical execution and integration pending.']}
    (ROOT/'docs/research/gx8002-uint32-double-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['bytes'],r['elf_sha256'])
