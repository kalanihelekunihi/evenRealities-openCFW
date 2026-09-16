# SPDX-License-Identifier: MIT
"""Build recovered backup context initialization with authenticated layout."""
import json,subprocess
from build_gx8002_buffer_initialize import build as authenticate,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS


def build():
    evidence=authenticate();out=ROOT/'build/gx8002-backup-context-initialize';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_context_initialize.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'gcc','-Os',*FLAGS[1:],'-I',str(ROOT/'build/upstream-nationalchip-lvp-kws/include'),'-c',str(source),'-o',str(out/'context.o')],check=True)
    (out/'context.ld').write_text('SECTIONS { .context_init 0x10009d7c : { *(.text*) } }\nmemset = 0x100113c4;\nbackup_context_header = 0x20017700;\nbackup_context_frames = 0x20017780;\nbackup_output_samples = 0x2001a380;\nbackup_microphone_samples = 0x20030000;\n')
    path=out/'context.elf';subprocess.run([pre+'ld','-T',str(out/'context.ld'),str(out/'context.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'context');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    sections=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(sections)==1
    body=elf.contents(sections[0]);assert len(body)<=156
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    (out/'context.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'upstream_evidence':evidence,'source_sha256':sha(source.read_bytes()),'storage_header_sha256':sha((source.parent/'runtime_gx8002_backup_context_storage.h').read_bytes()),'bytes':len(body),'envelope_bytes':156,'exact_stock_prefix':body==stock[0x426bc:0x426bc+len(body)],'source_admitted':False,'limits':['Two memset calls remain bound to backup implementation. Recovered complete field assignments; behavior, BSS ownership and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-context-initialize.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(build()['bytes'])
