# SPDX-License-Identifier: MIT
"""Build shared recovered RTC interrupt handler and state for backup firmware."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    out=ROOT/'build/gx8002-backup-rtc-isr'; out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_rtc_isr.c'
    text=source.read_text()+'\nvolatile struct rtc_callback_state open_cfw_gx8002_rtc_callback_state;\n'
    (out/'device.c').write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-common','-c',str(out/'device.c'),'-o',str(out/'device.o')]
    subprocess.run(command,check=True)
    script='''SECTIONS {
.rtc_isr 0x100087dc : { *(.text.open_cfw_gx8002_rtc_isr) }
.rtc_callback 0x200176d0 (NOLOAD) : { *(.bss.open_cfw_gx8002_rtc_callback_state) }
}

ASSERT(SIZEOF(.rtc_isr) <= 36, "device initializer overflow")
ASSERT(SIZEOF(.rtc_callback) == 8, "device heads ABI")
'''
    (out/'device.ld').write_text(script)
    path=out/'device.elf';subprocess.run([pre+'ld','-T',str(out/'device.ld'),str(out/'device.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'device');sec=next(s for s in elf.sections if s['name']=='.rtc_isr');body=elf.contents(sec)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert len(body)<=36
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    state=next(s for s in elf.sections if s['name']=='.rtc_callback')
    assert state['type']==8 and 0x20017090<=state['address'] and state['address']+state['size']<=0x2002d79c
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'device.disassembly.txt').write_text(asm)
    report={'source_sha256':sha(source.read_bytes()),'derived_source_sha256':sha(text.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_byte_exact':body==stock[0x4111c:0x4111c+len(body)],'compiled_bytes':len(body),'state_bytes':8,'source_admitted':False,'hardware_qualified':False,'limits':['Shared recovered RTC handler and source BSS callback state. Decoded callback and acknowledgement comparison is provided separately; full firmware and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-rtc-isr.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(build(),indent=2))
