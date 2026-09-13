# SPDX-License-Identifier: MIT
"""Fresh pinned GCC integer multiplication; original-entry placement using baseline instructions."""
import json,shlex,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    upstream=ROOT/'build/upstream-csky-toolchain-build/gcc'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip()=='1e9b70447a8417f5c692370de4533e43d754e8fa'
    source=upstream/'libgcc/libgcc2.c';lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc'
    out=ROOT/'build/gx8002-muldi-source-cluster';out.mkdir(exist_ok=True)
    log=subprocess.check_output(['make','-W',str(source),'_muldi3.o'],cwd=lib,text=True)
    assert ' -o _muldi3.o ' in log;(out/'rebuild.log').write_text(log)
    command=shlex.split(next(l for l in log.splitlines() if ' -o _muldi3.o ' in l))
    command+=['-mcpu=ck803ef','-mno-high-registers','-Os'];obj=out/'muldi.o';command[command.index('-o')+1]=str(obj)
    subprocess.run(command,cwd=lib,check=True)
    address=0x4ad64-0x3b940+0x10003000
    ld=out/'muldi.ld';ld.write_text(f'SECTIONS {{ .text {address:#x} : {{ {obj}(.text) }} }}\nASSERT(SIZEOF(.text) <= 76, "multiply overflow")\n')
    path=out/'muldi.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'muldi');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    size=next(s['size'] for s in e.sections if s['name']=='.text')
    result={'elf_sha256':sha(path.read_bytes()),'source_sha256':sha(source.read_bytes()),'command':command,'bytes':size,'entry_address':address,'package_offset':0x4ad64,'stock_envelope_bytes':76,'source_admitted':False,'limits':['Whole upstream source function at original entry. CK803EF code generation uses baseline integer instructions present in stock CK804 firmware; preserves hard-float ABI flags. Execution, integration and hardware require separate evidence.']}
    (ROOT/'docs/research/gx8002-muldi-source-cluster.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['bytes'])
