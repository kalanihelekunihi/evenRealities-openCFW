# SPDX-License-Identifier: MIT
"""Authenticate public audio-output wrappers and locate nonrelocated matches."""
import json,subprocess,struct
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/audio_out.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);elf=Elf32(data,rel);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Public audio stock identity')
    rows=[];symbols=elf.symbols()
    for section in elf.sections:
        if not section['name'].startswith('.text.') or not section['size']:continue
        body=elf.contents(section);relocations=elf.relocations(section['index']);skip={i for r in relocations for i in range(r['offset'],r['offset']+4)};matches=[];offset=stock.find(body[:2])
        while offset>=0:
            if offset%2==0 and offset+len(body)<=len(stock) and all(stock[offset+i]==value for i,value in enumerate(body) if i not in skip):
                literals=[]
                for r in relocations:
                    symbol=symbols[r['symbol']];target=symbol['name'] or elf.sections[symbol['section']]['name']
                    item={'relative_offset':r['offset'],'type':r['type'],'upstream_target':target,'addend':r['addend']}
                    if r['type']==1:
                        value=struct.unpack_from('<I',stock,offset+r['offset'])[0];item['stock_pointer']=value
                        if 0x101f6a74<=value<0x101f6a74+len(stock) and ('str' in target or 'rodata' in target):
                            start=value-0x101f6a74;end=stock.find(b'\0',start,min(start+512,len(stock)))
                            if end>=0:item['stock_string']=stock[start:end].decode('utf-8',errors='replace')
                    literals.append(item)
                matches.append({'package_offset':offset,'runtime_address':offset+0x101f6a74,'stock_sha256':sha(stock[offset:offset+len(body)]),'relocations':literals})
            offset=stock.find(body[:2],offset+2)
        rows.append({'section':section['name'],'bytes':len(body),'matches':matches})
    return {'sdk_commit':SDK_COMMIT,'oracle':{'path':rel,'blob':blob,'sha256':sha(data)},'stock_sha256':IMAGE_SHA,'functions':rows,'limits':['Matches exclude relocation bytes; literal targets reported separately. This is location/provenance evidence, not source admission or behavior qualification.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-audio-output-public-identities.json').write_text(json.dumps(r,indent=2)+'\n');print([(x['section'],[hex(m['package_offset']) for m in x['matches']]) for x in r['functions']])
