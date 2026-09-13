# SPDX-License-Identifier: MIT
"""Build scalar recovered forward/inverse radix-4 candidates on macOS."""
import json,subprocess
from build_gx8002_backup_platform_config import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS

def build(extra_flags=('-fno-caller-saves',)):
    out=ROOT/'build/gx8002-backup-radix4';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4.c';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');rows=[]
    for inverse,offset,helper in ((0,0x47d3c,0),(1,0x47f50,0)):
        name='inverse' if inverse else 'forward';symbol='open_cfw_gx8002_backup_radix4'+('_inverse' if inverse else '')
        dependency='backup_radix4'+('_inverse' if inverse else '')
        flags=['-Os',*FLAGS[1:],*extra_flags,'-DINVERSE='+str(inverse)]
        subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/(name+'.o'))],check=True)
        address=offset-0x3b940+0x10003000
        (out/(name+'.ld')).write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text*) }} }}\n')
        path=out/(name+'.elf');subprocess.run([pre+'ld','-T',str(out/(name+'.ld')),str(out/(name+'.o')),'-o',str(path)],check=True)
        elf=Elf32(path.read_bytes(),name);section=next(s for s in elf.sections if s['name']=='.text');body=elf.contents(section)
        assert not any(elf.relocations(s['index']) for s in elf.sections)
        assert not any(s['name'] and s['section']==0 for s in elf.symbols())
        (out/(name+'.disassembly.txt')).write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
        rows.append({'variant':name,'compiled_bytes':len(body),'envelope_bytes':532,'fits':len(body)<=532,'sha256':sha(body),'flags':flags})
    report={'source_sha256':sha(source.read_bytes()),'variants':rows,'source_admitted':False,'limits':['Scalar three-stage candidate only; decoded stock comparison pending. No retained arithmetic dependencies linked.']}
    (ROOT/'docs/research/gx8002-backup-radix4-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print([(x['variant'],x['compiled_bytes']) for x in build()['variants']])
