# SPDX-License-Identifier: MIT
"""Census external CFFT entries, shared literals and stored runtime pointers."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    text=subprocess.check_output([pre,'-D','--start-address=0x3b940','--stop-address=0x4ee5c',str(path)],text=True)
    ranges={'cfft':(0x47b14,0x47bf4)}
    jump_start=0x10012a3c-0x10003000+0x3b940
    results={}
    for name,(start,end) in ranges.items():
        branches=[];loads=[];words=[];runtime=start-0x3b940+0x10003000
        for pc,(op,args,width) in decode(text).items():
            if start<=pc<end or op not in ('br','bsr','bt','bf','bez','bnez','bnezad','bhz','blz','bhsz','blsz'):continue
            try:target=int(args.split(',')[-1].strip(),0)
            except ValueError:continue
            if start<=target<end:branches.append({'offset':pc,'target':target,'entry':target==start})
        for line in text.splitlines():
            m=re.match(r'\s*([0-9a-f]+):.*\blrw\s+.*//\s*([0-9a-f]+)\s',line)
            if m:
                pc,target=(int(v,16) for v in m.groups())
                if not start<=pc<end and start<=target<end:loads.append({'offset':pc,'pool':target})
        for offset in range(0x3893c,0x4f9cc-3):
            value=int.from_bytes(stock[offset:offset+4],'little')
            if runtime<=value<runtime+end-start:
                owned_jump=False
                words.append({'offset':offset,'value':value,'entry':value==runtime,'replaced_switch_word':owned_jump})
        results[name]={'interval':[start,end],'branches':branches,'external_pool_loads':loads,'runtime_words':words}
    tables={}
    for name,address,size in []:
        matches=[]
        for offset in range(0x3893c,0x4f9cc-3):
            value=int.from_bytes(stock[offset:offset+4],'little')
            if address<=value<address+size:
                matches.append({'offset':offset,'value':value,'within_replaced_code':any(a<=offset<b for a,b in ranges.values())})
        tables[name]={'address':address,'bytes':size,'pointer_matches':matches}
    function=results['cfft']
    artifacts=[]
    ready=(all(r['entry'] for r in function['branches'])
           and not function['external_pool_loads']
           and all(r['entry'] for r in function['runtime_words']))
    result={'image_sha256':IMAGE_SHA,'functions':results,'tables':tables,'source_admitted':False,'reference_ready':bool(ready),'literal_data_artifacts':artifacts,
            'limits':['Linear decoded branches and byte-aligned word census; computed and nonstandard entry paths are not globally excluded.',
                      'Raw findings are retained; admission requires all external branches and pointers to target the public entry and no external shared-pool loads.']}
    (ROOT/'docs/research/gx8002-backup-cfft-references.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    r=analyze()
    for name,v in r['functions'].items():
        print(name,'branches',len(v['branches']),'external pools',v['external_pool_loads'],'unexpected words',[x for x in v['runtime_words'] if not x['entry'] and not x['replaced_switch_word']])
    for name,v in r['tables'].items():print(name,v['pointer_matches'])
