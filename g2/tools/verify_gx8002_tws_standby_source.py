# SPDX-License-Identifier: MIT
"""Experimental standby setter/countdown source admission."""
import json,re,shutil
from verify_gx8002_tws_standby_tick import verify as behavior
from verify_gx8002_tws_standby_ownership import verify as ownership
from build_gx8002_tws_standby_candidate import ROOT,IMAGE,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);checks={'behavior':behavior(),'ownership':ownership()};path=ROOT/'build/gx8002-board/tws-standby-split.elf';elf=Elf32(path.read_bytes(),'standby');stock=IMAGE.read_bytes();rows=[]
    for name,symbol,offset,size in (('.setter','open_cfw_gx8002_tws_set_standby',0x183c8,16),('.loop','open_cfw_gx8002_tws_standby_loop',0x183d8,24)):
        section=next(s for s in elf.sections if s['name']==name);data=elf.contents(section);assert section['address']==offset+0x1000dfec and len(data)<=size and not elf.relocations(section['index'])
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':'compiled_c','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_sram'}]})
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text())):
        if name=='gx8002-tws-standby-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        report=json.loads(p.read_text())
        for row in report.get('functions',[report]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not (a<0x183f0 and 0x183c8<a+n),name
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'standby.elf')
    files=sorted(p.name for p in (ROOT/'tools').glob('*gx8002_tws_standby*.py'))
    return {'functions':rows,'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission; shared pool already source-owned and excluded from replacement. Eight-byte BSS allocated and startup clear checked. Physical execution/full firmware reconstruction remain unfinished.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-standby-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Standby qualification passed')
