# SPDX-License-Identifier: MIT
"""Link recovered centered remainder with complete existing source dependencies."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32,FLAGS


def build():
    out=ROOT/'build/gx8002-centered-remainder';out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-exp-placed-cluster'
    prior=json.loads((ROOT/'docs/research/gx8002-exp-placed-cluster.json').read_text())
    assert sha((base/'exp.elf').read_bytes())==prior['elf_sha256']
    before=Elf32((base/'exp.elf').read_bytes(),'source arithmetic')
    fmod=ROOT/'build/gx8002-fmod-probe/signed-zero-compact.o'
    placed=ROOT/'build/gx8002-fmod-placed/fmod.elf'
    evidence=json.loads((ROOT/'docs/research/gx8002-fmod-placed.json').read_text())
    assert sha(placed.read_bytes())==evidence['elf_sha256']
    source=ROOT/'components/shared/gx8002/runtime_gx8002_centered_remainder.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'centered.o'
    command=[pre+'gcc',*FLAGS,'-Os','-mno-high-registers','-ffp-contract=off','-c',str(source),'-o',str(obj)]
    subprocess.run(command,check=True)
    script=(base/'exp.ld').read_text()
    inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    script+='SECTIONS { .fmod 0x10010ca4 : { '+str(fmod)+'(.text.__ieee754_fmod) }\n'
    script+=' .centered 0x1000fc5c : { '+str(obj)+'(.text*) } }\n'
    ld=out/'centered.ld';ld.write_text(script);path=out/'centered.elf'
    subprocess.run([pre+'ld','-T',str(ld),*inputs,str(fmod),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'centered remainder')
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    for old in before.sections:
        if old['flags']&2 and old['size']:
            new=next(s for s in allocated if s['name']==old['name'])
            assert new['address']==old['address'] and elf.contents(new)==before.contents(old)
    old=Elf32(placed.read_bytes(),'fmod')
    sec=next(s for s in allocated if s['name']=='.fmod')
    assert elf.contents(sec)==old.contents(next(s for s in old.sections if s['name']=='.fmod'))
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    ordered=sorted(allocated,key=lambda s:s['address'])
    assert all(a['address']+a['size']<=b['address'] for a,b in zip(ordered,ordered[1:]))
    sec=next(s for s in allocated if s['name']=='.centered')
    result={'source_sha256':sha(source.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'bytes':sec['size'],'stock_envelope_bytes':160,'fits':sec['size']<=160,'source_admitted':False,'limits':['Source dependency closure authenticated; numerical/ABI, reference and integrated loader qualification pending.']}
    (ROOT/'docs/research/gx8002-centered-remainder.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
if __name__=='__main__':print(build())
