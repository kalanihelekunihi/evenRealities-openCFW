# SPDX-License-Identifier: MIT
"""Build recovered backup flash initializer on macOS; dependencies remain open."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
BINDINGS={'open_cfw_gx8002_platform_config':0x1001574c,'open_cfw_gx8002_platform_gate':0x10003be8,
'open_cfw_gx8002_request_irq':0x10004844,'open_cfw_gx8002_flash_interrupt':0x10007138,
'backup_flash_command_read':0x10006c30,'backup_flash_status_write':0x10006d34,
'open_cfw_gx8002_flash_discover':0x10007c90,'open_cfw_gx8002_flash_protection_initialize':0x10007f80,
'open_cfw_gx8002_flash_quad_enable':0x100073b4,'open_cfw_gx8002_flash_quad_enable_pair':0x10007370,
'open_cfw_gx8002_flash_device_config':0x100073f0,'open_cfw_gx8002_flash_state':0x20016d60,
'open_cfw_gx8002_flash_word_program':0x10006d90,'open_cfw_gx8002_flash_word_read':0x100074ec,
'open_cfw_gx8002_flash_interface':0x20016d80}

def build():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    out=ROOT/'build/gx8002-backup-flash-interface';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_flash_interface_initialize.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'initialize.o')],check=True)
    (out/'initialize.ld').write_text('SECTIONS { .text 0x10007d78 : { *(.text*) } }\n'+''.join(f'{k} = {v:#x};\n' for k,v in BINDINGS.items()))
    path=out/'initialize.elf';subprocess.run([pre+'ld','-T',str(out/'initialize.ld'),str(out/'initialize.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'initialize');assert next(s for s in elf.symbols() if s['name']=='open_cfw_gx8002_flash_interface_initialize')['value']==0x10007d78;sec=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(sec)
    assert not elf.relocations(sec['index']) and not any(s['name'] and s['section']==0 for s in elf.symbols())
    (out/'initialize.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':{n:sha((source.parent/n).read_bytes()) for n in ('runtime_gx8002_flash_state.h','runtime_gx8002_flash_interface_table.h')},'bindings':BINDINGS,'flags':flags,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'package_offset':0x406b8,'stock_envelope_bytes':480,'stock_sha256':sha(stock[0x406b8:0x40898]),'fits':len(payload)<=480,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded qualification required. External functions and initialized state are absolute bindings, not source closure.']}
    (ROOT/'docs/research/gx8002-backup-flash-interface-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(json.dumps(build(),indent=2))
