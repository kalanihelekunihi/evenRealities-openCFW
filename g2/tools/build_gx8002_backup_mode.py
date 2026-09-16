# SPDX-License-Identifier: MIT
"""Build upstream backup mode initialization/tick and source-owned mode state."""
import json,subprocess
from build_gx8002_backup_main import build as main_build,ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    evidence=main_build();out=ROOT/'build/gx8002-backup-mode';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/lvp_mode.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip()
    raw=authenticated_blob(sdk/rel,blob);source=raw.replace(b'#include <types.h>\n',b'').replace(b'#include <stdio.h>\n',b'')
    source=source.replace(b'static const LVP_MODE_INFO *s_lvp_mode_list[]', b'static const LVP_MODE_INFO *const s_lvp_mode_list[]')
    (out/'mode.c').write_bytes(source)
    (out/'lvp_mode.h').write_bytes((ROOT/'build/gx8002-backup-main/lvp_mode.h').read_bytes())
    (out/'autoconf.h').write_text('#define CONFIG_LVP_HAS_DENOISE_MODE 1\n')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffunction-sections','-I',str(out),'-c',str(out/'mode.c'),'-o',str(out/'mode.o')],check=True)
    (out/'mode.ld').write_text('''SECTIONS {
.init 0x1000b748 : { *(.text.LvpInitMode) }
.tick 0x1000b7a0 : { *(.text.LvpModeTick) }
.list 0x10013664 : { *(.rodata) }
.state 0x2002d2b4 (NOLOAD) : { *(.bss) }
/DISCARD/ : { *(.text*) }
}
lvp_idle_mode_info = 0x1001366c;
lvp_denoise_mode_info = 0x100136b0;
''')
    path=out/'mode.elf';subprocess.run([pre+'ld','-T',str(out/'mode.ld'),str(out/'mode.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'mode');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for name,offset,limit in (('.init',0x44088,88),('.tick',0x440e0,32),('.list',0x4bfa4,8)):
        section=next(s for s in elf.sections if s['name']==name);body=elf.contents(section)
        rows.append({'name':name,'bytes':len(body),'envelope_bytes':limit,'fits':len(body)<=limit,'exact_stock_prefix':body==stock[offset:offset+len(body)]})
    assert all(row['fits'] for row in rows)
    assert all(row['exact_stock_prefix'] for row in rows if row['name'] in ('.tick','.list'))
    symbols={s['name']:s['value'] for s in elf.symbols()}
    assert symbols['s_lvp_loop']==0x2002d2b4 and symbols['s_current_index']==0x2002d2b8
    for name in ('.state',):
        section=next(s for s in elf.sections if s['name']==name);assert section['size']==8 and section['type']==8
    (out/'mode.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_commit':SDK_COMMIT,'upstream_path':rel,'upstream_blob':blob,'source_sha256':sha(raw),'adapted_sha256':sha(source),'header_evidence':evidence,'sections':rows,'source_admitted':False,'limits':['Unused types/stdio includes removed; private mode pointer list made const (no writes in upstream translation unit). Only initialization and tick selected; switch/get/exit excluded from this component. Mode records and callbacks remain external. Behavior and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-mode.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
