#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build C fill implementation; pinned objects are lineage oracles only."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-board';deps=[];oracle=None
    for rel in ('utility/libc/memset.c','utility/libc/csky/memset_fast.o','LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob)
        deps.append({'path':rel,'blob':blob,'sha256':sha(data)})
        if rel.endswith('.o'):
            e=Elf32(data,rel);oracle=e.contents(next(s for s in e.sections if s['name']=='.text'))
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or stock[0x12f58:0x12f5a]!=bytes.fromhex('4474') or oracle!=stock[0x12f5a:0x12ff8]:raise ValueError('memset lineage')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_memset.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'memset-candidate.o')],check=True)
    script=out/'memset-candidate.ld';script.write_text('SECTIONS { .text 0x102099cc : { *(.text.open_cfw_gx8002_memset) } }\n')
    p=out/'memset-candidate.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'memset-candidate.o'),'-o',str(p)],check=True)
    e=Elf32(p.read_bytes(),str(p));s=next(s for s in e.sections if s['name']=='.text');payload=e.contents(s)
    if e.relocations(s['index']) or any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('memset link invariant')
    (out/'memset-candidate.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    report={'sdk_commit':SDK_COMMIT,'dependencies':deps,'flags':flags,'source_sha256':sha(source.read_bytes()),'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':0x12f58,'stock_envelope_bytes':160,'stock_sha256':sha(stock[0x12f58:0x12ff8]),'fits':len(payload)<=160,'source_admitted':False,'limits':['Candidate only. Need decoded store width/order, alignment, return, ABI and signed count boundary qualification; retained object supplies no output bytes.']}
    (ROOT/'docs/research/gx8002-memset-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
