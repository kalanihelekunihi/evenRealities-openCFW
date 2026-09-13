# SPDX-License-Identifier: MIT
"""Compile semantically expressed PGA/channel data at deployed locations."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
ROWS=(('pga_corrections',0x13e7a,5),('channel_selectors',0x13f30,12))
def build():
    out=ROOT/'build/gx8002-audio-mapping-tables';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_mapping_tables.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(out/'tables.o')],check=True)
    (out/'tables.ld').write_text('SECTIONS {\n'+''.join(f'.{name} {offset+0x101f6a74:#x} : {{ *(.rodata.{name}) }}\n' for name,offset,size in ROWS)+'}\n');path=out/'tables.elf';subprocess.run([pre+'ld','-T',str(out/'tables.ld'),str(out/'tables.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'tables');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    assert len([s for s in elf.sections if s['flags']&2 and s['size']])==2
    for name,offset,size in ROWS:
        s=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(s);assert s['address']==offset+0x101f6a74 and s['flags']==2 and len(body)==size and body==stock[offset:offset+size] and not elf.relocations(s['index'])
        if name=='pga_corrections':assert all(body[i]==5*(band-3) for i,band in enumerate(range(4,9)))
        else:
            for channel in range(4):assert tuple(body[row*4+channel] for row in range(3))==(int(channel==2),int(channel in (0,2,3)),int(channel==3))
        rows.append({'name':name,'package_offset':offset,'bytes':size,'sha256':sha(body)})
    return {'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'stock_sha256':IMAGE_SHA,'rows':rows,'source_admitted':False,'limits':['Complete finite table domains match recovered PGA correction/channel selector formulas and deployed bytes. No binary input to compilation.','Consumer provenance already exists separately; ownership/admission pending. Does not imply retained tables remain referenced after arithmetic replacements.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-mapping-tables-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio mapping table source bytes:',sum(x['bytes'] for x in r['rows']))
