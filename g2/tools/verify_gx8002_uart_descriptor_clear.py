# SPDX-License-Identifier: MIT
"""Ensure decoded startup BSS clearing preserves initialized UART descriptors."""
import json,subprocess
from build_gx8002_uart_descriptor_candidate import build,ROOT,sha,Elf32
from compare_gx8002_clear_bss import execute,START,END
from verify_gx8002_memcpy_source import decode

def verify():
    evidence=build();path=ROOT/'build/gx8002-clear-bss/clear.elf';elf=Elf32(path.read_bytes(),'clear');report=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());row=report['functions'][0];section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');trace=execute(decode(subprocess.check_output([pre,'-d',str(path)],text=True)),section['address'],91);assert trace==[[a,0] for a in range(START,END,4)]
    descriptor=Elf32((ROOT/'build/gx8002-board/uart-descriptor.elf').read_bytes(),'defaults');s=next(s for s in descriptor.sections if s['name']=='.descriptors');body=descriptor.contents(s)
    before={s['address']+i:int.from_bytes(body[i:i+4],'little') for i in range(0,len(body),4)};memory=before.copy()
    for a,v in trace:memory[a]=v
    assert all(memory[a]==v for a,v in before.items()) and not any(s['address']<=a<s['address']+len(body) for a,v in trace)
    return {'candidate':evidence,'clear_elf_sha256':sha(path.read_bytes()),'clear_writes':len(trace),'preserved_descriptor_words':len(before),'source_admitted':False,'limits':['Authenticated decoded BSS clearing does not touch initialized UART descriptor interval. Test begins with source defaults resident in RAM; it does not prove loader transfer or prior initialization.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-descriptor-clear.json').write_text(json.dumps(r,indent=2)+'\n');print(r['preserved_descriptor_words'])
