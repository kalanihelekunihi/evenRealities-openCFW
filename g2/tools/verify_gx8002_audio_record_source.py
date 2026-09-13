# SPDX-License-Identifier: MIT
"""Qualification adapter for recovered audio record callback and C state."""
import json,re,shutil
from verify_gx8002_audio_record_read_update import verify as compare
from verify_gx8002_audio_record_state import verify as state_check
from build_gx8002_audio_record_candidate import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();state=state_check()
    assert not state['missing_artifacts'] and not state['overlapping_allocations']
    path=ROOT/'build/gx8002-board/audio-record.elf';elf=Elf32(path.read_bytes(),'audio record');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==4
    text=next(s for s in sections if s['name']=='.text');payload=elf.contents(text)
    assert text['address']==0x10026214 and len(payload)<=256 and not elf.relocations(text['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert sha(path.read_bytes())==state['candidate_elf_sha256']==evidence['evidence']['candidate']['elf_sha256']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    offset=0x18228;size=256;registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-audio-record-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        report=json.loads(p.read_text())
        for row in report.get('functions',[report]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=occurrence.get('package_offset');n=occurrence.get('bytes')
                if a is not None and n is not None and a<offset+size and offset<a+n:raise ValueError(('Audio record overlap',name))
    symbol='open_cfw_gx8002_audio_record_callback'
    row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_sram'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'audio-record.elf')
    files=sorted(p.name for p in (ROOT/'tools').glob('*gx8002_audio_record*.py'))
    return {'functions':[row],'evidence':evidence,'runtime_state':state,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission; full composed build remains a separate check.','Startup state and decoded read-index integration qualified; other helpers and application body modeled. Full firmware source reconstruction and physical execution remain unfinished.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-record-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio record qualification passed')
