# SPDX-License-Identifier: MIT
"""Check exact getter encoding and binding to existing keyword-list owner."""
import json
from build_gx8002_keyword_list_get import build,ROOT,sha,Elf32

def verify():
    candidate=build();p=ROOT/'build/gx8002-keyword-list-get/get.elf';elf=Elf32(p.read_bytes(),'get');s=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(s);base=s['address']
    # Short LRW r0 followed by return; the encoded offset addresses its own literal.
    assert int.from_bytes(data[:2],'little')==0x1001 and data[2:4]==bytes.fromhex('3c78')
    literal_address=(base&~3)+4*(int.from_bytes(data[:2],'little')&31);assert literal_address==base+4
    target=int.from_bytes(data[4:],'little');assert target==0x2002e79c
    p=ROOT/'build/gx8002-source-candidate/max-list/max-list.elf';owner=Elf32(p.read_bytes(),'owner');report=json.loads((ROOT/'docs/research/gx8002-max-list-verification.json').read_text())
    for row in report['functions']:
        section=next(s for s in owner.sections if s['name']==row['section_name']);assert sha(owner.contents(section))==row['compiled_sha256']
    symbol=next(s for s in owner.symbols() if s['name']=='open_cfw_gx8002_max_keyword_list');section=owner.sections[symbol['section']]
    assert (symbol['value'],symbol['size'],section['address'],section['size'],section['type'])==(target,8,target,8,8)
    return {'candidate':candidate,'owner_elf_sha256':sha(p.read_bytes()),'owner_symbol':symbol,'literal_address':literal_address,'returned_address':target,'source_admitted':False,'hardware_qualified':False,'limits':['Exact LRW/return encoding yields the existing 8-byte source NOBITS list address without reading or modifying the list.','Read-only owner authentication and ABI binding; runtime list population already separately qualified. No registry admission here.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-keyword-list-get-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Keyword-list source owner verified')
