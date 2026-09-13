# SPDX-License-Identifier: MIT
"""Review proposed fill transfer without changing live admission baselines."""
import json,copy
from build_gx8002_app_command_callback_persistent import build,ROOT,IMAGE,Elf32,sha
from build_gx8002_source_candidate import reviewed_replacements,compose

def verify():
    candidate=build();stock=IMAGE.read_bytes()
    reviewed=json.loads((ROOT/'docs/research/gx8002-app-commands-source-verification.json').read_text())
    owner=copy.deepcopy(reviewed);text=owner['functions'][0];occ=text['stock_occurrences'][0]
    if occ['package_offset']!=0x127e4 or occ['bytes'] not in (384,388) or text['compiled_bytes']!=384:raise ValueError('Owner changed')
    occ['bytes']=384;occ['sha256']=sha(stock[0x127e4:0x12964])
    replacements=reviewed_replacements(owner,owner,ROOT/'build/gx8002-app-commands/candidate.elf','app-commands')
    path=ROOT/'build/gx8002-app-command-callback-persistent/candidate.elf';elf=Elf32(path.read_bytes(),'persistent');rows=[]
    for section in elf.sections:
        if not section['flags']&2 or not section['size']:continue
        name=section['name'];offset=section['address']-0x101f6a74;data=elf.contents(section)
        if name=='.text':
            if offset!=0x129bc or len(data)>716:raise ValueError('Code placement')
            size=716;kind='compiled_c'
        elif name=='.rodata.delay_response':
            if offset!=0x12964 or data!=b'\x01':raise ValueError('Response placement')
            size=1;kind='generated_source_data'
        else:
            if not name.startswith('.rodata.') or data!=stock[offset:offset+len(data)]:raise ValueError('Diagnostic')
            size=len(data);kind='generated_source_data'
        if elf.relocations(section['index']):raise ValueError('Relocation')
        rows.append({'symbol':name,'section_name':name,'ownership_kind':kind,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_xip_text','symbol':name}]})
    if len(rows)!=20:raise ValueError('Unexpected section count')
    report={'functions':rows};replacements+=reviewed_replacements(report,report,path,'persistent-callback')
    compose(stock,replacements)
    return {'candidate':candidate,'proposed_owner_bytes':384,'transferred_offset':0x12964,'transferred_bytes':1,'replacements':len(replacements),'source_admitted':False,'limits':['In-memory proposed ownership transfer and real composition validated; live registry and admission reports unchanged. The remaining three bytes are unclaimed stock padding; no data section claims unreachable code fill.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-callback-persistent-allocation.json').write_text(json.dumps(r,indent=2)+'\n');print('Proposed ownership transfer composes successfully')
