# SPDX-License-Identifier: MIT
"""Fresh pinned libgcc quotient/remainder objects for backup-image recovery."""
import json,shlex,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32

def build():
    upstream=ROOT/'build/upstream-csky-toolchain-build/gcc';pin='1e9b70447a8417f5c692370de4533e43d754e8fa'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=upstream,text=True).strip()==pin
    source=upstream/'libgcc/libgcc2.c'
    assert source.read_bytes()==subprocess.check_output(['git','show',pin+':libgcc/libgcc2.c'],cwd=upstream)
    out=ROOT/'build/gx8002-backup-unsigned-division';out.mkdir(exist_ok=True)
    lib=ROOT/'build/csky-macos/gcc-build/csky-unknown-elf/libgcc';names=['_udivdi3.o','_umoddi3.o','_clz.o']
    log=subprocess.check_output(['make','-W',str(source),*names],cwd=lib,text=True)
    assert all(' -o '+name+' ' in log for name in names);(out/'rebuild.log').write_text(log)
    records=[];script='';objects=[]
    for name,section,offset,limit in [('_udivdi3.o','quotient',0x49ddc,820),('_umoddi3.o','remainder',0x4a110,804),('_clz.o','bit_lengths',0x4df14,256)]:
        obj=out/name
        command=shlex.split(next(l for l in log.replace(chr(92)+chr(10),' ').splitlines() if ' -o '+name+' ' in l))
        command+=['-Os','-mcpu=ck803ef','-mno-high-registers','-fno-asynchronous-unwind-tables','-fno-unwind-tables','-fno-exceptions','-fno-non-call-exceptions']
        command[command.index('-o')+1]=str(obj);subprocess.run(command,cwd=lib,check=True)
        objects.append(str(obj));e=Elf32(obj.read_bytes(),name)
        allocated=[s for s in e.sections if s['flags']&2 and s['size']]
        assert len(allocated)==1;sec=allocated[0];address=offset-0x3b940+0x10003000
        script+=f'SECTIONS {{ .{section} {address:#x} : {{ {obj}({sec["name"]}) }} }}\nASSERT(SIZEOF(.{section}) <= {limit}, "{section} overflow")\n'
        records.append({'section':section,'offset':offset,'bytes':sec['size'],'limit':limit,'command':command,'object_sha256':sha(obj.read_bytes())})
    ld=out/'division.ld';ld.write_text(script);path=out/'division.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(ld),*objects,'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'division');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    table=e.contents(next(s for s in e.sections if s['name']=='.bit_lengths'));assert table==bytes(i.bit_length() for i in range(256))
    (out/'division.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'upstream_commit':pin,'source_sha256':sha(source.read_bytes()),'elf_sha256':sha(path.read_bytes()),'objects':records,'source_admitted':False,'limits':['Candidate entry assignments require stock execution validation. Not integrated; table identity is mathematical, not extracted firmware data.']}
    (ROOT/'docs/research/gx8002-backup-unsigned-division.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['objects'])
