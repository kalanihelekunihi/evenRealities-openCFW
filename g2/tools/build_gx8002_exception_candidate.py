# SPDX-License-Identifier: MIT
"""Compile authenticated Apache-licensed exception sources on macOS."""
import json,subprocess
from analyze_gx8002_exception_provenance import analyze,ROOT,IMAGE,sha,Elf32,SDK_COMMIT,authenticated_blob

def build():
    evidence=analyze();sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='arch/soc/grus/include/csi_config.h';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();header=authenticated_blob(sdk/rel,blob)
    out=ROOT/'build/gx8002-exception';out.mkdir(parents=True,exist_ok=True);pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    (out/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
    for name,source in (('handler','trap_c.c'),('entry','vectors.S')):
        subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-MMD','-MF',str(out/(name+'.d')),'-I'+str(out),'-I'+str(sdk/'arch/soc/grus/include'),'-I'+str(sdk/'include/utility/libc'),'-I'+str(sdk/'include'),'-c',str(sdk/'arch/soc/grus'/source),'-o',str(out/(name+'.o'))],check=True)
    dependencies={}
    for name in ('handler','entry'):
        dependency_text=(out/(name+'.d')).read_text().replace('\\\n',' ')
        for token in dependency_text.split(':',1)[1].split():
            dep=__import__('pathlib').Path(token)
            if dep==out/'autoconf.h':
                dependencies['generated/autoconf.h']={'sha256':sha(dep.read_bytes())};continue
            rel=dep.relative_to(sdk).as_posix()
            dep_blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
            dependencies[rel]={'blob':dep_blob,'sha256':sha(authenticated_blob(dep,dep_blob))}
    script='SECTIONS { .handler 0x100235f0 : { *handler.o(.text*) } .entry 0x100235fc : { *entry.o(.text*) } .stack 0x20027010 (NOLOAD) : { *entry.o(.bss*) } }\n'
    (out/'exception.ld').write_text(script);path=out/'exception.elf'
    subprocess.run([pre+'ld','-T',str(out/'exception.ld'),str(out/'handler.o'),str(out/'entry.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'exceptions');stock=IMAGE.read_bytes();sections=[]
    for name,offset,envelope in (('.handler',0x15604,12),('.entry',0x15610,80)):
        s=next(s for s in elf.sections if s['name']==name);data=elf.contents(s)
        assert len(data)<=envelope and not elf.relocations(s['index'])
        sections.append({'name':name,'address':s['address'],'bytes':len(data),'sha256':sha(data),'stock_offset':offset,'envelope':envelope,'byte_exact':data==stock[offset:offset+len(data)]})
    s=next(s for s in elf.sections if s['name']=='.stack');assert s['type']==8 and s['address']==0x20027010 and s['size']==772
    symbols={s['name']:s['value'] for s in elf.symbols() if s['name']};assert symbols['g_top_trapstack']==symbols['g_trap_sp']==0x20027310
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    (out/'exception.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'provenance':evidence,'dependencies':dependencies,'header_blob':blob,'header_sha256':sha(header),'sections':sections,'stack_address':s['address'],'stack_bytes':s['size'],'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Unmodified pinned Apache2.0 SDK C/assembly compiled and linked; stack source allocated at inferred deployed location.','Full instruction equivalence, stack ownership and exception entry execution remain to qualify. No registry admission.']}
if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-exception-candidate.json').write_text(json.dumps(r,indent=2)+'\n');print(r['sections'])
