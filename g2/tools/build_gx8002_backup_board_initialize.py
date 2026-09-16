# SPDX-License-Identifier: MIT
"""Link complete recovered board wrapper and existing source helpers."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT, FLAGS, IMAGE, IMAGE_SHA, sha, Elf32


def build():
    out=ROOT/'build/gx8002-backup-board-initialize';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');objects=[];sources=[]
    for name in ('backup_board_initialize','backup_status','analog_config_update_enable'):
        src=ROOT/f'components/shared/gx8002/runtime_gx8002_{name}.c';obj=out/(name+'.o')
        subprocess.run([pre+'gcc',*FLAGS,'-Os','-c',str(src),'-o',str(obj)],check=True)
        objects.append(str(obj));sources.append({'path':str(src),'sha256':sha(src.read_bytes())})
    specs=[('board',0x3be14,12,'open_cfw_gx8002_backup_board_initialize'),('status',0x3c8f8,68,'open_cfw_gx8002_backup_status'),('analog',0x3db18,20,'open_cfw_gx8002_analog_config_update_enable')]
    ld=out/'board.ld';ld.write_text('SECTIONS {\n'+''.join(f'.{name} {off-0x3b940+0x10003000:#x} : {{ *(.text.{symbol}) }}\n' for name,off,n,symbol in specs)+'}\n')
    path=out/'board.elf';subprocess.run([pre+'ld','-T',str(ld),*objects,'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'board');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    rows=[]
    for name,off,limit,symbol in specs:
        sec=next(s for s in elf.sections if s['name']=='.'+name);body=elf.contents(sec)
        rows.append({'section':name,'package_offset':off,'bytes':len(body),'envelope':limit,'fits':len(body)<=limit,'stock_identical':body==stock[off:off+len(body)]})
    (out/'board.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    return {'sources':sources,'elf_sha256':sha(path.read_bytes()),'sections':rows,'source_admitted':False,'limits':['Complete source wrapper and both helper bodies linked at backup bindings. Behavioral comparison and incoming references remain pending; no firmware integration or hardware qualification.']}


if __name__=='__main__':
    r=build();(ROOT/'docs/research/gx8002-backup-board-initialize.json').write_text(json.dumps(r,indent=2)+'\n');print(r['sections'])
