# SPDX-License-Identifier: MIT
"""Compare placed shared-polynomial cosine with unchanged upstream on special inputs."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_double_pack_target import execute


def verify():
    models=[];hashes={}
    for stem,filename,entry in [('gx8002-trig-source-closure','trig.elf',0x10018200),('gx8002-cosine-placed','cosine.elf',0x499ac+0x10003000-0x3b940)]:
        path=ROOT/'build'/stem/filename;report=json.loads((ROOT/'docs/research'/(stem+'.json')).read_text())
        assert sha(path.read_bytes())==report['elf_sha256'];hashes[stem]=report['elf_sha256']
        elf=Elf32(path.read_bytes(),stem)
        code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
        memory={s['address']+i:b for s in elf.sections if s['flags']&2 and s['size'] and s['type']!=8 for i,b in enumerate(elf.contents(s))}
        models.append((code,entry,memory))
    payloads=[0,1,2,1<<51,(1<<51)|123,(1<<52)-1]+[1<<i for i in range(52)]
    specials=[(sign<<63)|0x7ff0000000000000|p for sign in (0,1) for p in payloads]
    others=[0,1<<63,1,0x8000000000000001,0x3fe0000000000000,0xbfe0000000000000,0x7ff8000000000456]
    pairs=[(x,y) for x in specials for y in others]+[(x,y) for x in others for y in specials]
    differences=[];count=0
    for x,y in pairs:
        for iy in (0,):
            values=[]
            for code,entry,memory in models:
                memory.update({0x8000+i:b for i,b in enumerate(iy.to_bytes(4,'little'))})
                values.append(execute(code,entry,bytes(20),arguments=[x&0xffffffff,x>>32,y&0xffffffff,y>>32],readonly=memory,return_pair=True,max_steps=100000))
            if values[0]!=values[1]:differences.append({'x':hex(x),'y':hex(y),'iy':iy,'upstream':hex(values[0]),'placed':hex(values[1])})
            count+=1
    result={'source_elf_hashes':hashes,'cases':count,'differences':differences,'source_admitted':False,'limits':['Decoded upstream versus placed source comparison including arithmetic and ABI checks. Nonfinite kernel inputs are outside the normal reduced-angle contract. Does not qualify stock equivalence, exception flags, universal payload behavior or hardware.']}
    (ROOT/'docs/research/gx8002-cosine-special.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=verify();print(r['cases'],len(r['differences']))
