# SPDX-License-Identifier: MIT
"""Read-only authenticated clock lookup/table context for switching tests."""
import json,struct
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def load():
    path=ROOT/'build/gx8002-platform-gate/tables.elf';elf=Elf32(path.read_bytes(),'clock context')
    report=json.loads((ROOT/'docs/research/gx8002-clock-source-verification.json').read_text());stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    memory={};sections={};hashes={}
    for row in report['functions']:
        name=row.get('section_name','.text.'+row['symbol']);s=next(s for s in elf.sections if s['name']==name);data=elf.contents(s)
        assert len(data)==row['compiled_bytes'] and sha(data)==row['compiled_sha256'] and not elf.relocations(s['index'])
        hashes[name]=sha(data)
        if row.get('ownership_kind')!='generated_source_data':continue
        occurrence=row['stock_occurrences'][0];off=occurrence['package_offset']
        assert data==stock[off:off+occurrence['bytes']]
        assert s['address']==off+0x2000dfec
        assert not any(s['address']+i in memory for i in range(len(data)))
        memory.update({s['address']+i:v for i,v in enumerate(data)});sections[row['symbol']]=(s['address'],data)
    base,data=sections['gx_clock_param_table'];assert base==0x200266e0 and len(data)==26*16
    divbase,divs=sections['gx_clock_div_table'];dtobase,dtos=sections['gx_clock_dto_table'];modules=[]
    for i in range(26):
        module,high,all_gate,clock,divider,dto=struct.unpack_from('<IbbbxII',data,16*i)
        assert 0<=module<26 and all(-1<=v<32 for v in (high,all_gate,clock))
        assert divider==0 or (divbase<=divider<divbase+len(divs) and (divider-divbase)%4==0)
        assert dto==0 or dtobase<=dto<dtobase+len(dtos)
        modules.append({'module':module,'table_index':i,'address':base+16*i,'gate_high_offset':high,'gate_all_offset':all_gate,'clock_offset':clock,'divider':divider,'dto':dto})
    assert sorted(x['module'] for x in modules)==list(range(26))
    pairs={str(i):[modules[i+1]['module'],modules[i+2]['module']] for i in (16,19,22)}
    return memory,{'elf_sha256':sha(path.read_bytes()),'section_sha256':hashes,'modules':modules,'combined_gate_index_pairs':pairs,'limits':['Immutable source table context and lookup code authentication; successful module switching still needs decoded qualification.']}
if __name__=='__main__':
    memory,r=load();(ROOT/'docs/research/gx8002-clock-switch-context.json').write_text(json.dumps(r,indent=2)+'\n');print('Authenticated modules:',len(r['modules']),'data bytes:',len(memory))
