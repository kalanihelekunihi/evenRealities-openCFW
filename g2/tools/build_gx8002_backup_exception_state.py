# SPDX-License-Identifier: MIT
"""Compile recovered exception-frame and original BSS storage layout on macOS."""
import json,struct,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS


def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert struct.unpack_from('<I',stock,0x3ba88)[0]==0x20017090
    assert struct.unpack_from('<II',stock,0x3bb84)==(0x20017390,0x20017390)
    out=ROOT/'build/gx8002-backup-exception-state';out.mkdir(exist_ok=True)
    src=ROOT/'components/shared/gx8002/runtime_gx8002_backup_exception_state.c'
    header=src.parent/'backup_exception_state.h'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    obj=out/'state.o';cmd=[pre+'gcc',*FLAGS,'-c',str(src),'-o',str(obj)]
    subprocess.run(cmd,check=True)
    ld=out/'state.ld';ld.write_text('SECTIONS { .stack 0x20017090 (NOLOAD) : { *(.bss.backup_exception_stack) } .saved_sp 0x20017390 (NOLOAD) : { *(.bss.backup_interrupted_sp) } }\n')
    path=out/'state.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'exception state');allocated=[s for s in elf.sections if s['flags']&2 and s['size']]
    assert [(s['address'],s['size'],s['type']) for s in allocated]==[(0x20017090,768,8),(0x20017390,4,8)]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    result={'stock_sha256':IMAGE_SHA,'entry_bytes_sha256':sha(stock[0x3bb40:0x3bb8c]),'source_sha256':sha(src.read_bytes()),'header_sha256':sha(header.read_bytes()),'command':cmd,'elf_sha256':sha(path.read_bytes()),'frame_bytes':72,'stack_bytes':768,'saved_sp_bytes':4,'source_admitted':False,'limits':['Frame offsets and original BSS layout reconstructed; 768-byte capacity follows the BSS lower bound and entry stack top, not a proven maximum stack usage.','No exception entry/return implementation or memory relocation. Nested exceptions, handler stack consumption and other references remain to be reconstructed.']}
    (ROOT/'docs/research/gx8002-backup-exception-state.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(build()['elf_sha256'])
