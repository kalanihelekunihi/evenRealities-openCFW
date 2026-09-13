# SPDX-License-Identifier: MIT
"""Native compilation of recovered threshold-offset accessors."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-bionic-offsets';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_bionic_offsets.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    functions=[('open_cfw_gx8002_bunkws_offset',0x120e4,12),('open_cfw_gx8002_ctc_offset_clear',0x120f0,4),('open_cfw_gx8002_bunkws_offset_clear',0x120f4,16)]
    flags=['-Os',*FLAGS[1:]];subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'offsets.o')],check=True)
    script=out/'offsets.ld';script.write_text('SECTIONS {\n'+''.join(f'.text.{name} {offset+0x101f6a74:#x} : {{ *(.text.{name}) }}\n' for name,offset,size in functions)+'}\nopen_cfw_gx8002_bionic_state = 0x2002e84c;\n')
    p=out/'offsets.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'offsets.o'),'-o',str(p)],check=True);e=Elf32(p.read_bytes(),str(p));stock=IMAGE.read_bytes();rows=[]
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock')
    for name,offset,size in functions:
        sec=next(s for s in e.sections if s['name']=='.text.'+name);data=e.contents(sec)
        if e.relocations(sec['index']):raise ValueError('Relocation')
        rows.append({'symbol':name,'package_offset':offset,'compiled_bytes':len(data),'compiled_sha256':sha(data),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'fits':len(data)<=size,'exact_stock_prefix':data==stock[offset:offset+len(data)]})
    (out/'offsets.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(p)],text=True))
    r={'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':rows,'source_admitted':False,'limits':['Native candidates only; getter float bits, clear ordering, ABI and ownership need qualification.']};(ROOT/'docs/research/gx8002-bionic-offsets-candidate.json').write_text(json.dumps(r,indent=2)+'\n');return r
if __name__=='__main__':print(json.dumps(build(),indent=2))
