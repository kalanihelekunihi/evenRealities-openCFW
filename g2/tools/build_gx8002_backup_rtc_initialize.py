# SPDX-License-Identifier: MIT
"""Build shared recovered RTC initialization for backup firmware."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    out=ROOT/'build/gx8002-backup-rtc-initialize'; out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_rtc_init.c'
    text=source.read_text()+'\n'+(ROOT/'components/shared/gx8002/runtime_gx8002_rtc_error.c').read_text()
    (out/'device.c').write_text(text)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    command=[pre+'gcc','-Os','-mcpu=ck804ef','-mhard-float','-ffreestanding','-fno-builtin','-ffunction-sections','-fdata-sections','-fno-shrink-wrap','-fdata-sections','-fno-common','-c',str(out/'device.c'),'-o',str(out/'device.o')]
    subprocess.run(command,check=True)
    script='''SECTIONS {
.rtc_init 0x1000881c : { *(.text.open_cfw_gx8002_rtc_init) }
.rtc_error 0x10012eb4 : { *(.rodata.open_cfw_gx8002_rtc_error) }
}
gx_rtc_init = open_cfw_gx8002_rtc_init;
gx_clock_set_module_enable = 0x10003be8;
gx_clock_get_module_frequence = 0x10003cf0;
gx_request_irq = 0x10004844;
printf_ = 0x10009934;
open_cfw_gx8002_rtc_isr = 0x100087dc;
open_cfw_gx8002_rtc_start_tick = 0x10008800;
ASSERT(SIZEOF(.rtc_init) <= 76, "RTC initializer overflow")
ASSERT(SIZEOF(.rtc_error) <= 24, "RTC error overflow")
'''
    (out/'device.ld').write_text(script)
    path=out/'device.elf';subprocess.run([pre+'ld','-T',str(out/'device.ld'),str(out/'device.o'),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'device');sec=next(s for s in elf.sections if s['name']=='.rtc_init');body=elf.contents(sec)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert len(body)<=76
    error=next(s for s in elf.sections if s['name']=='.rtc_error')
    assert elf.contents(error)==stock[0x4b7f4:0x4b7f4+error['size']]
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    asm=subprocess.check_output([pre+'objdump','-d',str(path)],text=True);(out/'device.disassembly.txt').write_text(asm)
    report={'source_sha256':sha(source.read_bytes()),'derived_source_sha256':sha(text.encode()),'command':command,'elf_sha256':sha(path.read_bytes()),'stock_byte_exact':body==stock[0x4115c:0x4115c+len(body)],'compiled_bytes':len(body),'source_admitted':False,'hardware_qualified':False,'limits':['Shared recovered C and diagnostic string. Backup initialization differs in inlining from stock; decoded behavior comparison and composition remain pending. This build is not source admission or hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-rtc-initialize.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(json.dumps(build(),indent=2))
