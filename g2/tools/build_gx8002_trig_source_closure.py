# SPDX-License-Identifier: MIT
"""Link complete trig sources with authenticated reconstructed arithmetic."""
import json,re,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_trig_probe import build as probe


def build(loops=False):
    if loops:
        from build_gx8002_trig_loop_probe import build as loop_probe
    evidence=loop_probe() if loops else probe()
    stem='gx8002-trig-loop-closure' if loops else 'gx8002-trig-source-closure'
    out=ROOT/'build'/stem;out.mkdir(exist_ok=True)
    base=ROOT/'build/gx8002-exp-placed-cluster'
    prior=json.loads((ROOT/'docs/research/gx8002-exp-placed-cluster.json').read_text())
    before=Elf32((base/'exp.elf').read_bytes(),'arithmetic')
    assert sha((base/'exp.elf').read_bytes())==prior['elf_sha256']
    script=(base/'exp.ld').read_text()
    inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    for name,offset in [('sin',0x10018000),('cos',0x10018200)]:
        if loops:
            obj=ROOT/'build/gx8002-trig-loop-probe'/('k_'+name+'.c.o')
            row=next(r for r in evidence['objects'] if r['source']=='k_'+name+'.c')
            const=ROOT/'build/gx8002-trig-loop-probe'/(name+'_coefficients.c.o')
            const_row=next(r for r in evidence['objects'] if r['source']==name+'_coefficients.c')
            assert sha(const.read_bytes())==const_row['object_sha256']
            inputs.append(str(const))
            script+='SECTIONS { .trig_%s_constants 0x%x : { %s(.rodata*) } }\n'%(name,offset+0x180,const)
        else:
            obj=ROOT/'build/gx8002-trig-probe'/('k_'+name+'.c.low.o')
            row=next(r for r in evidence['objects'] if r['source']['path'].endswith('k_'+name+'.c') and r['variant']=='low')
        assert sha(obj.read_bytes())==row['object_sha256']
        inputs.append(str(obj))
        script+='SECTIONS { .trig_%s 0x%x : { %s(.text.__kernel_%s) } }\n'%(name,offset,obj,name)
        script+='ASSERT(SIZEOF(.trig_%s)<=512,"trig analysis overflow")\n'%name
    ld=out/'trig.ld';ld.write_text(script);path=out/'trig.elf'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'trig')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    for old in before.sections:
        if old['flags']&2 and old['size']:
            new=next(s for s in allocated if s['name']==old['name'])
            assert new['address']==old['address'] and elf.contents(new)==before.contents(old)
    assert {s['name'] for s in allocated}-{s['name'] for s in before.sections}==({'.trig_sin','.trig_cos','.trig_sin_constants','.trig_cos_constants'} if loops else {'.trig_sin','.trig_cos'})
    (out/'trig.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'loops':loops,'probe':evidence,'arithmetic_elf_sha256':prior['elf_sha256'],'elf_sha256':sha(path.read_bytes()),'sections':[{'name':s['name'],'address':s['address'],'bytes':s['size']} for s in allocated if s['name'].startswith('.trig')],'source_admitted':False,'limits':['Analysis addresses outside stock image; full source closure only, not firmware placement. Arithmetic sections authenticated byte-for-byte against prior source ELF. Numerical and hardware qualification pending.']}
    (ROOT/'docs/research'/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['elf_sha256'],r['sections'])
