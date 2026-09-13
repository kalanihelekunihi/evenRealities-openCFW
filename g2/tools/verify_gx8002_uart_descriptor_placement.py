# SPDX-License-Identifier: MIT
"""Check UART descriptor original placement against registered artifacts."""
import json,re
from build_gx8002_uart_descriptor_candidate import build,ROOT,sha,Elf32

def verify():
    evidence=build();references=[];checked=0
    for kind,artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()):
        if kind=='uart-descriptors':continue
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact;assert path.exists(),kind;elf=Elf32(path.read_bytes(),str(path));checked+=1
        for s in elf.sections:
            if s['flags']&2 and s['size'] and s['address']:assert not (s['address']<0x20026b94 and 0x20026a94<s['address']+s['size']),(kind,s['name'])
        for symbol in elf.symbols():
            if symbol['name']=='open_cfw_gx8002_uart_descriptors':
                assert symbol['value']==0x20026a94,(kind,symbol)
                references.append({'kind':kind,'artifact_sha256':sha(path.read_bytes()),'symbol':symbol})
    assert references
    return {'candidate':evidence,'checked_artifacts':checked,'references':references,'source_admitted':False,'limits':['All registered fixed allocated sections nonoverlapping; every exported UART descriptor binding observed at original address. Absolute symbol checks do not exhaust encoded literals/indirect references. Startup data loading and field semantics still pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-descriptor-placement.json').write_text(json.dumps(r,indent=2)+'\n');print(r['checked_artifacts'],len(r['references']))
