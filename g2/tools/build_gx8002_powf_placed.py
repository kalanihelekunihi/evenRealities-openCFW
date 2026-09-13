# SPDX-License-Identifier: MIT
"""Place complete upstream power and its complete source dependencies at stock entries."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from build_gx8002_powf_source_closure import build as closure_build

def build():
    closure=closure_build()
    out=ROOT/'build/gx8002-powf-placed';out.mkdir(exist_ok=True)
    layout=[('power',0x489fc,0x490a8,'__ieee754_powf'),('sqrt',0x4950c,0x495e4,'__ieee754_sqrtf'),('scale',0x49ad4,0x49bd8,'open_cfw_gx8002_scale_float'),('sign',0x49be4,0x49c04,'open_cfw_gx8002_copy_float_sign'),('absolute',0x49c04,0x49c14,'open_cfw_gx8002_float_absolute')]
    delta=0x10003000-0x3b940
    ld=out/'power.ld'
    ld.write_text('SECTIONS {\n'+''.join(' .%s 0x%x : { *(.text.%s) }\n'%(name,start+delta,symbol) for name,start,end,symbol in layout)+'}\n'+''.join('ASSERT(SIZEOF(.%s) <= %d, "%s exceeds original envelope")\n'%(name,end-start,name) for name,start,end,symbol in layout))
    objects=[ROOT/'build/gx8002-powf-source-closure'/n for n in ('ef_pow.c.o','ef_sqrt.c.o')]+[ROOT/'build/gx8002-scalbnf-corrected'/('source%d.o'%i) for i in (0,1)]
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');path=out/'power.elf'
    command=[pre+'ld','-T',str(ld),*[str(p) for p in objects],'-o',str(path)];subprocess.run(command,check=True)
    data=path.read_bytes();elf=Elf32(data,'power')
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert {s['name'] for s in allocated}=={'.'+row[0] for row in layout}
    sections=[]
    for name,start,end,symbol in layout:
        sec=next(s for s in allocated if s['name']=='.'+name)
        assert sec['address']==start+delta
        assert next(s['value'] for s in elf.symbols() if s['name']==symbol)==sec['address']
        sections.append({'section':sec['name'],'package_start':start,'package_end':end,'size':sec['size'],'sha256':sha(elf.contents(sec))})
    result={'closure':closure,'command':command,'elf_sha256':sha(data),'sections':sections,'source_admitted':False,'limits':['All allocated bytes come from complete source functions. Power behavior and reference closure remain unqualified; no integration or hardware qualification implied.']}
    (out/'power.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    (ROOT/'docs/research/gx8002-powf-placed.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['elf_sha256'],r['sections'])
