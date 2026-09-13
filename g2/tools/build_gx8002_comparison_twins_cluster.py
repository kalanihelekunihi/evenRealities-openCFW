# SPDX-License-Identifier: MIT
"""Build complete C comparison forwarding functions with source dependencies."""
import json,re,subprocess
from build_gx8002_exp_placed_cluster import build as prior_build
from build_gx8002_backup_cfft import ROOT,sha,Elf32,FLAGS

def build():
    prior=prior_build();base=ROOT/'build/gx8002-exp-placed-cluster'
    out=ROOT/'build/gx8002-comparison-twins-cluster';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_double_comparison_twins.c';obj=out/'twins.o'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    cmd=[pre+'gcc',*FLAGS,'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
    script=(base/'exp.ld').read_text();inputs=list(dict.fromkeys(re.findall(r'(/[^\s()]+\.o)\(',script)));inputs.append(str(obj))
    for name,off,limit in [('4ab20',0x4ab20,64),('4ab98',0x4ab98,56)]:
        address=off-0x3b940+0x10003000
        script+=f'SECTIONS {{ .twin_{name} {address:#x} : {{ {obj}(.text.open_cfw_gx8002_double_compare_{name}) }} }}\nASSERT(SIZEOF(.twin_{name}) <= {limit}, "twin overflow")\n'
    ld=out/'twins.ld';ld.write_text(script);path=out/'twins.elf';subprocess.run([pre+'ld','-T',str(ld),*inputs,'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'twins');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    sections=sorted([{'name':s['name'],'offset':s['address']-0x10003000+0x3b940,'bytes':s['size'],'sha256':sha(e.contents(s))} for s in e.sections if s['flags']&2 and s['size']],key=lambda s:s['offset'])
    assert all(a['offset']+a['bytes']<=b['offset'] for a,b in zip(sections,sections[1:]))
    old=Elf32((base/'exp.elf').read_bytes(),'prior');assert sha((base/'exp.elf').read_bytes())==prior['elf_sha256']
    for sec in old.sections:
        if sec['flags']&2 and sec['size']:
            current=next(s for s in e.sections if s['name']==sec['name']);assert current['address']==sec['address'] and e.contents(current)==old.contents(sec)
    (out/'twins.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'prior':prior,'source_sha256':sha(source.read_bytes()),'compile_command':cmd,'sections':sections,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['Fresh C forwarding functions and complete source dependencies at original entries. Execution/integration pending.']}
    (ROOT/'docs/research/gx8002-comparison-twins-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print([s for s in build()['sections'] if 'twin' in s['name']])
