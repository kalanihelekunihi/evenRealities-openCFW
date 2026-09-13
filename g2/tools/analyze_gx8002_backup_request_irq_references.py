# SPDX-License-Identifier: MIT
"""Conservative external reference census for the backup IRQ registration helper."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    start,end=0x3d184,0x3d1ac;entries={start};runtime=start-0x3b940+0x10003000
    text=subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3b940','--stop-address=0x4ee5c',str(p)],text=True)
    branches=[];loads=[];words=[]
    for pc,(op,args,width) in decode(text).items():
        if start<=pc<end or op not in ('br','bsr','bt','bf','bez','bnez','bnezad','bhz','blz','bhsz','blsz'):continue
        try:target=int(args.split(',')[-1].strip(),0)
        except ValueError:continue
        if start<=target<end:branches.append({'offset':pc,'target':target,'entry':target in entries})
    for line in text.splitlines():
        m=re.match(r'\s*([0-9a-f]+):.*\blrw\s+.*//\s*([0-9a-f]+)\s',line)
        if m:
            pc,target=(int(v,16) for v in m.groups())
            if not start<=pc<end and start<=target<end:loads.append({'offset':pc,'pool':target})
    for offset in range(0x3893c,0x4f9cc-3):
        value=int.from_bytes(stock[offset:offset+4],'little')
        if runtime<=value<runtime+end-start:
            words.append({'offset':offset,'value':value,'entry':value == runtime})
    return {'image_sha256':IMAGE_SHA,'package_interval':[start,end],'external_branches':branches,'external_pool_loads':loads,'runtime_word_matches':words,'source_admitted':False,'limits':['Linear decode and word census; computed references and nonstandard entry paths are not proven absent.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-backup-request-irq-references.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
