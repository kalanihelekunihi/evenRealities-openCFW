# SPDX-License-Identifier: MIT
"""Build complete math wrappers and compare their instruction bytes with stock."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_analog_source import FLAGS
from analyze_gx8002_double_wrapper_references import analyze

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-math-wrappers';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_math_wrappers.c';obj=out/'wrappers.o'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc',*FLAGS,'-fno-optimize-sibling-calls','-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
    rows=[('powf',0x489e4,0x489fc),('logf',0x489ec,0x490a8),('expf',0x489f4,0x49300)];delta=0x10003000-0x3b940
    script=''
    for name,start,target in rows:
        script+='__ieee754_%s = 0x%x;\nSECTIONS { .%s 0x%x : { *(.text.open_cfw_gx8002_%s) } }\nASSERT(SIZEOF(.%s)==8,"wrapper size changed")\n'%(name,target+delta,name,start+delta,name,name)
    ld=out/'wrappers.ld';ld.write_text(script);path=out/'wrappers.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'wrappers');assert not any(s['name'] and s['section']==0 for s in elf.symbols());assert not any(elf.relocations(s['index']) for s in elf.sections)
    sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==3
    evidence=[]
    for name,start,target in rows:
        sec=next(s for s in sections if s['name']=='.'+name);body=elf.contents(sec)
        assert sec['address']==start+delta and body==stock[start:start+8]
        evidence.append({'name':name,'offset':start,'target':target,'bytes':len(body),'sha256':sha(body),'references':analyze(start,start+8)})
    result={'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'command':command,'sections':evidence,'source_admitted':False,'limits':['Whole C wrappers byte-identical to stock at original placement. Linker names bind to reconstructed targets, whose integration identity must be checked by composer. Hardware/full application not qualified.']}
    (ROOT/'docs/research/gx8002-math-wrappers.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['elf_sha256'])
