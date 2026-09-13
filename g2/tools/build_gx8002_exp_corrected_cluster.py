# SPDX-License-Identifier: MIT
"""Link reconstructed exponential against corrected, source-built arithmetic."""
import json,re,subprocess
from build_gx8002_double_muldiv_cluster import build as arithmetic
from build_gx8002_backup_exp_probe import build as exponential
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build(signed_constants=False,helpers=False):
    dependencies=arithmetic(True);probe=exponential()
    base=ROOT/'build/gx8002-double-muldiv-corrected'
    stem='gx8002-exp-helper-cluster' if helpers else 'gx8002-exp-signed-cluster' if signed_constants else 'gx8002-exp-corrected-cluster'
    out=ROOT/'build'/stem;out.mkdir(exist_ok=True)
    script=(base/'muldiv.ld').read_text()
    inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)))
    obj=ROOT/'build/gx8002-backup-exp-probe/exp.o';assert sha(obj.read_bytes())==probe['object_sha256']
    variant=None
    if signed_constants:
        from probe_gx8002_exp_size import probe as size_probe
        inventory=size_probe();variant=next(r for r in inventory['variants'] if r.get('source_variant')=='signed constants')
        obj=ROOT/'build/gx8002-exp-size-probe/signed-constants.o'
        assert sha(obj.read_bytes())==variant['object_sha256']
    if helpers:
        from probe_gx8002_exp_helpers import run as helper_probe
        inventory=helper_probe();variant=next(r for r in inventory['variants'] if r['variant']=='tiny_scale')
        obj=ROOT/'build/gx8002-exp-helper-probe/tiny_scale.o'
        assert sha(obj.read_bytes())==variant['object_sha256']
    inputs.append(str(obj))
    # Analysis placement only: stock exp plus pools has 712 bytes available.
    script+=f'SECTIONS {{ .exp 0x10018000 : {{ {obj}(.text*) }} .exp_data : {{ {obj}(.rodata*) }} }}\n'
    ld=out/'exp.ld';ld.write_text(script);path=out/'exp.elf'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'exp');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    sections=[{'name':s['name'],'address':s['address'],'bytes':s['size'],'sha256':sha(elf.contents(s))} for s in elf.sections if s['flags']&2 and s['size']]
    prior_elf=Elf32((base/'muldiv.elf').read_bytes(),'arithmetic')
    assert sha((base/'muldiv.elf').read_bytes())==dependencies['elf_sha256']
    for sec in prior_elf.sections:
        if sec['flags']&2 and sec['size']:
            current=next(s for s in elf.sections if s['name']==sec['name'])
            assert current['address']==sec['address'] and elf.contents(current)==prior_elf.contents(sec)
    ordered=sorted(sections,key=lambda s:s['address'])
    assert all(a['address']+a['bytes']<=b['address'] for a,b in zip(ordered,ordered[1:]))
    own=[s for s in sections if s['name'].startswith('.exp')]
    (out/'exp.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'signed_constants':signed_constants,'variant':variant,'arithmetic':dependencies,'exponential':probe,'sections':sections,'exp_allocated_bytes':sum(s['bytes'] for s in own),'stock_exp_envelope':712,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Complete source dependency link at analysis address. Target exponential execution and physical placement remain unqualified.']}
    (ROOT/'docs/research'/(stem+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['elf_sha256'],r['exp_allocated_bytes'])
