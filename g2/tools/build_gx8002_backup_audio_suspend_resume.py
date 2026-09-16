# SPDX-License-Identifier: MIT
"""Build source audio-input suspend/resume wrappers on macOS."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
ROWS=(('suspend',0x43054,28),('resume',0x43070,20))
def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-audio-suspend-resume';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_audio_suspend_resume.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-c',str(source),'-o',str(out/'wrappers.o')],check=True)
    script='SECTIONS {\n'+''.join(f'.audio_{name} {offset-0x38940+0x10000000:#x} : {{ *(.text.open_cfw_gx8002_backup_audio_{name}) }}\n' for name,offset,size in ROWS)+'}\nopen_cfw_gx8002_audio_interrupt_enable = 0x10005cbc;\n'
    (out/'wrappers.ld').write_text(script);path=out/'wrappers.elf'
    subprocess.run([pre+'ld','-T',str(out/'wrappers.ld'),str(out/'wrappers.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrappers');assert not any(elf.relocations(s['index']) for s in elf.sections) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    rows=[]
    for name,offset,size in ROWS:
        sec=next(s for s in elf.sections if s['name']=='.audio_'+name);body=elf.contents(sec);assert len(body)<=size
        rows.append({'name':name,'bytes':len(body),'envelope_bytes':size,'exact_stock':body==stock[offset:offset+size]})
    (out/'wrappers.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'source_sha256':sha(source.read_bytes()),'functions':rows,'source_admitted':False,'limits':['Interrupt helper bound separately; hardware qualification remains pending.']}
    (ROOT/'docs/research/gx8002-backup-audio-suspend-resume.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
