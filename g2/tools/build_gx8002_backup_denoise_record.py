# SPDX-License-Identifier: MIT
"""Compile reconstructed denoise dispatch record and wrappers; no binary input code."""
import json,subprocess
from build_gx8002_backup_mode import build as mode_build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32


def build():
    evidence=mode_build();out=ROOT/'build/gx8002-backup-denoise-record';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_denoise_record.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-fno-builtin','-ffunction-sections','-fdata-sections','-I',str(ROOT/'build/gx8002-backup-mode'),'-c',str(source),'-o',str(out/'denoise.o')],check=True)
    placements=[('.denoise_done',0x1000b7e8,'.text.denoise_done',16),('.denoise_buffer',0x1000b7f8,'.text.denoise_buffer_init',8),('.denoise_record',0x100136b0,'.rodata.lvp_denoise_mode_info',20),('.denoise_message',0x100136c4,'.denoise_message',40)]
    ld='SECTIONS {\n'+''.join(f'{name} {addr:#x} : {{ *({section}) }}\n' for name,addr,section,limit in placements)+'}\nprintf = 0x10009934;\nopen_cfw_gx8002_backup_context_initialize = 0x10009d7c;\nopen_cfw_gx8002_backup_denoise_init = 0x1000bc44;\nopen_cfw_gx8002_backup_denoise_tick = 0x1000b958;\n'
    (out/'denoise.ld').write_text(ld);path=out/'denoise.elf';subprocess.run([pre+'ld','-T',str(out/'denoise.ld'),str(out/'denoise.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'denoise');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for name,addr,section,limit in placements:
        sec=next(s for s in elf.sections if s['name']==name);body=elf.contents(sec);offset=addr-0x10000000+0x38940
        assert len(body)<=limit and body==stock[offset:offset+len(body)]
        rows.append({'name':name,'bytes':len(body),'stock_prefix_exact':True})
    assert {s['name'] for s in elf.sections if s['flags']&2 and s['size']}=={p[0] for p in placements}
    report={'source_sha256':sha(source.read_bytes()),'header_evidence':evidence,'sections':rows,'source_admitted':False,'limits':['Denoise init/tick, context initialization and printf remain external. Record and complete done/buffer callbacks only; full denoise functionality is not yet source-closed.']}
    (ROOT/'docs/research/gx8002-backup-denoise-record.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['sections'])
