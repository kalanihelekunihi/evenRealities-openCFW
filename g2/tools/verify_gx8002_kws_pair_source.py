# SPDX-License-Identifier: MIT
"""Qualify compiler-produced KWS pair for experimental hybrid replacement."""
import json,re,shutil
from verify_gx8002_kws_pair_layout import verify as layout,ROOT,sha,Elf32
from verify_gx8002_audio_completion_lifecycle import verify as lifecycle
from verify_gx8002_kws_run_cache import verify as cache
from verify_gx8002_kws_run_task_initialize import verify as task
from verify_gx8002_kws_run_context import verify as context
from verify_gx8002_kws_run_submission import verify as submission
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'lifecycle':lifecycle(),'cache_and_memory':cache(),'task':task(),'context':context(),'submission':submission()}
    # Build the final paired artifact last; compare against standalone linked C.
    checks['layout']=layout()
    path=ROOT/'build/gx8002-board/kws-pair.elf';elf=Elf32(path.read_bytes(),'KWS pair')
    sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1
    section=sections[0];data=elf.contents(section);offset=0x180e4;size=220
    assert section['name']=='.text' and section['address']==0x100260d0
    assert len(data)==216 and not elf.relocations(section['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-kws-pair-source-verification.json':continue
        report=ROOT/'docs/research'/name
        if not report.exists():continue
        value=json.loads(report.read_text())
        for row in value.get('functions',[value]):
            for occurrence in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                start=occurrence.get('package_offset');length=occurrence.get('bytes')
                if start is not None and length is not None and start<offset+size and offset<start+length:
                    raise ValueError(('KWS pair ownership overlap',name))
    symbol='open_cfw_gx8002_kws_pair'
    rows=[{'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,'sha256':sha(stock[offset:offset+size]),'region':'image_a_sram'}]}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'kws-pair.elf')
    files=sorted({p.name for pattern in ('*gx8002_kws_pair*.py','*gx8002_kws_run*.py','*gx8002_audio_completion*.py') for p in (ROOT/'tools').glob(pattern)})
    return {'functions':rows,'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission; full composed build and hardware qualification remain separate.','Compiler-produced assembly is rearranged with guarded pool placement; no stock byte extraction. Literal pool bytes are included in compiled text accounting.','Helper integrations are separate experiments, not one fully composed execution. Physical hardware and model graph/weight source reconstruction remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-pair-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('KWS pair experimental admission passed')
