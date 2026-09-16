# SPDX-License-Identifier: MIT
"""Build pinned upstream cosine and sine table; no stock bytes are build inputs."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';out=ROOT/'build/gx8002-backup-cosine';out.mkdir(exist_ok=True);provenance=[];sources=[]
    for rel in ('utility/libdsp/Source/FastMathFunctions/csky_cos_f32.c','utility/libdsp/Source/CommonTables/csky_common_fastmath_tables.c'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=subprocess.check_output(['git','-C',str(sdk),'show',blob]);assert subprocess.check_output(['git','hash-object','--stdin'],input=data,text=False).decode().strip()==blob
        provenance.append({'path':rel,'git_blob':blob,'sha256':sha(data)});sources.append(data.decode());(out/rel.split('/')[-1]).write_bytes(data)
    # Match the stock ordered >= zero comparison; casts already require finite range.
    assert sources[0].count('if(in < 0.0f)')==1
    (out/'cosine-adapted.c').write_text(sources[0].replace('if(in < 0.0f)', 'if(!(in >= 0.0f))'))
    # Compile with a minimal declaration-only facade.
    (out/'csky_math.h').write_text('#include <stdint.h>\ntypedef float float32_t;\n#define FAST_MATH_TABLE_SIZE 512\n')
    (out/'csky_common_tables.h').write_text('extern const float sinTable_f32[513];\n')
    table=re.search(r'const float32_t sinTable_f32\[FAST_MATH_TABLE_SIZE \+ 1\] = \{.*?\};',sources[1],re.S);assert table
    # Keep the upstream copyright/license preamble, selecting the named source
    # declaration rather than extracting any firmware data.
    (out/'sine-table.c').write_text(sources[1].split('#include')[0]+'#include "csky_math.h"\n'+table.group()+'\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    for src,obj in (('cosine-adapted.c','cosine.o'),('sine-table.c','table.o')):
        subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(out),'-c',str(out/src),'-o',str(out/obj)],check=True)
    (out/'cosine.ld').write_text('SECTIONS { .cosine 0x1000ee64 : { *(.text*) } .sine_table 0x100148d4 : { *(.rodata*) } }\n')
    path=out/'cosine.elf';subprocess.run([pre+'ld','-T',str(out/'cosine.ld'),str(out/'cosine.o'),str(out/'table.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'cosine');sections={s['name']:s for s in elf.sections};body=elf.contents(sections['.cosine']);tablebytes=elf.contents(sections['.sine_table']);offset=0x148d4+0x38940
    assert len(tablebytes)==513*4
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'cosine.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'sdk_commit':SDK_COMMIT,'upstream':provenance,'bytes':len(body),'envelope_bytes':128,'fits':len(body)<=128,'exact_code':body==stock[0x477a4:0x477a4+len(body)],'table_bytes':len(tablebytes),'exact_table':tablebytes==stock[offset:offset+len(tablebytes)],'source_admitted':False,'limits':['Upstream condition adapted from < zero to !(>= zero), matching stock comparison; defined finite conversion domain only. Declaration-only facade used. Table selected from upstream C, not firmware. Decoded floating-point execution and placement verification remain pending.']}
    (ROOT/'docs/research/gx8002-backup-cosine.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(build())
