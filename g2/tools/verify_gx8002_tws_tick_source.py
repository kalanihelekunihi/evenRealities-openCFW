# SPDX-License-Identifier: MIT
"""Qualification adapter for recovered TWS tick text using shared source pool."""
import json,re,shutil
from verify_gx8002_tws_tick_mutation import verify as mutation
from verify_gx8002_tws_tick_queue import verify as queue
from verify_gx8002_tws_tick_lock import verify as lock
from verify_gx8002_tws_tick_pool import verify as pool
from build_gx8002_tws_tick_candidate import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);checks={'mutation':mutation(),'queue':queue(),'lock':lock(),'pool':pool()}
    path=ROOT/'build/gx8002-board/tws-tick-split.elf';elf=Elf32(path.read_bytes(),'tick');section=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(section)
    assert section['address']==0x10026358 and len(body)==90 and not elf.relocations(section['index'])
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA and body==stock[0x1836c:0x183c6]
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-tws-tick-source-verification.json':continue
        p=ROOT/'docs/research'/name
        if not p.exists():continue
        report=json.loads(p.read_text())
        for row in report.get('functions',[report]):
            for o in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                a=o.get('package_offset');n=o.get('bytes')
                if a is not None and n is not None:assert not (a<0x183c8 and 0x1836c<a+n),name
    symbol='open_cfw_gx8002_tws_tick';row={'symbol':symbol,'section_name':'.text','ownership_kind':'compiled_c','compiled_bytes':90,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x1836c,'bytes':92,'sha256':sha(stock[0x1836c:0x183c8]),'region':'image_a_sram'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'tws-tick.elf')
    files=sorted(p.name for p in (ROOT/'tools').glob('*gx8002_tws_tick*.py'))
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'limits':['Experimental hybrid admission; full composed build is separate. Only text claimed; linked pool duplicates already registered source data for relocation checking, not replacement.','Queue read and lock query decoded separately; decoder, event, suspend and complete lifecycle remain modeled/unqualified. Exact stock instructions do not prove complete firmware hardware execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-tick-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('TWS tick qualification passed')
