# SPDX-License-Identifier: MIT
"""Compile upstream idle mode callbacks, record and diagnostic strings."""
import json,subprocess
from build_gx8002_backup_mode import build as mode_build,ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    evidence=mode_build();out=ROOT/'build/gx8002-backup-idle-mode';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='lvp/lvp_mode_idle.c'
    blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();raw=authenticated_blob(sdk/rel,blob)
    source=raw.decode().replace('#include <stdio.h>','extern int printf(const char *, ...);').replace('#include <types.h>','').replace('#include <board_config.h>','')
    for kind in ('Init','Exit'):
        literal='LOG_TAG"'+kind+' IDLE mode\\n"';symbol='idle_'+kind.lower()+'_message'
        source=source.replace('printf('+literal+')','printf('+symbol+')')
        source=source.replace('//=================================================================================================',f'static const char {symbol}[] __attribute__((section(".message.{kind.lower()}"))) = {literal};\n//=================================================================================================',1)
    (out/'idle.c').write_text(source);(out/'lvp_mode.h').write_bytes((ROOT/'build/gx8002-backup-mode/lvp_mode.h').read_bytes());(out/'autoconf.h').write_text('')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-fno-builtin','-ffunction-sections','-fdata-sections','-I',str(out),'-c',str(out/'idle.c'),'-o',str(out/'idle.o')],check=True)
    placements=[('.idle_tick',0x1000b7c0,'.text._IdleModeTick',4),('.idle_buffer',0x1000b7c4,'.text._IdleModeBufferInit',4),('.idle_done',0x1000b7c8,'.text._IdleModeDone',16),('.idle_init',0x1000b7d8,'.text._IdleModeInit',16),('.idle_record',0x1001366c,'.rodata.lvp_idle_mode_info',20),('.idle_exit_message',0x10013680,'.message.exit',24),('.idle_init_message',0x10013698,'.message.init',24)]
    ld='SECTIONS {\n'+''.join(f'{name} {addr:#x} : {{ *({section}) }}\n' for name,addr,section,limit in placements)+'}\nprintf = 0x10009934;\n'
    (out/'idle.ld').write_text(ld);path=out/'idle.elf';subprocess.run([pre+'ld','-T',str(out/'idle.ld'),str(out/'idle.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'idle');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for name,addr,section,limit in placements:
        sec=next(s for s in elf.sections if s['name']==name);body=elf.contents(sec);offset=addr-0x10000000+0x38940
        assert len(body)<=limit and body==stock[offset:offset+len(body)]
        rows.append({'name':name,'bytes':len(body),'envelope_bytes':limit,'exact_stock_prefix':True})
    assert {s['name'] for s in elf.sections if s['flags']&2 and s['size']}=={p[0] for p in placements}
    report={'upstream_commit':SDK_COMMIT,'path':rel,'blob':blob,'source_sha256':sha(raw),'adapted_sha256':sha(source.encode()),'mode_evidence':evidence,'sections':rows,'source_admitted':False,'limits':['Printf remains external. Unused includes removed and printf prototype supplied; original string literals assigned named sections for placement. Authentic idle callbacks, not placeholders for denoise. Integration and hardware qualification pending.']}
    (ROOT/'docs/research/gx8002-backup-idle-mode.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
