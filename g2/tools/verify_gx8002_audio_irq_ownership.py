# SPDX-License-Identifier: MIT
"""Source-owned audio IRQ runtime startup and overlap qualification."""
import json,re,subprocess
from build_gx8002_audio_irq_candidate import build,ROOT,sha,Elf32
from compare_gx8002_clear_bss import execute,START,END
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();candidate=Elf32((ROOT/'build/gx8002-board/audio-irq.elf').read_bytes(),'TWS audio');state=next(s for s in candidate.sections if s['name']=='.state')
    assert (state['address'],state['size'],state['type'],state['flags'])==(0x20027330,28,8,3)
    clear_path=ROOT/'build/gx8002-clear-bss/clear.elf';clear=Elf32(clear_path.read_bytes(),'clear');report=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());row=report['functions'][0];section=next(s for s in clear.sections if s['name']==row['section_name']);assert sha(clear.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');trace=execute(decode(subprocess.check_output([pre,'-d',str(clear_path)],text=True)),section['address'],91);assert trace==[[a,0] for a in range(START,END,4)];assert all(dict(trace)[a]==0 for a in range(0x20027330,0x2002734c,4))
    checked=0
    for kind,artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)",(ROOT/'tools/build_gx8002_source_candidate.py').read_text()):
        if kind=='audio-irq':continue
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact;assert path.exists(),kind;elf=Elf32(path.read_bytes(),str(path));checked+=1
        for s in elf.sections:
            if s['flags']&2 and s['size'] and s['address']:assert not (s['address']<0x2002734c and 0x20027330<s['address']+s['size']),(kind,s['name'])
    return {'candidate':evidence,'checked_artifacts':checked,'clear_elf_sha256':sha(clear_path.read_bytes()),'source_admitted':False,'limits':['Exact C BSS state and decoded startup zero checked. Fixed-section audit excludes retained indirect writes and physical concurrency.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-irq-ownership.json').write_text(json.dumps(r,indent=2)+'\n');print(r['checked_artifacts'])
