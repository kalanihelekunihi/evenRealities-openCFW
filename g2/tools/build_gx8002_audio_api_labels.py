# SPDX-License-Identifier: MIT
"""Compile readable audio diagnostic strings; authenticate SDK provenance."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32
ROWS=(('config',0x14020,48),('drain',0x1407f,25),('controls',0x140ac,64),('power',0x14129,93))
def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/audio_out/audio_out.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();up=Elf32(authenticated_blob(sdk/rel,blob),rel)
    upstream=[(s,up.contents(s)) for s in up.sections if s['type']!=8 and not s['flags']&4]
    out=ROOT/'build/gx8002-audio-api-labels';out.mkdir(parents=True,exist_ok=True);source=ROOT/'components/shared/gx8002/runtime_gx8002_audio_api_labels.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-c',str(source),'-o',str(out/'labels.o')],check=True)
    (out/'labels.ld').write_text('SECTIONS {\n'+''.join(f'.{name} {offset+0x101f6a74:#x} : {{ *(.rodata.labels_{name}) }}\n' for name,offset,size in ROWS)+'}\n');path=out/'labels.elf';subprocess.run([pre+'ld','-T',str(out/'labels.ld'),str(out/'labels.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'labels');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;rows=[]
    for name,offset,size in ROWS:
        section=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(section);assert len(body)==size and body==stock[offset:offset+size] and not elf.relocations(section['index'])
        matches=[]
        for label in body.split(b'\0'):
            if not label:continue
            found=[(s['name'],data.find(label+b'\0')) for s,data in upstream if label+b'\0' in data];assert found,label
            matches.append({'label':label.decode('ascii'),'upstream_occurrences':[[a,b] for a,b in found]})
        rows.append({'name':name,'package_offset':offset,'bytes':size,'sha256':sha(body),'labels':matches})
    return {'sdk_commit':SDK_COMMIT,'upstream_blob':blob,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'rows':rows,'source_admitted':False,'limits':['Readable source literals compile byte-exact; each name is present in authenticated SDK object data. Reference/ownership qualification and admission pending.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-audio-api-labels-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio diagnostic source bytes:',sum(x['bytes'] for x in r['rows']))
