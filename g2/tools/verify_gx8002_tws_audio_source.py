# SPDX-License-Identifier: MIT
"""Experimental TWS audio callback and diagnostic source admission."""
import json,re,shutil
from verify_gx8002_tws_audio import verify as behavior
from verify_gx8002_tws_audio_mutation import verify as mutation
from verify_gx8002_tws_audio_standby import verify as standby
from verify_gx8002_tws_audio_mic import verify as microphone
from verify_gx8002_tws_audio_ownership import verify as ownership
from build_gx8002_tws_audio_candidate import ROOT,IMAGE,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);checks={'behavior':behavior(),'mutation':mutation(),'standby':standby(),'microphone':microphone(),'ownership':ownership()};path=ROOT/'build/gx8002-board/tws-audio.elf';elf=Elf32(path.read_bytes(),'standby');stock=IMAGE.read_bytes();rows=[]
    for name,symbol,offset,size,address,kind,region in (('.text','open_cfw_gx8002_tws_audio_callback',0x183f0,248,0x100263dc,'compiled_c','image_a_sram'),):
        section=next(s for s in elf.sections if s['name']==name);data=elf.contents(section);assert section['address']==address and len(data)==size and not elf.relocations(section['index'])
        rows.append({'symbol':symbol,'section_name':name,'ownership_kind':kind,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':region}]})
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",(ROOT/'tools/build_gx8002_source_candidate.py').read_text())):
        if name=='gx8002-tws-audio-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        report=json.loads(p.read_text())
        for row in report.get('functions',[report]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not any(a<end and start<a+n for start,end in ((0x183f0,0x184e8),)),name
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'audio.elf')
    files=sorted(p.name for p in (ROOT/'tools').glob('*gx8002_tws_audio*.py'))
    return {'functions':rows,'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission; Callback pointer constants included; diagnostic already owned by runtime-messages. Four-byte last-VAD BSS allocated and startup clear checked. Physical execution/full firmware reconstruction remain unfinished.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-audio-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('TWS audio qualification passed')
