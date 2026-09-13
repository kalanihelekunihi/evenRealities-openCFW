# SPDX-License-Identifier: MIT
"""Resolve typed descriptor references to authenticated allocated source owners."""
import json,re,struct
from build_gx8002_mode_descriptors import build,ROOT,sha,Elf32

def verify():
    candidate=build();wanted=candidate['bindings'];owners={name:[] for name in wanted}
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for kind,artifact,report_name in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'(gx8002-[^']+\.json)'\)",registry):
        p=ROOT/'build/gx8002-source-candidate'/kind/artifact;assert p.exists(),kind;elf=Elf32(p.read_bytes(),kind)
        for symbol in elf.symbols():
            name=symbol['name']
            if name not in wanted or not 0<symbol['section']<len(elf.sections):continue
            s=elf.sections[symbol['section']]
            if not s['flags']&2 or not s['size']:continue
            assert symbol['value']==wanted[name] and s['address']<=symbol['value']<s['address']+s['size']
            report=json.loads((ROOT/'docs/research'/report_name).read_text());matches=[r for r in report.get('functions',[report]) if r.get('symbol')==name or r.get('section_name')==s['name']]
            assert any(r.get('compiled_sha256')==sha(elf.contents(s)) for r in matches),(kind,name)
            owners[name].append({'kind':kind,'section':s['name'],'symbol':symbol,'elf_sha256':sha(p.read_bytes())})
    assert all(len(v)==1 for v in owners.values()),{k:len(v) for k,v in owners.items()}
    p=ROOT/'build/gx8002-mode-descriptors/descriptors.elf';elf=Elf32(p.read_bytes(),'descriptors');sections={s['name']:s for s in elf.sections}
    mode_list=struct.unpack('<2I',elf.contents(sections['.mode_list']));info=struct.unpack('<5I',elf.contents(sections['.tws_info']))
    assert mode_list==(wanted['lvp_idle_mode_info'],sections['.tws_info']['address'])
    assert info==(1,wanted['open_cfw_gx8002_tws_init'],wanted['open_cfw_gx8002_tws_done'],wanted['open_cfw_gx8002_tws_tick'],wanted['open_cfw_gx8002_tws_buffer_init'])
    return {'candidate':candidate,'source_owners':owners,'source_admitted':False,'hardware_qualified':False,'limits':['Each external callback/idle descriptor resolves to exactly one allocated registered source owner authenticated by reviewed section hash. List points to existing idle and new TWS descriptor.','Indirect mode dispatch execution and package overlap qualification pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-mode-descriptor-bindings.json').write_text(json.dumps(r,indent=2)+'\n');print('Mode descriptor source owners:',len(r['source_owners']))
