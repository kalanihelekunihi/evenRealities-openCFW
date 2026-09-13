# SPDX-License-Identifier: MIT
"""Link the complete pinned upstream sqrt function at its stock SRAM entry."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_powf_source_closure import build as closure_build

def build():
    closure=closure_build()
    out=ROOT/'build/gx8002-sqrtf-placed';out.mkdir(exist_ok=True)
    obj=ROOT/'build/gx8002-powf-source-closure/ef_sqrt.c.o'
    entry=0x4950c-0x3b940+0x10003000
    ld=out/'sqrt.ld';ld.write_text('SECTIONS { .sqrt 0x%x : { *(.text*) } }\nASSERT(SIZEOF(.sqrt) <= 216, "sqrt exceeds stock region")\n'%entry)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');path=out/'sqrt.elf'
    command=[pre+'ld','-T',str(ld),str(obj),'-o',str(path)];subprocess.run(command,check=True)
    data=path.read_bytes();elf=Elf32(data,'sqrt')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(allocated)==1 and allocated[0]['name']=='.sqrt'
    section=allocated[0];assert section['address']==entry
    assert next(s['value'] for s in elf.symbols() if s['name']=='__ieee754_sqrtf')==entry
    result={'closure':closure,'command':command,'elf_sha256':sha(data),'entry':entry,'package_start':0x4950c,'package_end':0x495e4,'size':section['size'],'section_sha256':sha(elf.contents(section)),'source_admitted':False,'limits':['Complete upstream C function placed at original entry. Unused stock tail remains unclassified; firmware integration, special-value paths and hardware qualification pending.']}
    (out/'sqrt.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    (ROOT/'docs/research/gx8002-sqrtf-placed.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print({k:r[k] for k in ('elf_sha256','entry','size')})
