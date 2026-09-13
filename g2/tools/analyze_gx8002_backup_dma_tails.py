# SPDX-License-Identifier: MIT
"""Authenticate residual combined-layout bytes and conservatively census references."""
import json,re,subprocess
from build_gx8002_backup_dma_combined import ROOT,Elf32,sha
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA
from verify_gx8002_memcpy_source import decode

def analyze():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    disassembly=subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3b940','--stop-address=0x4ee5c',str(p)],text=True)
    code=decode(disassembly)
    rows=[]
    for start,end in ((0x3d5b8,0x3d5bc),(0x3d6cc,0x3d6d4)):
        runtime=start-0x3b940+0x10003000
        words=[{'package_offset':i,'value':int.from_bytes(stock[i:i+4],'little')} for i in range(start,end,4)]
        pointers=[{'package_offset':i,'value':int.from_bytes(stock[i:i+4],'little')} for i in range(0x3893c,0x4f9cc-3) if runtime<=int.from_bytes(stock[i:i+4],'little')<runtime+end-start]
        branches=[]
        for pc,(op,args,width) in code.items():
            if op not in ('br','bsr','bt','bf','bez','bnez','bnezad'):continue
            try:target=int(args.split(',')[-1].strip(),0)
            except ValueError:continue
            if start<=target<end:branches.append({'package_offset':pc,'target':target})
        literal_loads=[]
        for line in disassembly.splitlines():
            match=re.match(r'\s*([0-9a-f]+):.*\blrw\s+.*//\s*([0-9a-f]+)\s',line)
            if match and start<=int(match[2],16)<end:
                literal_loads.append({'package_offset':int(match[1],16),'pool_offset':int(match[2],16)})
        rows.append({'literal_loads':literal_loads,'package_interval':[start,end],'runtime_interval':[runtime,runtime+end-start],'words':words,'runtime_pointer_matches':pointers,'direct_branch_matches':branches})
    return {'image_sha256':IMAGE_SHA,'tails':rows,'source_admitted':False,'limits':['Linear disassembly and literal census do not resolve computed references. Residual words are stock literal pools, not yet admitted fill.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-backup-dma-tails.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
