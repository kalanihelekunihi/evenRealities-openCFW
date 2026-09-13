# SPDX-License-Identifier: MIT
"""Fresh upstream multiply/divide build against the placed source arithmetic core."""
import json,re,shlex,subprocess
from build_gx8002_double_addsub_cluster import build as addsub
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build(corrected=False):
    prior=addsub(True);base=ROOT/'build/gx8002-double-addsub-placed'
    stem='gx8002-double-muldiv-corrected' if corrected else 'gx8002-double-muldiv-cluster'
    out=ROOT/'build'/stem;out.mkdir(exist_ok=True)
    script=(base/'addsub.ld').read_text()
    inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    log=(ROOT/'build/gx8002-exp-source-closure/rebuild.log').read_text()
    patch=ROOT/'components/shared/gx8002/gcc-fp-bit-sticky-rounding.patch'
    upstream=ROOT/'build/upstream-csky-toolchain-build/gcc/libgcc/fp-bit.c'
    if corrected:
        source=out/'fp-bit.c';source.write_bytes(upstream.read_bytes())
        subprocess.run(['patch','--batch',str(source),str(patch)],check=True)
    records=[]
    for name,offset,limit in [('mul',0x4a790,512),('div',0x4a990,280)]:
        line=next(l for l in log.splitlines() if ' -o _'+name+'_df.o ' in l)
        cmd=['-Os' if x=='-O2' else x for x in shlex.split(line)];obj=out/(name+'.o')
        for flag,target in [('-o',obj),('-MT',obj),('-MF',out/(name+'.dep'))]:cmd[cmd.index(flag)+1]=str(target)
        if corrected:
            candidates=[i for i,x in enumerate(cmd) if x.endswith('/fp-bit.c')]
            assert len(candidates)==1
            cmd[candidates[0]]=str(source)
            cmd+=['-I'+str(upstream.parent)]
        subprocess.run(cmd,cwd=lib,check=True)
        e=Elf32(obj.read_bytes(),name);text=next(s for s in e.sections if s['name']=='.text')
        records.append({'name':name,'offset':offset,'stock_bytes':limit,'bytes':text['size'],'object_sha256':sha(obj.read_bytes()),'command':cmd})
        address=offset-0x3b940+0x10003000
        # Reject expansion into an adjacent original routine.
        script+=f'SECTIONS {{ .{name} {address:#x} : {{ {obj}(.text) }} }}\nASSERT(SIZEOF(.{name}) <= {limit}, "{name} overflow")\n'
        inputs.append(str(obj))
    ld=out/'muldiv.ld';ld.write_text(script);path=out/'muldiv.elf'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'muldiv')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    allocated=sorted([s for s in elf.sections if s['flags']&2 and s['size']],key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(allocated,allocated[1:]))
    (out/'muldiv.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'corrected':corrected,'upstream_source_sha256':sha(upstream.read_bytes()),'patch_sha256':sha(patch.read_bytes()) if corrected else None,'derived_source_sha256':sha(source.read_bytes()) if corrected else None,'prior':prior,'routines':records,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Whole freshly compiled source objects at original public entries. Numerical execution, references, stock equivalence and firmware integration remain pending.']}
    (ROOT/'docs/research'/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print([(x['name'],x['bytes'],x['stock_bytes']) for x in r['routines']])
