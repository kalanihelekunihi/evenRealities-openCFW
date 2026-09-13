# SPDX-License-Identifier: MIT
"""Build source-authored binary32 sign helpers at stock entry addresses."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,sha,Elf32
from verify_gx8002_analog_source import FLAGS

def build():
    out=ROOT/'build/gx8002-float-sign';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_float_sign.c';obj=out/'sign.o';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc',*FLAGS,'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
    rows=[('copy',0x49be4,32,'open_cfw_gx8002_copy_float_sign'),('absolute',0x49c04,16,'open_cfw_gx8002_float_absolute')]
    script=''
    for name,offset,limit,symbol in rows:
        address=offset-0x3b940+0x10003000
        script+=f'SECTIONS {{ .{name} {address:#x} : {{ *(.text.{symbol}) }} }}\nASSERT(SIZEOF(.{name}) <= {limit}, "{name} overflow")\n'
    ld=out/'sign.ld';ld.write_text(script);path=out/'sign.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    e=Elf32(path.read_bytes(),'sign');assert not any(s['name'] and s['section']==0 for s in e.symbols());assert not any(e.relocations(s['index']) for s in e.sections)
    result={'elf_sha256':sha(path.read_bytes()),'source_sha256':sha(source.read_bytes()),'command':command,'sections':[{'name':name,'offset':offset,'bytes':next(s['size'] for s in e.sections if s['name']=='.'+name)} for name,offset,limit,symbol in rows],'source_admitted':False,'limits':['Complete semantic C sign helpers; decoded comparison and firmware integration pending.']}
    (ROOT/'docs/research/gx8002-float-sign-build.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['sections'])
