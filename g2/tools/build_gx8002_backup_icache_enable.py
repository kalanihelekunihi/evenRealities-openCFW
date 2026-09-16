# SPDX-License-Identifier: MIT
"""Build shared recovered instruction-cache enable for backup firmware."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    out=ROOT/'build/gx8002-backup-icache-enable'; out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_icache_enable.c'
    text=source.read_text()
    (out/'device.c').write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-common','-c',str(out/'device.c'),'-o',str(out/'device.o')]
    subprocess.run(command,check=True)
    script='''SECTIONS {
.icache_enable 0x10004fac : { *(.text.gx_icache_enable) }
}
ASSERT(SIZEOF(.icache_enable) <= 32, "instruction-cache enable overflow")
'''
    (out/'device.ld').write_text(script)
    path=out/'device.elf';subprocess.run([pre+'ld','-T',str(out/'device.ld'),str(out/'device.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'device');sec=next(s for s in elf.sections if s['name']=='.icache_enable');body=elf.contents(sec)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert len(body)<=32
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'device.disassembly.txt').write_text(asm)
    report={'source_sha256':sha(source.read_bytes()),'derived_source_sha256':sha(text.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_byte_exact':body==stock[0x3d8ec:0x3d8ec+len(body)],'compiled_bytes':len(body),'source_admitted':False,'hardware_qualified':False,'limits':['Shared recovered C retains the external-controller ready poll without timeout. Decoded control/status trace comparison is separate; hardware cache behavior remains unqualified.']}
    (ROOT/'docs/research/gx8002-backup-icache-enable.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(build(),indent=2))
