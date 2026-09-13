# SPDX-License-Identifier: MIT
"""Link audio buffer initialization using authenticated SDK layout headers."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha,authenticated_blob
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';evidence={}
    for rel in ('include/lvp_context.h','include/lvp_attr.h','lvp/common/lvp_buffer.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);evidence[rel]={'blob':blob,'sha256':sha(data)}
    out=ROOT/'build/gx8002-buffer-initialize';out.mkdir(parents=True,exist_ok=True);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');source=ROOT/'components/shared/gx8002/runtime_gx8002_buffer_initialize.c'
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(sdk/'include'),'-c',str(source),'-o',str(out/'buffer.o')],check=True)
    (out/'buffer.ld').write_text('SECTIONS { .text 0x10206dc0 : { *(.text.open_cfw_gx8002_buffer_initialize) } }\nmemset = 0x102099cc;\n')
    subprocess.run([pre+'ld','-T',str(out/'buffer.ld'),str(out/'buffer.o'),'-o',str(out/'buffer.elf')],check=True)
    elf=Elf32((out/'buffer.elf').read_bytes(),'buffer.elf');section=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(section)
    if any(elf.relocations(s['index']) for s in elf.sections) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('Unresolved link')
    if any(s['size'] and s['flags']&2 and s['name']!='.text' for s in elf.sections):raise ValueError('Unowned allocation')
    (out/'buffer.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'buffer.elf')],text=True))
    return {'compiled_bytes':len(payload),'fits':len(payload)<=172,'compiled_sha256':sha(payload),'stock_sha256':sha(stock[0x1034c:0x103f8]),'source_sha256':sha(source.read_bytes()),'upstream':evidence,'source_admitted':False}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-buffer-initialize-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['compiled_bytes'])
