# SPDX-License-Identifier: MIT
"""Build recovered backup status-register write helper on macOS."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_flash_command_read':0x10006c30,'open_cfw_gx8002_flash_command_write':0x10006cb0}

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-flash-status-write';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_flash_status_write.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os','-fno-tree-switch-conversion','-fno-shrink-wrap','-fno-move-loop-invariants',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'initialize.o')],check=True)
    (out/'initialize.ld').write_text('SECTIONS { .text 0x10006d34 : { *(.text*) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    path=out/'initialize.elf';subprocess.run([pre+'ld','-T',str(out/'initialize.ld'),str(out/'initialize.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'initialize');assert next(s for s in elf.symbols() if s['name']=='backup_flash_status_write')['value']==0x10006d34;sec=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(sec)
    assert all(s['name']=='.text' for s in elf.sections if s['flags']&2 and s['size'])
    assert not elf.relocations(sec['index']) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    (out/'initialize.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'bindings':BINDINGS,'flags':flags,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':0x3f674,'stock_envelope_bytes':92,'stock_sha256':sha(stock[0x3f674:0x3f6d0]),'fits':len(payload)<=92,'source_admitted':False,'hardware_qualified':False,'limits':['Standalone transport bindings require source resolution; see the separate decoded verifier. Physical flash behavior remains unqualified.']}
    (ROOT/'docs/research/gx8002-backup-flash-status-write-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
