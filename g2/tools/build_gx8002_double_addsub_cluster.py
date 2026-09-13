# SPDX-License-Identifier: MIT
"""Compile upstream add/subtract with separate function sections and source core."""
import json,shlex,subprocess
from build_gx8002_double_bidirectional_conversion_cluster import build as conversions
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build(placed=False):
    prior=conversions();base=ROOT/'build/gx8002-double-bidirectional-conversion-cluster'
    stem='gx8002-double-addsub-placed' if placed else 'gx8002-double-addsub-cluster'
    out=ROOT/'build'/stem;out.mkdir(exist_ok=True)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    log=(ROOT/'build/gx8002-exp-source-closure/rebuild.log').read_text()
    line=next(line for line in log.splitlines() if ' -o _addsub_df.o ' in line)
    cmd=['-Os' if x=='-O2' else x for x in shlex.split(line)];obj=out/'addsub.o'
    for flag,target in [('-o',obj),('-MT',obj),('-MF',out/'addsub.dep')]:cmd[cmd.index(flag)+1]=str(target)
    cmd+=['-ffunction-sections','-fdata-sections'];subprocess.run(cmd,cwd=lib,check=True)
    e=Elf32(obj.read_bytes(),'addsub');sizes={s['name']:s['size'] for s in e.sections if s['flags']&2 and s['size']}
    script=(base/'wrappers.ld').read_text()
    # Keep public entries; reserve bounded subregions for complete source sections.
    sections=[('.text.__adddf3',0x4a724,48),('.text.__subdf3',0x4a754,56),('.text._fpadd_parts',0x4a460,708)]
    for i,(name,off,limit) in enumerate(sections):
        address=off-0x3b940+0x10003000
        script+=f'SECTIONS {{ .add{i} {address:#x} : {{ {obj}({name}) }} }}\n'
        bound=500 if placed and i==2 else limit
        script+=f'ASSERT(SIZEOF(.add{i}) <= {bound}, "add/sub region overflow")\n'
    nan=out/'nan.o';nan.write_bytes((lib/'_thenan_df.o').read_bytes())
    nan_address=0x4a6f0-0x3b940+0x10003000 if placed else 0x10019000
    script+=f'SECTIONS {{ .nan {nan_address:#x} : {{ {nan}(.rodata*) }} }}\n'
    inputs=[ROOT/'build/gx8002-double-core-layout'/(n+'.o') for n in ('pack','right','unpack','left','compare')]+[base/(n+'.o') for n in ('gt','lt','si','fi')]+[obj,nan]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    copy_source=ROOT/'components/shared/gx8002/runtime_gx8002_memcpy.c';copy=out/'copy.o'
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-Dopen_cfw_gx8002_memcpy=memcpy','-c',str(copy_source),'-o',str(copy)],check=True)
    copy_address=0x4a654-0x3b940+0x10003000 if placed else 0x10019020
    inputs.append(copy);script+=f'SECTIONS {{ .copy {copy_address:#x} : {{ {copy}(.text*) }} }}\n'
    script+='ASSERT(SIZEOF(.copy) <= 156, "copy overflow")\nASSERT(SIZEOF(.nan) == 20, "NaN size")\n'
    ld=out/'addsub.ld';ld.write_text(script);path=out/'addsub.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*[str(p) for p in inputs],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'addsub');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'addsub.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    allocated=sorted([s for s in elf.sections if s['flags']&2 and s['size']],key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(allocated,allocated[1:]))
    if placed:assert all(0x10003000<=s['address'] and s['address']+s['size']<=0x1001708c for s in allocated)
    placement=[{'name':s['name'],'offset':s['address']-0x10003000+0x3b940,'bytes':s['size'],'sha256':sha(elf.contents(s))} for s in allocated]
    result={'placed':placed,'placement':placement,'memcpy_source_sha256':sha(copy_source.read_bytes()),'prior':prior,'compile_command':cmd,'source_object_sha256':sha(obj.read_bytes()),'nan_object_sha256':sha(nan.read_bytes()),'sections':sizes,'fits_code':all(sizes[n]<=limit for n,off,limit in sections),'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Complete source dependency link; bounded placement is experimental. Stock equivalence, references, and hardware qualification remain pending.']}
    (ROOT/'docs/research'/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['sections'],r['fits_code'])
