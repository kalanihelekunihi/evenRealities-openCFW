# SPDX-License-Identifier: MIT
"""Build complete pinned upstream fault handler and vector-entry assembly."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS
from analyze_gx8002_upstream_objects import SDK_COMMIT,authenticated_blob


def build():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    out=ROOT/'build/gx8002-backup-upstream-trap';out.mkdir(exist_ok=True)
    rows=[]
    for name in ('trap_c.c','vectors.S'):
        rel='arch/soc/grus/'+name
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
        data=authenticated_blob(sdk/rel,blob);(out/name).write_bytes(data)
        rows.append({'path':rel,'git_blob':blob,'sha256':sha(data)})
    # No enabled source statement uses stdio/stdlib/config declarations.
    for name in ('stdio.h','stdlib.h','csi_config.h'):
        (out/name).write_text('/* No declarations needed by the enabled upstream fault-handler path. */\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    commands=[]
    for name in ('trap_c.c','vectors.S'):
        cmd=[pre+'gcc',*FLAGS,'-Os','-Wno-error=unused-parameter','-I',str(out),'-c',str(out/name),'-o',str(out/(name+'.o'))]
        subprocess.run(cmd,check=True);commands.append(cmd)
    ld=out/'trap.ld';ld.write_text('SECTIONS { .trap_c 0x100031f0 : { *(.text.trap_c) } .vectors 0x100031fc : { *(.text) } .state 0x20017090 (NOLOAD) : { *(.bss) } }\n')
    path=out/'trap.elf';subprocess.run([pre+'ld','-T',str(ld),str(out/'trap_c.c.o'),str(out/'vectors.S.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'upstream trap');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sections=[]
    for name,offset,limit in (('.trap_c',0x3bb30,12),('.vectors',0x3bb3c,80)):
        s=next(s for s in elf.sections if s['name']==name);body=elf.contents(s)
        assert len(body)<=limit and body==stock[offset:offset+len(body)]
        sections.append({'name':name,'offset':offset,'bytes':len(body),'stock_envelope_bytes':limit,'stock_identical':body==stock[offset:offset+len(body)],'sha256':sha(body)})
    symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    assert symbols['g_trapstackbase']==0x20017090 and symbols['g_top_trapstack']==symbols['g_trap_sp']==0x20017390
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'trap.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'sdk_commit':SDK_COMMIT,'upstream_sources':rows,'commands':commands,'compatibility_headers':'Empty stdio.h, stdlib.h and csi_config.h; none contributes declarations to enabled upstream code. stdint.h from toolchain.','elf_sha256':sha(path.read_bytes()),'sections':sections,'stock_sha256':IMAGE_SHA,'source_admitted':False,'limits':['Existing upstream fatal exception path only; not a substitute for missing application functionality.','Behavior, reference census and integration pending; no claim of exception recovery or hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-upstream-trap.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['sections'])
