# SPDX-License-Identifier: MIT
"""Authenticate startup clearing and inspect audio callback storage allocations."""
import json,re,subprocess
from build_gx8002_audio_record_candidate import ROOT,sha,Elf32
from compare_gx8002_clear_bss import execute,START,END
from verify_gx8002_memcpy_source import decode

def verify():
    report=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());row=report['functions'][0]
    path=ROOT/'build/gx8002-clear-bss/clear.elf';elf=Elf32(path.read_bytes(),'clear');section=next(s for s in elf.sections if s['name']==row['section_name'])
    assert sha(elf.contents(section))==row['compiled_sha256']
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    trace=execute(code,section['address'],91);assert trace==[[a,0] for a in range(START,END,4)]
    ranges={'control':(0x2002ecb0,20),'handler':(0x2002dfa0,4),'invalid_vad':(0x2002dfa8,4)}
    candidate_path=ROOT/'build/gx8002-board/audio-record.elf'
    candidate=Elf32(candidate_path.read_bytes(),'audio state')
    for name,(address,size) in ranges.items():
        allocation=next(s for s in candidate.sections if s['name']=='.audio_record_'+name)
        assert (allocation['address'],allocation['size'],allocation['type'],allocation['flags'])==(address,size,8,3)
    cleared={a:v for a,v in trace}
    for address,size in ranges.values():assert all(cleared[a]==0 for a in range(address,address+size,4))
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text();overlaps=[];missing=[];checked=0
    for kind,artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)",registry):
        if kind=='audio-record':continue
        p=ROOT/'build/gx8002-source-candidate'/kind/artifact
        if not p.exists():missing.append(kind);continue
        image=Elf32(p.read_bytes(),str(p));checked+=1
        for s in image.sections:
            if not s['flags']&2 or not s['size'] or not s['address']:continue
            for name,(a,n) in ranges.items():
                if s['address']<a+n and a<s['address']+s['size']:overlaps.append({'state':name,'kind':kind,'section':s['name'],'address':s['address'],'bytes':s['size']})
    return {'candidate_elf_sha256':sha(candidate_path.read_bytes()),'clear_elf_sha256':sha(path.read_bytes()),'decoded_clear_words':len(trace),'state':{k:{'address':a,'bytes':n,'startup_value':0} for k,(a,n) in ranges.items()},'checked_artifacts':checked,'missing_artifacts':missing,'overlapping_allocations':overlaps,'source_admitted':False,'limits':['Decoded source startup clears all state words. Allocation scan covers only materialized fixed-address registered sections; retained indirect writers and runtime concurrency remain unqualified. All three state ranges have exact source NOBITS allocations in the callback candidate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-record-state.json').write_text(json.dumps(r,indent=2)+'\n');print({k:r[k] for k in ('decoded_clear_words','checked_artifacts','missing_artifacts','overlapping_allocations')})
