# SPDX-License-Identifier: MIT
"""Build recovered upstream-layout logfbank indexing on native macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';upstream={}
    for rel in ('include/lvp_context.h','include/lvp_attr.h','lvp/common/lvp_buffer.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        upstream[rel]={'blob':blob,'sha256':sha(authenticated_blob(sdk/rel,blob))}
    out=ROOT/'build/gx8002-logfbank-index';out.mkdir(parents=True,exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_logfbank_index.c';flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-I',str(sdk/'include'),'-c',str(source),'-o',str(out/'index.o')],check=True)
    (out/'index.ld').write_text('SECTIONS { .text 0x10206eac : { *(.text.open_cfw_gx8002_logfbank_index) } }\n')
    subprocess.run([pre+'ld','-T',str(out/'index.ld'),str(out/'index.o'),'-o',str(out/'index.elf')],check=True)
    elf=Elf32((out/'index.elf').read_bytes(),'index');section=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(section)
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unowned allocation')
    (out/'index.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'index.elf')],text=True))
    return {'compiled_bytes':len(payload),'fits':len(payload)<=28,'compiled_sha256':sha(payload),'stock_sha256':sha(stock[0x10438:0x10454]),'exact_stock':payload==stock[0x10438:0x10454],'source_sha256':sha(source.read_bytes()),'flags':flags,'upstream':upstream,'source_admitted':False}
if __name__=='__main__':
    report=build();(ROOT/'docs/research/gx8002-logfbank-index-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['compiled_bytes'])
