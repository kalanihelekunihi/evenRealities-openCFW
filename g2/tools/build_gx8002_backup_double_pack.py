# SPDX-License-Identifier: MIT
"""Size-optimized upstream binary64 packer at its original entry."""
import json,shlex,subprocess
from build_gx8002_exp_source_closure import build as closure
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32

def build():
    evidence=closure();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    log=ROOT/'build/gx8002-exp-source-closure/rebuild.log'
    lines=[line for line in log.read_text().splitlines() if ' -o _pack_df.o ' in line];assert len(lines)==1
    command=shlex.split(lines[0]);out=ROOT/'build/gx8002-backup-double-pack';out.mkdir(exist_ok=True)
    obj=out/'pack.o'
    for flag,target in [('-o',obj),('-MT',obj),('-MF',out/'pack.dep')]:command[command.index(flag)+1]=str(target)
    command=['-Os' if arg=='-O2' else arg for arg in command]
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    subprocess.run(command,cwd=lib,check=True)
    helper_names=['_lshrdi3.o','_ashldi3.o']
    run=subprocess.run(['make','-W',str(ROOT/'build/upstream-csky-toolchain-build/gcc/libgcc/libgcc2.c'),*helper_names],cwd=lib,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (out/'shift-rebuild.log').write_text(run.stdout);assert run.returncode==0,run.stdout
    dependencies=dict(evidence['source_dependencies'])
    for name in helper_names:
        assert '-o '+name in run.stdout
        dep=(lib/name.replace('.o','.dep')).read_text().replace('\\\n',' ')
        for entry in shlex.split(dep.splitlines()[0].split(':',1)[1]):
            item=(lib/entry).resolve();assert item.is_file()
            dependencies[str(item.relative_to(ROOT))]=sha(item.read_bytes())
    start,end=0x4ae44,0x4afd4;address=start-0x3b940+0x10003000
    script=out/'pack.ld';script.write_text(f'SECTIONS {{ .text {address:#x} : {{ *(.text*) }} }}\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');path=out/'pack.elf'
    subprocess.run([pre+'ld','-T',str(script),str(obj),*[str(lib/n) for n in helper_names],'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'pack');sections=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert len(sections)==1 and sections[0]['address']==address
    assert next(s['value'] for s in elf.symbols() if s['name']=='__pack_d')==address
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    body=elf.contents(sections[0])
    (out/'pack.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'gcc_revision':evidence['gcc_revision'],'source_dependencies':dependencies,'shift_objects':{n:sha((lib/n).read_bytes()) for n in helper_names},'compile_command':command,'object_sha256':sha(obj.read_bytes()),'elf_sha256':sha(path.read_bytes()),
            'entry_address':address,'package_offset':start,'compiled_bytes':len(body),'stock_bytes':end-start,'fits':len(body)<=end-start,'compiled_sha256':sha(body),'stock_sha256':IMAGE_SHA,'source_admitted':False,'limits':['Original-entry source probe. Size optimization changes code; execution and caller/loader qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-double-pack-candidate.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['compiled_bytes'],r['stock_bytes'],r['fits'])
