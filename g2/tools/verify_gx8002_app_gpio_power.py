# SPDX-License-Identifier: MIT
"""GPIO callback call-order oracle and exact compiled instruction checks."""
import json,shutil
from itertools import product
from build_gx8002_app_gpio_power import build,ROOT,IMAGE,sha,Elf32
from execute_gx8002_app_gpio_power import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();path=ROOT/'build/gx8002-app-gpio-power/offsets.elf';elf=Elf32(path.read_bytes(),str(path));code=decode((path.parent/'offsets.disassembly.txt').read_text());rows=[];cases=0
    for i,item in enumerate(evidence['functions']):
        if not item['fits'] or not item['exact_stock_prefix']:raise ValueError('Exact source')
        sec=next(s for s in elf.sections if s['name']=='.text.'+item['symbol'])
        if sec['address']!=item['package_offset']+0x101f6a74 or elf.relocations(sec['index']):raise ValueError('Placement')
        for name,result in product((0,0x20040000,0xffffffff),(0,1,0xffffffff)):
            expected=[(0x10206c24,(0x1020b443 if i else 0x1020b43b,name))]
            expected+=([(0x102065dc,(6,1)),(0x10205f24,(6,0)),(0x10205fb4,(6,1,0x10208e20,0))] if i else [(0x10206074,(6,)),(0x102065dc,(6,0))])
            def helper(target,args,m,events):
                lengths={0x10206c24:2,0x102065dc:2,0x10205f24:2,0x10205fb4:4,0x10206074:1}
                events.append((target,tuple(args[:lengths[target]])));return result
            ret,m,events=execute(code,sec['address'],name,0,{},helper)
            if (ret,m,events)!=(('return',0),{},expected):raise ValueError('Callback oracle')
            cases+=1
        rows.append({'symbol':item['symbol'],'section_name':sec['name'],'compiled_bytes':item['compiled_bytes'],'compiled_sha256':item['compiled_sha256'],'stock_occurrences':[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]})
    sec=next(s for s in elf.sections if s['name']=='.rodata');data=elf.contents(sec);offset=0x149c7;stock=IMAGE.read_bytes()
    if sec['address']!=0x1020b43b or data!=stock[offset:offset+len(data)] or data[8:]!=b'%s\n\0':raise ValueError('Shared diagnostic')
    rows.append({'symbol':'open_cfw_gx8002_app_gpio_message','section_name':'.rodata','ownership_kind':'generated_source_data','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':'open_cfw_gx8002_app_gpio_message','package_offset':offset,'bytes':len(data),'sha256':sha(data),'region':'image_a_xip_text'}]})
    if output:output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'gpio-power.elf')
    return {'functions':rows,'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Exact stock code and independent helper-order oracle. Physical GPIO, nested helpers and asynchronous callback behavior remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-app-gpio-power-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
