# SPDX-License-Identifier: MIT
"""Compile recovered readable application messages, excluding neighboring fill."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
ROWS=(('soft_off',0x1441b,18),('sample_labels',0x14bd5,44))
def build():
    out=ROOT/'build/gx8002-application-labels';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_application_labels.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-c',str(source),'-o',str(out/'labels.o')],check=True)
    (out/'labels.ld').write_text('SECTIONS {\n'+''.join(f'.{name} {offset+0x101f6a74:#x} : {{ *(.rodata.{name}) }}\n' for name,offset,size in ROWS)+'}\n');p=out/'labels.elf';subprocess.run([pre+'ld','-T',str(out/'labels.ld'),str(out/'labels.o'),'-o',str(p)],check=True)
    elf=Elf32(p.read_bytes(),'labels');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    assert len([s for s in elf.sections if s['flags']&2 and s['size']])==2
    for name,offset,size in ROWS:
        s=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(s)
        assert s['address']==offset+0x101f6a74 and s['flags']==2 and len(body)==size and body==stock[offset:offset+size] and not elf.relocations(s['index'])
        rows.append({'name':name,'package_offset':offset,'bytes':size,'sha256':sha(body),'text':body.decode('ascii')})
    return {'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(p.read_bytes()),'stock_sha256':IMAGE_SHA,'rows':rows,'source_admitted':False,'limits':['Readable strings match stock at exact XIP addresses. Adjacent1byte/3byte zeros are not claimed. Original application source lineage and runtime references not established by text match.','Ownership checks and admission pending; no application behavior reconstructed by this data change.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-application-labels-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Application text bytes:',sum(x['bytes'] for x in r['rows']))
