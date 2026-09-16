# SPDX-License-Identifier: MIT
"""Build backup IRQ enable-bank restoration for backup firmware."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    out=ROOT/'build/gx8002-backup-irq-initialize'; out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_irq_initialize.c'
    text=source.read_text()
    (out/'device.c').write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-common','-c',str(out/'device.c'),'-o',str(out/'device.o')]
    subprocess.run(command,check=True)
    script='''SECTIONS {
.irq_init 0x1000482c : { *(.text.gx_irq_init) }
}
open_cfw_gx8002_irq_saved_enable = 0x200173a0;
ASSERT(SIZEOF(.irq_init) <= 24, "IRQ initializer overflow")
'''
    (out/'device.ld').write_text(script)
    path=out/'device.elf';subprocess.run([pre+'ld','-T',str(out/'device.ld'),str(out/'device.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'device');sec=next(s for s in elf.sections if s['name']=='.irq_init');body=elf.contents(sec)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert body==stock[0x3d16c:0x3d184]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'device.disassembly.txt').write_text(asm)
    code=decode(asm);pc=0x1000482c
    sequence=[('lrw','r2, 0x200173a0',2),('lrw','r3, 0xe000e100',2),('ld.w','r1, (r2, 0x0)',2),('st.w','r1, (r3, 0x0)',2),('ld.w','r2, (r2, 0x4)',2),('st.w','r2, (r3, 0x4)',2),('rts','',2)]
    for ins in sequence:assert code[pc]==ins;pc+=ins[2]
    report={'source_sha256':sha(source.read_bytes()),'derived_source_sha256':sha(text.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_byte_exact':True,'compiled_bytes':len(body),'ordered_effects':[['read32',0x200173a0],['write32',0xe000e100],['read32',0x200173a4],['write32',0xe000e104]],'source_admitted':False,'hardware_qualified':False,'limits':['Exact stock bytes and decoded leaf access sequence restore two saved enable banks. Hardware interrupt delivery and full firmware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-irq-initialize.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(build(),indent=2))
