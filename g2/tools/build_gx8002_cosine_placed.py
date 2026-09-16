# SPDX-License-Identifier: MIT
"""Place complete source cosine and coefficients with authenticated source helpers."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32,IMAGE,IMAGE_SHA
from build_gx8002_cosine_shared_probe import build as probe
from build_gx8002_polynomial_placed import build as polynomial


def build():
    evidence=probe();poly=polynomial();out=ROOT/'build/gx8002-cosine-placed';out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-exp-placed-cluster'
    prior=json.loads((ROOT/'docs/research/gx8002-exp-placed-cluster.json').read_text())
    assert sha((base/'exp.elf').read_bytes())==prior['elf_sha256']
    before=Elf32((base/'exp.elf').read_bytes(),'arithmetic')
    script=(base/'exp.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    delta=0x10003000-0x3b940
    sections=[('cosine',ROOT/'build/gx8002-cosine-shared-probe/cos.o','.text.__kernel_cos',0x499ac,252),('polynomial',ROOT/'build/gx8002-polynomial-placed/polynomial.o','.text.open_cfw_gx8002_polynomial',0x49828,50),('coefficients',ROOT/'build/gx8002-trig-loop-probe/cos_coefficients.c.o','.rodata*',0x4f99c,48)]
    for name,obj,selector,off,size in sections:
        inputs.append(str(obj));script+='SECTIONS { .%s 0x%x : { %s(%s) } }\nASSERT(SIZEOF(.%s)==%d,"section size changed")\n'%(name,off+delta,obj,selector,name,size)
    ld=out/'cosine.ld';ld.write_text(script);path=out/'cosine.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'cosine');allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for old in before.sections:
        if old['flags']&2 and old['size']:
            new=next(s for s in allocated if s['name']==old['name']);assert new['address']==old['address'] and elf.contents(new)==before.contents(old)
    assert {s['name'] for s in allocated}-{s['name'] for s in before.sections}=={'.cosine','.polynomial','.coefficients'}
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    const=next(s for s in allocated if s['name']=='.coefficients');assert elf.contents(const)==stock[0x4f99c:0x4f9cc]
    polyelf=Elf32((ROOT/'build/gx8002-polynomial-placed/polynomial.elf').read_bytes(),'poly')
    assert elf.contents(next(s for s in allocated if s['name']=='.polynomial'))==polyelf.contents(next(s for s in polyelf.sections if s['name']=='.polynomial'))
    ordered=sorted(allocated,key=lambda s:s['address']);assert all(a['address']+a['size']<=b['address'] for a,b in zip(ordered,ordered[1:]))
    assert all(0x10003000<=s['address'] and s['address']+s['size']<=0x1001708c for s in allocated)
    (out/'cosine.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'probe':evidence,'polynomial':poly,'arithmetic_elf_sha256':prior['elf_sha256'],'elf_sha256':sha(path.read_bytes()),'sections':[{'name':s['name'],'offset':s['address']-delta,'bytes':s['size'],'sha256':sha(elf.contents(s))} for s in allocated if s['name'] in ('.cosine','.polynomial','.coefficients')],'source_admitted':False,'limits':['Complete source placement with coefficients equal to stock values. Reference census, placed execution, exceptional behavior and firmware integration pending.']}
    (ROOT/'docs/research/gx8002-cosine-placed.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['elf_sha256'],r['sections'])
