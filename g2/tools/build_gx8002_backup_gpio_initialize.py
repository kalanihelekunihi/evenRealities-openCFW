# SPDX-License-Identifier: MIT
"""Build shared recovered GPIO initialization for backup firmware."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    out=ROOT/'build/gx8002-backup-gpio-initialize'; out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_gpio_initialize.c'
    text=source.read_text()
    (out/'device.c').write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-common','-c',str(out/'device.c'),'-o',str(out/'device.o')]
    subprocess.run(command,check=True)
    script='''SECTIONS {
.gpio_init 0x100081ec : { *(.text.open_cfw_gx8002_gpio_initialize) }
}
gx_gpio_init = open_cfw_gx8002_gpio_initialize;
open_cfw_gx8002_platform_gate = 0x10003be8;
ASSERT(SIZEOF(.gpio_init) <= 24, "GPIO initializer overflow")
'''
    (out/'device.ld').write_text(script)
    path=out/'device.elf';subprocess.run([pre+'ld','-T',str(out/'device.ld'),str(out/'device.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'device');sec=next(s for s in elf.sections if s['name']=='.gpio_init');body=elf.contents(sec)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert body==stock[0x40b2c:0x40b44]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'device.disassembly.txt').write_text(asm)
    code=decode(asm);pc=0x100081ec
    sequence=[('push','r15',2),('movi','r1, 1',2),('movi','r0, 4',2),('bsr','0x10003be8',4),('movi','r3, 32773',4),('rotli','r3, r3, 29',4),('movi','r0, 0',2),('st.w','r0, (r3, 0x34)',2),('pop','r15',2)]
    for instruction in sequence:
        assert code[pc]==instruction;pc+=instruction[2]
    report={'source_sha256':sha(source.read_bytes()),'derived_source_sha256':sha(text.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_byte_exact':True,'compiled_bytes':len(body),'ordered_effects':[['platform_gate',4,1],['write32',0xa0001034,0]],'source_admitted':False,'hardware_qualified':False,'limits':['Shared recovered C enables module 4 before clearing the GPIO control register. Exact stock bytes and decoded call/store ordering qualify this component only; gate internals and electrical behavior require separate evidence.']}
    (ROOT/'docs/research/gx8002-backup-gpio-initialize.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(build(),indent=2))
