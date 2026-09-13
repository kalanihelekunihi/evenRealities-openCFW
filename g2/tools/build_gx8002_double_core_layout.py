# SPDX-License-Identifier: MIT
"""Place whole upstream source objects within pack/unpack/compare envelopes."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    probe=json.loads((ROOT/'docs/research/gx8002-pack-size-probe.json').read_text())
    chosen=probe['variants'][0];assert chosen['bytes']==418
    assert sha((ROOT/chosen['path']).read_bytes())==chosen['elf_sha256']
    unpack=json.loads((ROOT/'docs/research/gx8002-backup-double-unpack-candidate.json').read_text())
    compare=json.loads((ROOT/'docs/research/gx8002-backup-double-compare-candidate.json').read_text())
    out=ROOT/'build/gx8002-double-core-layout';out.mkdir(exist_ok=True)
    # Whole independently compiled function objects, not firmware ranges.
    rows=[('pack',ROOT/'build/gx8002-pack-size-probe/0-0.o',0x4ae44,338,'__pack_d'),
          ('right',ROOT/'build/gx8002-pack-size-probe/0-1.o',0x4af98,38,'__lshrdi3'),
          ('unpack',ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc/_unpack_df.o',0x4afd4,176,'__unpack_d'),
          ('left',ROOT/'build/gx8002-pack-size-probe/0-2.o',0x4b084,38,'__ashldi3'),
          ('compare',ROOT/'build/gx8002-backup-double-compare/compare.o',0x4b0b8,186,'__fpcmp_parts_d')]
    assert sha(rows[2][1].read_bytes())==unpack['object_sha256']
    assert sha(rows[4][1].read_bytes())==compare['object_sha256']
    # Bind probe objects by reproducing its previously authenticated complete link.
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    repro=out/'probe-reproduced.elf'
    subprocess.run([pre+'ld','-T',str(ROOT/'build/gx8002-backup-double-pack/pack.ld'),*[str(rows[i][1]) for i in (0,1,3)],'-o',str(repro)],check=True)
    expected=Elf32((ROOT/chosen['path']).read_bytes(),'probe');actual=Elf32(repro.read_bytes(),'reproduced')
    def allocated(e):return [(s['name'],s['address'],e.contents(s)) for s in e.sections if s['flags']&2 and s['size']]
    assert allocated(expected)==allocated(actual)
    script='SECTIONS {\n';inputs=[]
    for name,path,off,size,symbol in rows:
        copy=out/(name+'.o');copy.write_bytes(path.read_bytes());inputs.append(copy)
        addr=off-0x3b940+0x10003000
        script+=f'.{name} {addr:#x} : {{ {copy}(.text) }}\nASSERT(SIZEOF(.{name}) == {size}, "size drift")\n'
    script+='}\n';ld=out/'core.ld';ld.write_text(script);path=out/'core.elf'
    subprocess.run([pre+'ld','-T',str(ld),*[str(p) for p in inputs],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'layout');assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert len(allocated(elf))==5;sections=[]
    for name,obj,off,size,symbol in rows:
        sec=next(s for s in elf.sections if s['name']=='.'+name)
        assert next(s['value'] for s in elf.symbols() if s['name']==symbol)==sec['address']
        assert sec['size']==size
        sections.append({'name':name,'offset':off,'bytes':size,'symbol':symbol,'sha256':sha(elf.contents(sec))})
    from verify_gx8002_memcpy_source import decode
    code=decode(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    for pc,(op,args,width) in code.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bhz'):
            assert int(args.split(',')[-1].strip(),0) in code
    spans=sorted((r['offset'],r['offset']+r['bytes']) for r in sections)
    assert all(a[1]<=b[0] for a,b in zip(spans,spans[1:]))
    result={'elf_sha256':sha(path.read_bytes()),'sections':sections,'source_bytes':sum(r['bytes'] for r in sections),'source_admitted':False,'hardware_qualified':False,
            'limits':['Whole source objects preserve original pack/unpack/comparator entries. Left shift uses 38 bytes of old unpack tail; reuse not yet admitted.',
                      'Pack semantics, relocated calls, complete composition and loader qualification pending. No firmware image changed.']}
    (ROOT/'docs/research/gx8002-double-core-layout.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build())
