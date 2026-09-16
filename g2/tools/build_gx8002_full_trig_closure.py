# SPDX-License-Identifier: MIT
"""Link public trig, full reduction and reconstructed kernels entirely from source."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_public_trig_probe import build as wrappers


def build(placed_wrappers=False):
    evidence=wrappers();stem='gx8002-public-trig-placed' if placed_wrappers else 'gx8002-full-trig-closure'
    out=ROOT/'build'/stem;out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-reduction-source-closure';report=json.loads((ROOT/'docs/research/gx8002-reduction-source-closure.json').read_text())
    assert sha((base/'reduction.elf').read_bytes())==report['elf_sha256']
    before=Elf32((base/'reduction.elf').read_bytes(),'reduction')
    script=(base/'reduction.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    # Copy only linker declarations and source object inputs, never binary sections.
    authenticated=[]
    for kernel_stem,filename in [('gx8002-sine-placed','sine'),('gx8002-cosine-placed','cosine')]:
        prior=json.loads((ROOT/'docs/research'/(kernel_stem+'.json')).read_text());path=ROOT/'build'/kernel_stem/(filename+'.elf')
        assert sha(path.read_bytes())==prior['elf_sha256'];authenticated.append((Elf32(path.read_bytes(),kernel_stem),prior['elf_sha256']))
        text=(ROOT/'build'/kernel_stem/(filename+'.ld')).read_text()
        for line in text.splitlines():
            if line.startswith('SECTIONS { .'+filename+' ') or line.startswith('SECTIONS { .coefficients ') or (filename=='sine' and line.startswith('SECTIONS { .polynomial ')):
                line=line.replace('.coefficients ','.'+filename+'_coefficients ')
                script+=line+'\n';inputs+=re.findall(r'(/[^\s()]+\.o)\(',line)
    addresses=[('sin',0x484f0+0x10003000-0x3b940),('cos',0x48454+0x10003000-0x3b940)] if placed_wrappers else [('sin',0x1001a000),('cos',0x1001a100)]
    for name,addr in addresses:
        obj=ROOT/'build/gx8002-public-trig-probe'/('s_'+name+'.c.low.o')
        row=next(r for r in evidence['objects'] if r['source']['path'].endswith('s_'+name+'.c') and r['variant']=='low');assert sha(obj.read_bytes())==row['object_sha256']
        inputs.append(str(obj));script+='SECTIONS { .public_%s 0x%x : { %s(.text.%s) } }\n'%(name,addr,obj,name)
    if placed_wrappers:
        script+='ASSERT(SIZEOF(.public_sin)<=168,"sin overflow")\nASSERT(SIZEOF(.public_cos)<=156,"cos overflow")\n'
    ld=out/'trig.ld';ld.write_text(script);path=out/'trig.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*dict.fromkeys(inputs),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'trig');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    for prior in [before]+[v[0] for v in authenticated]:
        for old in prior.sections:
            if old['flags']&2 and old['size']:
                new=next(s for s in sections if s['address']==old['address']);assert elf.contents(new)==prior.contents(old)
    ordered=sorted(sections,key=lambda s:s['address']);assert all(a['address']+a['size']<=b['address'] for a,b in zip(ordered,ordered[1:]))
    (out/'trig.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'placed_wrappers':placed_wrappers,'wrapper_sections':[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in sections if s['name'].startswith('.public')],'wrapper_probe':evidence,'reduction_elf_sha256':report['elf_sha256'],'kernel_elf_sha256':[v[1] for v in authenticated],'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Complete source trig dependency closure; reducer remains at analysis address; optional public-wrapper placement only. No unresolved symbols or relocations. End-to-end accuracy, stock placement and hardware pending.']}
    (ROOT/'docs/research'/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['elf_sha256'])
