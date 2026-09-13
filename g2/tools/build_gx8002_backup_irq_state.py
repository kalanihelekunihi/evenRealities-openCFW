# SPDX-License-Identifier: MIT
"""Compile pinned upstream CSI interrupt state primitives for backup SRAM."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_csi_source import HEADERS
from verify_gx8002_analog_source import FLAGS


def build():
    out=ROOT/'build/gx8002-backup-irq-state';out.mkdir(exist_ok=True)
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_irq.c'
    dependencies=[]
    for name in (*HEADERS,'LICENSE'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+name],text=True).strip()
        dependencies.append({'path':name,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/name,blob))})
    command=[pre+'gcc','-Os',*FLAGS[1:]]
    for directory in ('arch/soc/grus/include','include/utility','include/utility/libc'):
        command+=['-isystem',str(sdk/directory)]
    subprocess.run([*command,'-c',str(source),'-o',str(out/'state.o')],check=True)
    (out/'state.ld').write_text('''SECTIONS {
.save 0x1000486c : { *(.text.open_cfw_gx8002_irq_save) }
.restore 0x10004878 : { *(.text.open_cfw_gx8002_irq_restore) }
/DISCARD/ : { *(.text*) }
}
''')
    subprocess.run([pre+'ld','-T',str(out/'state.ld'),str(out/'state.o'),'-o',str(out/'state.elf')],check=True)
    elf=Elf32((out/'state.elf').read_bytes(),'IRQ state');stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    alloc=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(alloc)==2
    rows=[]
    for name,offset,address,size in (('.save',0x3d1ac,0x1000486c,12),('.restore',0x3d1b8,0x10004878,8)):
        section=next(s for s in alloc if s['name']==name);payload=elf.contents(section)
        assert section['address']==address and not elf.relocations(section['index'])
        assert len(payload)<=size
        rows.append({'section_name':name,'package_offset':offset,'runtime_address':address,
                     'compiled_bytes':len(payload),'compiled_sha256':sha(payload),
                     'stock_envelope_bytes':size,'exact_stock_prefix':payload==stock[offset:offset+len(payload)]})
    (out/'state.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'state.elf')],text=True))
    result={'sdk_commit':SDK_COMMIT,'dependencies':dependencies,'source_sha256':sha(source.read_bytes()),
            'functions':rows,'source_admitted':False,'hardware_qualified':False}
    (ROOT/'docs/research/gx8002-backup-irq-state-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(build(),indent=2))
