# SPDX-License-Identifier: MIT
"""Place freshly rebuilt GCC binary64 unpack at the observed stock entry."""
import json,subprocess
from build_gx8002_exp_source_closure import build as closure
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32

def build():
    evidence=closure();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    obj=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc/_unpack_df.o'
    row=next(r for r in evidence['rebuilt_objects'] if r['name']==obj.name);assert sha(obj.read_bytes())==row['sha256']
    out=ROOT/'build/gx8002-backup-double-unpack';out.mkdir(exist_ok=True)
    start,end=0x4afd4,0x4b0b8;address=start-0x3b940+0x10003000
    script=out/'unpack.ld';script.write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text*) }} }}\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');path=out/'unpack.elf'
    subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'unpack');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['address']==address
    assert next(s['value'] for s in elf.symbols() if s['name']=='__unpack_d')==address
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    body=elf.contents(sections[0]);assert len(body)<=end-start
    (out/'unpack.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'gcc_revision':evidence['gcc_revision'],'source_dependencies':evidence['source_dependencies'],'object_sha256':sha(obj.read_bytes()),'elf_sha256':sha(path.read_bytes()),
            'entry_address':address,'package_offset':start,'compiled_bytes':len(body),'stock_bytes':end-start,'unreplaced_tail_bytes':end-start-len(body),'compiled_sha256':sha(body),'stock_sha256':IMAGE_SHA,
            'source_admitted':False,'hardware_qualified':False,'limits':['Original-entry standalone source candidate. Tail remains stock, not declared unreachable or reusable. Caller census, relocated execution and loader integration pending.']}
    (ROOT/'docs/research/gx8002-backup-double-unpack-candidate.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['compiled_bytes'],r['stock_bytes'])
