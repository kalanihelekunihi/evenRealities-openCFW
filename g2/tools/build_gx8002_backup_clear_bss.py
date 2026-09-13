# SPDX-License-Identifier: MIT
"""Build backup BSS clear on macOS; candidate only."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-backup-clear-bss';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_clear_bss.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'clear.o')],check=True)
    rt=lambda p:p-0x3b940+0x10003000
    bindings={'open_cfw_gx8002_backup_bss_start':0x20017090,'open_cfw_gx8002_backup_bss_end':0x2002d79c}
    script=out/'clear.ld'
    script.write_text('SECTIONS { .text %#x : { *(.text*) } .bounds 0x10003144 : { *(.backup_bss_bounds) } }\n'%rt(0x3ba68)+''.join('%s = %#x;\n'%(k,v) for k,v in bindings.items()))
    subprocess.run([pre+'ld','-T',str(script),str(out/'clear.o'),'-o',str(out/'clear.elf')],check=True)
    e=Elf32((out/'clear.elf').read_bytes(),'candidate');s=next(s for s in e.sections if s['name']=='.text');body=e.contents(s)
    assert not e.relocations(s['index']) and not any(s['name'] and s['section']==0 for s in e.symbols())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    bounds=next(s for s in e.sections if s['name']=='.bounds')
    assert s['size']==28 and bounds['address']==0x10003144 and bounds['size']==8
    assert e.contents(bounds)==stock[0x3ba84:0x3ba8c]
    (out/'clear.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'clear.elf')],text=True))
    return {'source_sha256':sha(source.read_bytes()),'bounds_sha256':sha(e.contents(bounds)),'compiled_bytes':len(body),'compiled_sha256':sha(body),'envelope_bytes':36,'fits':len(body)<=36,'bindings':bindings,'source_admitted':False,'limits':['Candidate only; decoded equivalence and placement pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-clear-bss-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
